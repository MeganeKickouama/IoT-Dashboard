import dash
from dash import html

external_stylesheets = ['']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    children=[
        html.Div(
            className="wrapper",
            children=[
                # Top menu
                html.Div(
                    className="sidebar",
                    children=[
                        html.Div(
                            className="profile",
                            children=[
                                html.Img(
                                    src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCshQ1PdEP1zRjFjqv72i0uAq8CuRjncbdDP3wUFjVpw&s",
                                    alt="profile_picture"
                                ),
                                html.H3("First Name"),
                                html.P("Last Name")
                            ]
                        ),
                        # Menu items
                        html.Ul(
                            children=[
                                html.Li(
                                    children=[
                                        html.A(
                                            href="#",
                                            className="active",
                                            children=[
                                                html.Span(className="icon", children=[html.I(className="fas fa-home")]),
                                                html.Span(className="item", children="Home")
                                            ]
                                        )
                                    ]
                                ),
                                html.Li(
                                    children=[
                                        html.A(
                                            href="#",
                                            children=[
                                                html.Span(className="icon", children=[html.I(className="fas fa-desktop")]),
                                                html.Span(className="item", children="My Dashboard")
                                            ]
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                ),
                html.Div(
                    className="section",
                    children=[
                        html.Div(
                            className="top_navbar",
                            children=[
                                html.Div(
                                    className="hamburger",
                                    children=[
                                        html.A(
                                            href="#",
                                            children=[
                                                html.I(className="fa fa-bars", hidden="true")
                                            ]
                                        ),
                                        html.H1("IoT Dashboard Phase #2")
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        ),
        html.Div(
            id="main",
            children=[
                html.Table(
                    id="main-table",
                    children=[
                        # Row 1
                        html.Tr(
                            children=[
                                html.Td(
                                    colSpan="3", rowSpan="2",
                                    children=[
                                        html.Div(
                                            className="time-container global-containers",
                                            children=[
                                                html.Section(
                                                    children=[
                                                        html.Div(
                                                            className="container",
                                                            children=[
                                                                html.Div(
                                                                    className="icons",
                                                                    children=[
                                                                        html.I(className="fas fa-moon", hidden=True),
                                                                        html.I(className="fas fa-sun", hidden=True)
                                                                    ]
                                                                ),
                                                                html.Div(
                                                                    className="time",
                                                                    children=[
                                                                        html.Div(
                                                                            className="time-colon",
                                                                            children=[
                                                                                html.Div(
                                                                                    className="time-text",
                                                                                    children=[
                                                                                        html.Span(className="num hour_num", children="08"),
                                                                                        html.Span(className="text", children="Hours")
                                                                                    ]
                                                                                ),
                                                                                html.Span(className="colon", children=":")
                                                                            ]
                                                                        ),
                                                                        html.Div(
                                                                            className="time-colon",
                                                                            children=[
                                                                                html.Div(
                                                                                    className="time-text",
                                                                                    children=[
                                                                                        html.Span(className="num min_num", children="45"),
                                                                                        html.Span(className="text", children="Minutes")
                                                                                    ]
                                                                                ),
                                                                                html.Span(className="colon", children=":")
                                                                            ]
                                                                        ),
                                                                        html.Div(
                                                                            className="time-colon",
                                                                            children=[
                                                                                html.Div(
                                                                                    className="time-text",
                                                                                    children=[
                                                                                        html.Span(className="num sec_num", children="06"),
                                                                                        html.Span(className="text", children="Seconds")
                                                                                    ]
                                                                                ),
                                                                                html.Span(className="am_pm", children="AM")
                                                                            ]
                                                                        )
                                                                    ]
                                                                )
                                                            ]
                                                        )
                                                    ]
                                                )
                                            ]
                                        )
                                    ]
                                ),
                                html.Td(
                                    colSpan="3", rowSpan="1", id="gauge-cell",
                                    children=[
                                        html.Div(
                                            id="gauge-row",
                                            children=[
                                                html.Div(
                                                    className="gauge-containers global-containers",
                                                    children="[gauge temperature]"
                                                ),
                                                html.Div(
                                                    className="gauge-containers global-containers",
                                                    children="[gauge humidity]"
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]
                        ),
                        # Row 2
                        html.Tr(
                            children=[
                                html.Td(
                                    children=[
                                        html.Div(
                                            className="smallest-containers global-containers",
                                            children=[
                                                # [light]
                                                html.Div(
                                                    className="led-container",
                                                    children=[
                                                        html.Div(
                                                            className="lamp-container",
                                                            children=[
                                                                html.Div(id="lamp", className="off"),
                                                                html.Label(
                                                                    className="switch",
                                                                    children=[
                                                                        # html.Input(type="checkbox", id="toggleSwitch"), # onClick="toggle_led()"
                                                                        html.Span(className="slider")
                                                                    ]
                                                                )
                                                            ]
                                                        )
                                                    ]
                                                )
                                            ]
                                        )
                                    ]
                                ),
                                html.Td(
                                    children=[
                                        html.Div(
                                            className="smallest-containers global-containers",
                                            children="[fan]"
                                        )
                                    ]
                                ),
                                html.Td(
                                    children=[
                                        html.Div(
                                            className="smallest-containers global-containers",
                                            children="[e]"
                                        )
                                    ]
                                )
                            ]
                        ),
                        # Row 3
                        html.Tr(
                            children=[
                                html.Td(
                                    colSpan="3",
                                    children=[
                                        html.Div(
                                            className="left-bottom-container global-containers",
                                            children=[
                                                html.H2("[f]")
                                            ]
                                        )
                                    ]
                                ),
                                html.Td(
                                    colSpan="1",
                                    children=[
                                        html.Div(
                                            className="smallest-containers global-containers",
                                            children=[
                                                html.H2("[g]")
                                            ]
                                        )
                                    ]
                                ),
                                html.Td(
                                    colSpan="1",
                                    children=[
                                        html.Div(
                                            className="smallest-containers global-containers",
                                            children=[
                                                html.H2("[h]")
                                            ]
                                        )
                                    ]
                                ),
                                html.Td(
                                    colSpan="1",
                                    children=[
                                        html.Div(
                                            className="smallest-containers global-containers",
                                            children=[
                                                html.H2("[i]")
                                            ]
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        ),
        html.Footer("IoT Dashboard - Section 000001 - [Members]")
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
