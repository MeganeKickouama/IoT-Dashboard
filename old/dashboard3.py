#imports
from bluepy.btle import Scanner

class User:
    def __init__(self, user_id, rfid, temp_threshold, light_intensity):
        self.user_id = user_id
        self.rfid = rfid
        self.temp_threshold = temp_threshold
        self.light_intensity = light_intensity
    
instance_user = User(11, "123 456 789 000", 21.0, 2222) # for testing 

# profile button setup
profile_icon = html.I(className="bi bi-person-circle", style=dict(display="inline-block"))
btn_text = html.Div('Your Profile', style=dict(paddingRight="0.5vw", display="inline-block"))
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
                                html.Strong("User ID"),
                                html.P(f"{instance_user.user_id}"),
                            ]
                        ),
                        html.H5(
                            children=[
                                html.Strong("User RFID"),
                                html.P(f"{instance_user.rfid}"),
                            ]
                        ),
                        html.H5(
                            children=[
                                html.Strong("Temperature Threshold"),
                                html.P(f"{instance_user.temp_threshold}"),
                            ]
                        ),
                        html.H5(
                            children=[
                                html.Strong("Light Intensity Threshold"),
                                html.P(f"{instance_user.light_intensity}"),
                            ]
                        ),
                        
                    ]
                ),
            ],
            id="offcanvas",
            title="Welcome,",
            is_open=False,
        ),
    ]
)

# just put "profile" in the children of the navbar
navbar = dbc.NavbarSimple(
    children=[
        profile,
    ],
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
            html.Img(src=app.get_asset_url('bluetooth'),width='60px', height='60px'),
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


# I changed the app layout so it has 2 rows and 3 columns
# (the teacher said the whole dashboard should fit in 1 page without scrolling
app.layout = html.Div([
    navbar,
    dash_mqtt.DashMqtt(
        id='mqtt'            
    ),
    dbc.Container([
        dbc.Row([
            dbc.Col(ledBox, width=6, lg=3),
            dbc.Col(fanControl, width=6, lg=3),
            dbc.Col(photoResistor, width=6, lg=3),
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