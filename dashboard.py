import dash.dependencies
import dash_daq as daq
from dash import html, Input, Output, dcc, Dash, State
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeChangerAIO
import RPi.GPIO as GPIO
import Freenove_DHT as DHT
import time
import smtplib
import imaplib
import easyimap as imap
import email

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

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
img = html.Img(src=app.get_asset_url('lightbulb_off.png'),width='100px', height='100px')
humidityValue = 0
temperatureValue = 0
emailSent = False

source_address = 'else6541@gmail.com'
dest_address = 'yasselyamani@gmail.com'
password = 'zcmf lmlv lcfu igqi'
imap_srv = 'imap.gmail.com'
imap_port = 993

css_animation = """
@keyframes rotate {
    from {
        transform: rotate(0deg);
    }
    to {
        transform: rotate(360deg);
    }
}

.rotate {
    animation: rotate 2s linear infinite;
}
"""

navbar = dbc.NavbarSimple(
    brand="Welcome to IoT Dashboard",
    brand_href="#",
    color="black",
    dark=True,
    className="mb-5",
)

# Body components
ledBox = html.Div(
    id='led-box',
    children=[
        html.H3('LED Control'),
        html.Button('Toggle LED', id='led-image', n_clicks=0),
    ],
    style={'text-align': 'center'}
)

fanControl = html.Div(
    id='fan-control',
    children=[
        html.H3('Fan'),
        html.Img(src=app.get_asset_url("fan.png"), id='fan-image' ,style={'width': '100px', 'height': '100px'}),
        daq.ToggleSwitch(id='fan-toggle', value=False, labelPosition="bottom"),
    ],
    style={'text-align': 'center'}
)

temperatureGauge = html.Div(
    id='temperature',
    children=[
        html.H3('Temperature'),
        daq.Thermometer(
            id='temperature-thermometer',
            value=temperatureValue,
            min=0,
            showCurrentValue=True,
            max=100,
            label="Degrees C"
        ),
    ],
    style={'text-align': 'center'}
)

humidityGauge = html.Div(
    id='humidity',
    children=[
        html.H3('Humidity'),
        daq.Gauge(
            id='humidity-gauge',
            value=humidityValue,
            min=0,
            max=100,
            showCurrentValue=True,
            label="Percent"
        ),
    ],
    style={'text-align': 'center'}
)

# Footer definition
footer = html.Footer(
    dbc.Container(
        "Team Members: Yassine El Yamani, Megane Kickouama, Peter Fishmann",
        className="text-white",
        style={"textAlign": "center"}
    ),
    className="bg-black py-3",
    style={"position": "fixed", "left": 0, "bottom": 0, "width": "100%"}
)

# Interval component for triggering periodic callbacks
interval_component = dcc.Interval(
    id='interval-component',
    interval=2000,  # 1.5 seconds
    n_intervals=0
)

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
    dcc.Store(id='fan-state-store', data={'fan_on': False}),
    interval_component,
    footer
], style={"backgroundColor": "white"})

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
    

@app.callback(Output('led-image', 'children'),
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
        return img

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

@app.callback(
    Output('fan-image', 'className'),
    [Input('fan-toggle', 'value')]
)
def rotate_fan(on):
    return "rotate" if on else ""

@app.callback(
    Output('humidity-gauge', 'value'),
    Output('temperature-thermometer', 'value'),
    Input('interval-component', 'n_intervals')
)

def update_sensor(n):
    global emailSent
    dht.readDHT11()
    temperatureValue = dht.temperature
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