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

conn = sqlite3.connect('profile.db')


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

cursor = mydb.cursor()

logging.basicConfig(level=logging.INFO)
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
img = html.Img(src=app.get_asset_url('lightbulb_off.png'),width='100px', height='100px')
humidityValue = 0
temperatureValue = 0
emailSent = False

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
MQTT_TOPIC = "IoTLabPhase3/Peter"
light_level = None  # Variable to store the light level

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    global light_level
    try:
        # Decode the message payload
        message = msg.payload.decode()
        # Assuming the message format is "Light level: <number>"
        # Split the message string and convert the second part (index 1) to integer
        light_level = int(message.split(': ')[1])
        print(f"Received message '{light_level}' on topic '{msg.topic}'")
    except ValueError as e:
        print(f"Error converting MQTT message to integer: {e}")
    except IndexError as e:
        print(f"Error splitting the message: {e}")


def insert_data_to_database(user_id, rfid, temperature_limit, light_limit, humidity_limit, name):
    sql = "INSERT INTO profile (UserID, RFID, Temperature_Limit, Light_Limit, Humidity_Limit, Name) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (user_id, rfid, temperature_limit, light_limit, humidity_limit, name)
    cursor.execute(sql, val)
    conn.commit()
    print("Data inserted into database.")


# Setup MQTT Client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()

# Navbar
navbar = dbc.NavbarSimple(
    brand="Welcome to IoT Dashboard",
    brand_href="#",
    color="black",
    dark=True,
    className="mb-5",
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
    html.Img(src=app.get_asset_url("fan.png"), style={'width': '100px', 'height': '100px'}),
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

# Footer definition
footer = html.Footer([
    dbc.Container("Team Members: Yassine El Yamani, Megane Kickouama, Peter Fishman, Ilan Trutner", className="text-white", style={"textAlign": "center"})
], className="bg-black py-3", style={"position": "fixed", "left": 0, "bottom": 0, "width": "100%"})

# Interval component for triggering periodic callbacks
interval_component = dcc.Interval(id='interval-component', interval=2500, n_intervals=0)

# App layout assembly
app.layout = html.Div([
    navbar,
    dbc.Container([
        dbc.Row([
            dbc.Col(ledBox, width=6, lg=3),
            dbc.Col(fanControl, width=6, lg=3),
        ], justify="around", className="mb-4"),
        dbc.Row([
            dbc.Col(temperatureGauge, width=6, lg=3),
            dbc.Col(humidityGauge, width=6, lg=3),
        ], justify="around"),
    ], fluid=True, style={"padding": "20px"}),
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
def update_light_level_and_email(n):
    global emailSent, light_level
    confirmation_message = ''
    led_image_src = app.get_asset_url('lightbulb_off.png')
    if light_level is not None:
        current_time = datetime.datetime.now().strftime("%H:%M")
        light_level_display = f"Current light level: {light_level}"
        logging.info(f"Checking light level: {light_level}")
        if light_level < 400:
            GPIO.output(40, GPIO.HIGH)
            led_image_src = app.get_asset_url('lightbulb_on.png')
            if not emailSent:
                send_email("The light is ON", f"The light is ON at {current_time} time!")
                emailSent = True
                confirmation_message = "Email has been sent!"
        else:
            GPIO.output(40, GPIO.LOW)
            led_image_src = app.get_asset_url('lightbulb_off.png')
            emailSent = False  # Reset the email sent flag when condition is no longer met
    else:
        light_level_display = "Waiting for light level data..."
        logging.info("No light level data available.")
    return confirmation_message, light_level_display, led_image_src


@app.callback(
    Output('humidity-gauge', 'value'),
    Output('temperature-thermometer', 'value'),
    Input('interval-component', 'n_intervals')
)

def update_sensor(n):
    global emailSent
    dht.readDHT11()
    temperatureValue = dht.temperature
    insert_data_to_database(user_id, rfid, temperature_limit, light_limit, humidity_limit, name)
    if temperatureValue > 24 and not emailSent:
        send_email("Temperature is High", "Would you like to start the fan?")
        emailSent = True
    elif receive_email():
        toggle_fan(True)
        time.sleep(5)
        toggle_fan(False)
    elif temperatureValue < 22:
        toggle_fan(False)
        emailSent = False

    humidityValue = dht.humidity
    print(humidityValue, temperatureValue)
    return humidityValue, temperatureValue


main()
