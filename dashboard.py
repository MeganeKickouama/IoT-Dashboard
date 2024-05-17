import dash.dependencies
import dash_daq as daq
from dash import html, Input, Output, dcc, Dash, State
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeChangerAIO
import RPi.GPIO as GPIO
import Freenove_DHT as DHT
import paho.mqtt.client as mqtt
import time
import smtplib
import imaplib
import easyimap as imap
import email
import datetime
import logging
import sqlite3
from bluepy.btle import Scanner


# BOARD: https://www.electronicayciencia.com/assets/2016/11/conexion-gpio-de-raspberry-pi-3/img/pi_board_pinout.jpg

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

ledPin = 40
GPIO.setup(ledPin, GPIO.OUT)

DHTPin = 11 #define the pin of DHT11

# Initialize GPIO pin for DHT sensor
GPIO.setup(DHTPin, GPIO.OUT)

# Create DHT object after GPIO pin setup
dht = DHT.DHT(DHTPin)

# Read DHT sensor data
dht.readDHT11()

Motor1 = 35 # Enable Pin
Motor2 = 13 # Input Pin
Motor3 = 15 # Input Pin

GPIO.setup(Motor1,GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(Motor2,GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(Motor3,GPIO.OUT, initial=GPIO.LOW)

logging.basicConfig(level=logging.INFO)
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.themes.SANDSTONE])
img = html.Img(src=app.get_asset_url('lightbulb_off.png'),width='100px', height='100px')
humidityValue = 0
temperatureValue = 0
emailSent = False

# Global threshold values with the default values.
global light_threshold, temperature_threshold, humidity_threshold
light_threshold = 400  # Default value, update as needed
temperature_threshold = 24  # Default value, update as needed
humidity_threshold = 50  # Default value, update as needed
profile_name = "Unknown"

class User:
    def __init__(self, profile_name, rfid, temp_threshold, humidity_threshold, light_intensity):
        self.profile_name = profile_name
        self.rfid = rfid
        self.temp_threshold = temp_threshold
        self.humidity_threshold = humidity_threshold
        self.light_intensity = light_intensity
    
instance_user = User(profile_name, "XX XX XX XX", temperature_threshold, humidity_threshold, light_threshold) # for testing 


# Global variables for email flags
temperatureEmailSent = False
lightEmailSent = False

source_address = 'else6541@gmail.com'
dest_address = 'peterfishman01@gmail.com'
# dest_address = 'em.kouama@gmail.com'
# dest_address = 'yasselyamani@ gmail.com'
password = 'zcmf lmlv lcfu igqi'
imap_srv = 'imap.gmail.com'
imap_port = 993

# MQTT Setup
MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883
MQTT_TOPIC = "IoTLabPhase4/#"
light_level = None  # Variable to store the light level

# Path to SQL script and database
#sql_file_path = '/home/georgea/Desktop/IoT-Dashboard/profile.sql'
#db_path = '/home/georgea/Desktop/IoT-Dashboard/profile.db'
sql_file_path = 'profile.sql'
db_path = 'profile.db'

def execute_sql_script(file_path, db_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Open and read the SQL file
    with open(file_path, 'r') as sql_file:
        sql_script = sql_file.read()

    # Execute the SQL script
    cursor.executescript(sql_script)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    
execute_sql_script(sql_file_path, db_path)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    global light_level
    global profile_name
    global temperature_threshold, humidity_threshold, light_threshold, temperatureEmailSent
    
    message = msg.payload.decode()
    topic = msg.topic

    if topic == "IoTLabPhase4/Light":
        try:
            # Assuming the message format is "Light level: <number>"
            light_level = int(message.split(': ')[1])
            print(f"Received message '{light_level}' on topic '{msg.topic}'")
        except (ValueError, IndexError) as e:
            print(f"Error processing light level message: {e}")

    elif topic == "IoTLabPhase4/RFID":
        if "Hex:" in message:
            hex_tag = message.split('Hex: ')[1].strip()
            profile = get_profile_by_rfid(hex_tag)
            if profile:
                # Unpack the profile information
                profile_name, temperature_limit, humidity_limit, light_limit = profile

                # Check if the temperature threshold has changed
                if temperature_limit != temperature_threshold:
                    temperature_threshold = temperature_limit  # Update the global threshold
                    temperatureEmailSent = False  # Reset the email sent flag
                    print(f"Updated temperature threshold for {profile_name} to {temperature_threshold}°C")
                    send_email(f"{profile_name} has just logged into the greatest dashboard ever!",
                               "Hello {profile_name}, you've entered the mainframe and your settings are updated.")
                if light_limit != light_threshold:
                    light_threshold = light_limit
                    print(f"Updated light threshold for {profile_name} to {light_threshold}")

            
                print(f"RFID Tag {hex_tag} belongs to {profile_name} with thresholds - Temp: {temperature_limit}, Hum: {humidity_limit}, Light: {light_limit}")
            else:
                profile_name = "Unknown"
                print(f"RFID Tag {hex_tag} not found in database")
                
        


def get_profile_by_rfid(rfid):
    conn = sqlite3.connect('profile.db')
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Name, Temperature_Limit, Humidity_Limit, Light_Limit FROM profile WHERE RFID = ?", (rfid,))
        return cursor.fetchone()
    finally:
        conn.close()



# Setup MQTT Client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()

# profile button setup
profile_icon = html.I(className="bi bi-person-circle", style=dict(display="inline-block"))
btn_text = html.Div('User Profile', style=dict(paddingRight="0.5vw", display="inline-block"))
btn_content = html.Span([profile_icon, btn_text])

# Body components
profile = html.Div(
    [
        dbc.Button(
            children=btn_content,
            n_clicks=0,
            size="lg",
            style=dict(fontSize="1.7vh", backgroundColor="#007bC4", textAlign="center"),
            id="open-offcanvas"
        ),
        dbc.Offcanvas(
            children=[
                html.Div(
                    children=[
                        html.H5(
                            children=[
                                html.Strong("User Name"),
                                #html.Div(f"{instance_user.profile_name}", id="profile-name-display"),
                                html.Div(id='profile-name-display', children="Scan an RFID to see user details", style={'color': 'grey', 'fontSize': 20}),
                            ]
                        ), 
                        html.H5(
                            children=[
                                html.Strong("Temperature Threshold"),
                                #html.P(f"{instance_user.temp_threshold}"),
                                html.Div(id='profile-temperature-display', style={'color': 'grey', 'fontSize': 20}),
                            ]
                        ),
                        html.H5(
                            children=[
                                html.Strong("Humidity Threshold"),
                                #html.P(f"{instance_user.humidity_threshold}"),
                                html.Div(id='profile-humidity-display', style={'color': 'grey', 'fontSize': 20}),
                            ]
                        ),
                        html.H5(
                            children=[
                                html.Strong("Light Intensity Threshold"),
                                #html.P(f"{instance_user.light_intensity}"),
                                html.Div(id='profile-light-display', style={'color': 'grey', 'fontSize': 20})
                            ]
                        ),
                        
                    ]
                ),
            ],
            id="offcanvas",
            title="User Dashboard,",
            is_open=False,
        ),
    ]
)

# Navbar
navbar = dbc.NavbarSimple(
    children = [profile],
    brand="Welcome to IoT Dashboard",
    brand_href="#",
    color="black",
    dark=True,
    className="mb-5",
)

# Bluetooth notifications
BL_notification = html.Div(
    id='bluetooth',
    children=[
        dbc.Button('Find Nearby Bluetooth Devices', id='BL_button', color='primary', class_name='mr-2'),
        html.Div([
            
            html.Img(src=app.get_asset_url('bluetooth'),width='60px', height='60px', style={'padding': '10px'}),
            dbc.Row([
                dbc.Col(html.H5('Bluetooth Devices Nearby'), width=3, lg=1),
                dbc.Col(html.H5('', id='bluetooth_count'), width=1, lg=1)
            ], justify="around"),
            
            dbc.Row([
                dbc.Col(html.H5('RSSI Threshold'), width=3, lg=1),
                dbc.Col(html.H5('-50', id='rssi_threshold'), width=1, lg=1)
            ], justify="around")
        ]),  
    ],
    style={'text-align': 'center'}
)

# Body components
ledBox = html.Div([
    html.H3('LED Control'),
    html.Img(id='led-image', src=app.get_asset_url('lightbulb_off.png'), style={'width': '100px', 'height': '100px'}),
    html.P(id='light-level-text', children="Waiting for light level data..."),
    html.P(id='email-sent-confirmation', children='', style={'color': 'green'})
], style={'text-align': 'center'})

fanControl = html.Div([
    html.H3('Fan'),
    html.Img(src=app.get_asset_url("fan.png"), style={'width': '100px', 'height': '100px','padding': '10px'}),
    daq.ToggleSwitch(id='fan-toggle', value=False, labelPosition="bottom")
], style={'text-align': 'center'})

temperatureGauge = html.Div([
    html.H3('Temperature'),
    daq.Thermometer(id='temperature-thermometer', min=0, max=100, value=20, showCurrentValue=True, label="Degrees C")
], style={'text-align': 'center'})

humidityGauge = html.Div([
    html.H3('Humidity'),
    daq.Gauge(id='humidity-gauge', min=0, max=100, value=50, showCurrentValue=True, label="Percent")
], style={'text-align': 'center'})

# New component for displaying RFID scanned name
'''
rfidNameDisplay = html.Div([
    html.H3('User Profile'),
    html.Div(id='profile-name-display', children="Scan an RFID to see user details", style={'color': 'blue', 'fontSize': 24}),
    html.Div(id='profile-temperature-display', style={'color': 'blue'}),
    html.Div(id='profile-humidity-display', style={'color': 'blue'}),
    html.Div(id='profile-light-display', style={'color': 'blue'})
    ], style={'text-align': 'center', 'margin-top': '20px'})
'''

# Footer definition
footer = html.Footer([
    dbc.Container("Team Members: Yassine El Yamani, Megane Kickouama, Peter Fishman, Ilan Trutner", className="text-white", style={"textAlign": "center"})
], className="bg-black py-3", style={"position": "fixed", "left": 0, "bottom": 0, "width": "100%"})

# Interval component for triggering periodic callbacks
interval_component = dcc.Interval(id='interval-component', interval=3500, n_intervals=0)

# App layout assembly
'''
app.layout = html.Div([
    navbar,
    dbc.Container([
        dbc.Row([
            dbc.Col(ledBox, width=6, lg=3),
            dbc.Col(fanControl, width=6, lg=3),
            dbc.Col(temperatureGauge, width=6, lg=3),
            dbc.Col(humidityGauge, width=6, lg=3),
            dbc.Col(rfidNameDisplay, width=12)  # Full width for RFID name display
        ], justify="around", className="mb-4"),
    ], fluid=True, style={"padding": "20px"}),
    interval_component,
    footer
], style={"backgroundColor": "white"})
'''

app.layout = html.Div([
    navbar,
    dbc.Container([
        dbc.Row([
            dbc.Col(ledBox, width=6, lg=3),
            dbc.Col(fanControl, width=6, lg=3),
            dbc.Col(html.Div(children=[]), width=6, lg=3),
        ], justify="around", className="mb-4"),
        dbc.Row([
            dbc.Col(temperatureGauge, width=6, lg=3),
            dbc.Col(humidityGauge, width=6, lg=3),
            dbc.Col(BL_notification, width=6, lg=3),
        ], justify="around"),
    ], fluid=True, style={"padding": "20px"}),
    dcc.Store(id='fan-state-store', data={'fan_on': False}),
    interval_component,
    footer
], style={"backgroundColor": "white"})

'''@app.callback(
    Output('led-image', 'src'),
    Input('interval-component', 'n_intervals')
)
def update_led_image(n):
    if light_level is not None:
        if light_level < 400:
            GPIO.output(40, GPIO.HIGH)
            return app.get_asset_url('lightbulb_on.png')
        else:
            GPIO.output(40, GPIO.LOW)
            return app.get_asset_url('lightbulb_off.png')
    return app.get_asset_url('lightbulb_off.png')'''

@app.callback(
    [Output('profile-name-display', 'children'),
     Output('profile-temperature-display', 'children'),
     Output('profile-humidity-display', 'children'),
     Output('profile-light-display', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_profile_display(n):
    global profile_name, temperature_threshold, humidity_threshold, light_threshold
    return [
        f"{profile_name}",
        f"{temperature_threshold}°C",
        f"{humidity_threshold}%",
        f"{light_threshold}"
    ]

def send_email(subject, body):
    smtp_srv = 'smtp.gmail.com'
    smtp_port = 587
    smtp_user = source_address
    smtp_pass = password

    msg = 'Subject: {}\n\n{}'.format(subject, body)
    server = smtplib.SMTP(smtp_srv, smtp_port)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(smtp_user, smtp_pass)
    server.sendmail(smtp_user, dest_address, msg)
    server.quit()

def receive_email():
    #global emailReceived
    mail = imaplib.IMAP4_SSL(imap_srv)
    mail.login(source_address, password)
    mail.select('inbox')
    status, data = mail.search(None,
    'UNSEEN',
    'HEADER SUBJECT "Temperature is High"',
    'HEADER FROM "' + dest_address +  '"')

    mail_ids = []
    for block in data:
        mail_ids += block.split()
    for i in mail_ids:
        status, data = mail.fetch(i, '(RFC822)')
        for response_part in data:
            if isinstance(response_part, tuple):
                message = email.message_from_bytes(response_part[1])
                mail_from = message['from']
                mail_subject = message['subject']
                if message.is_multipart():
                    mail_content = ''
                    for part in message.get_payload():
                        if part.get_content_type() == 'text/plain':
                            mail_content += part.get_payload()
                else:
                    mail_content = message.get_payload().lower()
                return "yes" in mail_content.lower()

                if 'yes' in mail_content:

                    return True
                elif 'no' in mail_content:
                    emailReceived = False
                    return True
                else:
                    return False

#Old Button Click (Reconfigure dashboard to add it back as a button).
'''@app.callback(Output('led-image', 'children'),
              Input('led-image', 'n_clicks')
                )
def update_output(n_clicks):
    if n_clicks % 2 == 1:
        GPIO.output(ledPin, GPIO.HIGH)
        img = html.Img(src=app.get_asset_url('lightbulb_on.png'), width='100px', height='100px')
        return img
    else:
        GPIO.output(ledPin, GPIO.LOW)
        img = html.Img(src=app.get_asset_url('lightbulb_off.png'),width='100px', height='100px')
        return img'''

def main():
    app.run_server(debug=True)


@app.callback(Output('fan-toggle', 'value'),
              Input('fan-toggle', 'value')
)
def toggle_fan(value):
    if value:
        GPIO.output(Motor1, GPIO.HIGH)
        value = True
    else:
         GPIO.output(Motor1, GPIO.LOW)
         value = False
    return value


# Bluetooth Logic
@app.callback(
    Output("bluetooth_count", "children"),
    [Input("BL_button", "n_clicks")]
)

def update_bluetooth(n_clicks):
    if n_clicks is None:
        return "0"
    else:
        disabled = True # disable the button until the function is finished
        scanner = Scanner()
        devices = scanner.scan(10.0)
        device_list = []
        for device in devices:
            if device.rssi > -50: # and device.connectable == True:
                device_list.append(device.addr)
        disabled = False
        return f"{len(device_list)}"

#canvas logic
@app.callback(
    Output("offcanvas", "is_open"),
    Input("open-offcanvas", "n_clicks"),
    [State("offcanvas", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open

# Callbacks for light level and email
'''@app.callback(
    [Output('email-sent-confirmation', 'children'),
     Output('light-level-text', 'children')],
    Input('interval-component', 'n_intervals')
)
def update_light_level_and_email(n):
    global emailSent
    confirmation_message = ''
    if light_level is not None:
        current_time = datetime.datetime.now().strftime("%H:%M")
        if light_level < 400 and not emailSent:
            send_email("The light is ON", f"The light is ON at {current_time} time!")
            emailSent = True
            confirmation_message = "Email has been sent!"
        elif light_level >= 400:
            emailSent = False  # Reset the email sent flag when condition is no longer met

        light_level_display = f"Current light level: {light_level}"
    else:
        light_level_display = "Waiting for light level data..."
    return confirmation_message, light_level_display'''

@app.callback(
    [Output('email-sent-confirmation', 'children'),
     Output('light-level-text', 'children'),
     Output('led-image', 'src')],
    Input('interval-component', 'n_intervals')
)
def update_light_level_and_email(_):
    global lightEmailSent, light_level, light_threshold
    email_message = ""
    if light_level is not None:
        src = "/assets/lightbulb_on.png" if light_level < light_threshold else "/assets/lightbulb_off.png"
        GPIO.output(40, GPIO.HIGH if light_level < light_threshold else GPIO.LOW)
        light_level_display = f"Current light level: {light_level}"
        if light_level < light_threshold and not lightEmailSent:
            send_email("The light is ON", f"The light is ON at {datetime.datetime.now().strftime('%H:%M')} time!")
            lightEmailSent = True
            email_message = "Email has been sent!"
        elif light_level >= light_threshold:
            lightEmailSent = False  # Reset the flag when condition is no longer met
    else:
        light_level_display = "Waiting for light level data..."
        src = "/assets/lightbulb_off.png"

    return email_message, light_level_display, src


@app.callback(
    Output('humidity-gauge', 'value'),
    Output('temperature-thermometer', 'value'),
    Input('interval-component', 'n_intervals')
)
def update_sensor(_):
    global temperatureEmailSent, temperatureValue, temperature_threshold
    dht.readDHT11()
    temperatureValue = dht.temperature
    humidityValue = dht.humidity

    # Check and respond to temperature readings
    if temperatureValue > temperature_threshold and not temperatureEmailSent:
        send_email("Temperature is High", "Would you like to start the fan?")
        temperatureEmailSent = True
    elif receive_email():
        toggle_fan(True)
        # Optional: add a delay or a way to turn off the fan automatically after a certain condition
        time.sleep(5)  # This sleep will block the callback, consider asynchronous handling
        toggle_fan(False)
    elif temperatureValue < temperature_threshold - 2:  # A tolerance or hysteresis can be added here
        toggle_fan(False)
        temperatureEmailSent = False  # Reset the flag when the temperature goes below the threshold


    print(f"Temperature: {temperatureValue}, Humidity: {humidityValue}")
    return humidityValue, temperatureValue

main()
