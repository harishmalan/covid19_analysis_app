import pickle
import copy
import pathlib
import dash
import math
import datetime as dt
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import dash_table
from data_cleanup import *
import pycountry

COUNTIES_ISO ={}
for country in pycountry.countries:
    COUNTIES_ISO[country.name] = country.alpha_3

covid19_table= pd.DataFrame
covid19_table=dataset_downlaod_df()

# Grouped by day, country
# =======================
covid19_country = pd.DataFrame
covid19_country =groupby_day_country(covid19_table)

#Day_wise df
day_wise = pd.DataFrame
day_wise = day_wise_dataframe(covid19_country)

#country_wise 
country_wise = pd.DataFrame
country_wise = country_wise_dataframe(covid19_country)
country_wise['iso_alpha'] =country_wise['Country'].map(COUNTIES_ISO)
datatabler = country_wise[['Country','Confirmed','Deaths','Recovered','Active']]
# # Multi-dropdown options
# from controls import COUNTIES, WELL_STATUSES, WELL_TYPES, WELL_COLORS

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()



app = dash.Dash(
    __name__, meta_tags=[{"Covid19": "viewport", "content": "width=device-width"}]
)
server = app.server

# Create Country for Drop Down
county_options = [
    {"label": str(country), "value": str(country)}
    for country in covid19_country.Country
]

# Create app layout
app.layout = html.Div(
    [
        dcc.Store(id="aggregate_data"),
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),
        html.Div
        (
            [
                html.Div
                (
                    [
                        html.Img
                        (
                            src=app.get_asset_url("dash-logo1.png"),
                            id="plotly-image",
                            style=
                            {
                                "height": "60px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        )
                    ],
                    className="one-third column",
                ),
                html.Div
                (
                    [
                        html.Div
                        (
                            [
                                html.H4
                                (
                                    "Data Modelling & Analysing Coronavirus: Exploratory Analysis",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5
                                (
                                    "Covid19 Pandamic Overview", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                ),
                html.Div
                (
                    [
                        html.A
                        (
                            html.Button("Developer Info", id="learn-more-button"),
                            href="http://www.harishmalan.com/",
                        )
                    ],
                    className="one-third column",
                    id="button",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        html.Div
        (
            [
                 html.Div(
                     [
                         html.Div
                         (
                             [
                                 html.Div
                                 (
                                     [ 
                                         html.P("Covid19 Analysis (select Country from Dropdown):")
                                    ],
                            className="control_label",
                            ),
                            html.Div
                            (
                                [
                                    dcc.Dropdown(
                                    id="country_dropdown",
                                    options=county_options,
                                    value= 'Singapore',
                                    multi=False,)
                                ],
                                className="dcc_control six columns",
                            ),
                            ],
                        id="info-container-left",
                        className="row container-display",
                         ),
                         html.Div(
                             [
                                 html.Div(
                                    [html.H6(id="confirm_left"), html.P("Confirmed")],
                                    id="country_confirm",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="death_left"), html.P("Death's")],
                                    id="country_death",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="recovery_left"), html.P("Recovered")],
                                    id="country_recovery",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="new_left"), html.P("New Cases")],
                                    id="new_active",
                                    className="mini_container",
                                ),
                             ],
                            id="info-container-left-2",
                            className="row container-display",
                         ),

                           html.Div([html.Span("Select the Metric to display in Plot : ", className="six columns",
                                           style={"text-align": "right", "width": "40%", "padding-top": 10}),
                                 dcc.Dropdown(id="value-selected_left", value='New cases',
                                              options=[{'label': "Confirmed Cases", 'value': 'Confirmed'},
                                                       {'label': "Deaths Cases ", 'value': 'Deaths'},
                                                       {'label': "Recovered Cases", 'value': 'Recovered'},
                                                       {'label': "Active", 'value': 'Active'},
                                                       {'label': "New Cases", 'value': 'New cases'},
                                                       {'label': "New Death's", 'value': 'New deaths'},
                                                       {'label': "New Recovery", 'value': 'New recovered'},
                                                       ],
                                                       multi=False,
                                              style={"display": "block", "margin-left": "auto", "margin-right": "auto",
                                                     "width": "70%"},
                                              className="six columns")], className="row"),
                         html.Div(id='country_metric'),
                    ],
                    className="pretty_container six columns",
                    id="cross-filter-options",
                ),
                html.Div(
                    [
                        html.P(
                            "World Wide Covid19 Analysis",
                            className="control_label",
                        ),
                        html.Div(
                            [
                                
                                html.Div(
                                    [html.H6(id="world_confirm"), html.P("Confirmed")],
                                    id="confirm",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="world_death"), html.P("Death's")],
                                    id="death",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="world_recovery"), html.P("Recovered")],
                                    id="recovery",
                                    className="mini_container",
                                ),
                                  html.Div(
                                    [html.H6(id="world_new"), html.P("New Cases")],
                                    id="active_new",
                                    className="mini_container",
                                ),
                            ],
                            id="info-container",
                            className="row container-display",
                        ),
                         html.Div([html.Span("Select Metric to displayed in Map : ", className="six columns",
                                           style={"text-align": "right", "width": "40%", "padding-top": 10}),
                                 dcc.Dropdown(id="value-selected", value='New cases',
                                              options=[{'label': "Confirmed Cases", 'value': 'Confirmed'},
                                                       {'label': "Deaths Cases ", 'value': 'Deaths'},
                                                       {'label': "Recovered Cases", 'value': 'Recovered'},
                                                       {'label': "New Cases", 'value': 'New cases'},
                                                       {'label': "Deaths / 100 Cases", 'value': 'Deaths / 100 Cases'},
                                                       {'label': "Recovered / 100 Cases", 'value': 'Recovered / 100 Cases'},
                                                       {'label': "Deaths / 100 Recovered", 'value': 'Deaths / 100 Recovered'},
                                                       ],
                                              style={"display": "block", "margin-left": "auto", "margin-right": "auto",
                                                     "width": "70%"},
                                              className="six columns")], className="row"),
                        dcc.Graph(id="world_matrix")
                    ],
                    id="right-column",
                    className="pretty_container six columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [html.Div(id="country_wide_graph")],
                    className="pretty_container six columns",
                ),
                html.Div(
                    #[dcc.Graph(id="world_wide_graph")],
                     [html.Div(id='world_wide_graph')],
                    className="pretty_container six columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [html.Div(id="country_sir_pred")],
                    className="pretty_container six columns",
                ),
                html.Div(
                    [html.Div(id="death_recovery_martix")],
                    className="pretty_container six columns",
                ),
            ],
            className="row flex-display",
        ),

    html.Div(
        [
            dcc.Markdown('''
            ### Data Modelling and Prediction 
           Just because the rise in number of cases is exponential, it does not imply that we can fit the data to an exponential 
           curve and predict the number of cases in the coming days. Compartmental model techniques are normally used to model infectious diseases. 
           Same could be used in the case of  COVID-19 too. The simplest compartmental model is the SIR model. The following excerpt  from this source
            link describes the model and its basic blocks. '''),
            dcc.Markdown('''
            The model consists of three compartments: S for the number of susceptible, I for the number of infectious, and R for the 
            number of recovered or deceased (or immune) individuals. This model is reasonably predictive for infectious diseases which 
            are transmitted from human to human, and where recovery confers lasting resistance, such as measles, mumps and rubella. '''),
            dcc.Markdown('''Each member of the population typically progresses from susceptible to infectious to recovered. This can be 
            shown as a flow diagram in which the boxes represent the different compartments and the arrows the transition between compartments, i.e.
            '''),
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("SIR-SIRS.png"),
                            id="plotly-image2",
                            style={
                                "height": "120px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        )
                    ],
                    #className="one-third column",
                ),
            dcc.Markdown('''In multiple models developed for COVID-19 (diffusion medium: Airborne Droplet) by experts and researchers they try to 
            estimate the right set of parameters for the region/country. As per the CDC and WHO, the R0 for COVID-19 is definitely above 2. 
            Some sources say it is between 3-5.
            ''' ),
            dcc.Markdown('''
            In the model, the value R0 is an estimate of the number of people an average infected person will spread the disease to. If the value of R0 
            is greater than 1 then the disease probably continues to spread and if it is < 1 then the disease slowly dies down. Since COVID-19’s R0 is > 2, 
            so an average infected person spreads it to 2 or more people who again spread it to 2 or more people and that is how this infection continues to 
            spread across the globe. There are other parameters in the model like and which needs to be estimated. You can read more about the model params and 
            related differential equations here. 
            '''),
            dcc.Markdown('''
            As a matter of fact, there is a well-documented example in the scipy package on SIR model. Check out this link for more clarity on the calculations 
            of these parameters. I also came across a blog “COVID-19 dynamics with SIR model” on how to estimate these parameters from available COVID-19 data. 
            It turns out that the differential equations can be easily solved and tuning of the parameters of the model can be done using the “solve_ivp” function in the scipy module. 
            '''),
            dcc.Markdown('''
            ### what Can we Do ?
            Since there is no vaccine available right now, the only way to handle the spread is to slow down the transmission. As it can be seen even in the 
            under-estimates and from the actual data around us, the sharply increasing number of cases is bound to overwhelm the medical infrastructure of any
             nation. So, by slowing down the transmission, we don’t actually stop the spread but keep the transmission and the active cases at any point in time
            well within the limits of the medical handling capacity. This is what is being referred to as “Flattening The Curve”. 
            '''),
            html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("flat_curve.png"),
                            id="plotly-image1",
                            style={
                                "height": "200px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        )
                    ],
                    className="one-third column",
                ),
           

            # ![COVID-19](https://lh6.googleusercontent.com/WwmVkWAdqQmQpVAKBad1PAVS3AtsLnkbgl2M0k2Tyr6DDPEol1PzpYHeySEIO_dLxqaxJ1NVUmKl5bvlEciMrZtTLsC3vxBmD72xnlX37Wd8p1lBOum2dW4fsDXTw3sm8KjJ8SpnbqWKpJxc2A)
            # ''')
            # dcc.Markdown('''
            # ### Data Modelling and Prediction Just because the rise in number of cases is exponential, it does not imply that we can fit the 
            # data to an exponential curve and predict the number of cases in the coming days. Compartmental model techniques are normally used 
            # to model infectious diseases. Same could be used in the case of  COVID-19 too. The simplest compartmental model is the SIR model. 
            # The following excerpt  from this source link describes the model and its basic blocks. The model consists of three compartments: S 
            # for the number of susceptible, I for the number of infectious, and R for the number of recovered or deceased (or immune) individuals. 
            # This model is reasonably predictive for infectious diseases which are transmitted from human to human, and where recovery confers lasting 
            # resistance, such as measles, mumps and rubella.Each member of the population typically progresses from susceptible to infectious to recovered. 
            # This can be shown as a flow diagram in which the boxes represent the different compartments and the arrows the transition between compartments, i.e.
            # ![COVID-19](https://lh6.googleusercontent.com/WwmVkWAdqQmQpVAKBad1PAVS3AtsLnkbgl2M0k2Tyr6DDPEol1PzpYHeySEIO_dLxqaxJ1NVUmKl5bvlEciMrZtTLsC3vxBmD72xnlX37Wd8p1lBOum2dW4fsDXTw3sm8KjJ8SpnbqWKpJxc2A)
            # ''')
        ],

    ),



        html.Div([
   dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {"name": i, "id": i, "deletable": True, "selectable": True} for i in datatabler.columns
        ],
        data=country_wise.to_dict('records'),
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        column_selectable="single",
        row_selectable="multi",
        row_deletable=True,
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current= 0,
        page_size= 10,
        
    ),
    html.Div(id='datatable-interactivity-container')
]),
    dcc.Markdown('''
   ### Reference Links: 
Novel Coronavirus (COVID-19) Cases, provided by JHU CSSE  
https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge  
https://github.com/CSSEGISandData/COVID-19/tree/master/csse_COVID_19_data/csse_covid_19_time_series  
https://github.com/CSSEGISandData/COVID-19/tree/web-data  
https://scipython.com/book/chapter-8-scipy/additional-examples/the-sir-epidemic-model/  
https://www.lewuathe.com/COVID-19-dynamics-with-sir-model.html  
https://github.com/Lewuathe/COVID19-SIR  
https://science.sciencemag.org/content/early/2020/03/05/science.aba9757  
https://en.wikipedia.org/wiki/Compartmental_models_in_epidemiology  
https://science.sciencemag.org/content/early/2020/03/05/science.aba9757/tab-figures-data  
'''),
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
    className= "row flex-display",
)

# Selectors -> well text
@app.callback(
    [
    Output("confirm_left", "children"),
    Output("death_left", "children"),
    Output("recovery_left", "children"),
    Output("new_left", "children"),
    ],
    [
        Input("country_dropdown", "value"),
    ],
)
def update_well_text(country_dropdown):
    temp= country_wise[country_wise['Country']==country_dropdown]
    return temp['Confirmed'],temp['Deaths'], temp['Recovered'], temp['New cases']

@app.callback(
    [
        Output("world_confirm", "children"),
        Output("world_death", "children"),
        Output("world_recovery", "children"),
         Output("world_new", "children"),
    ],
    [
        Input("country_dropdown", "value"),
    ],
)
def update_well_text(country_dropdown):

    # dff = filter_dataframe(country_dropdown)
    temp = covid19_country.groupby('Date')['Confirmed', 'Deaths', 'Recovered', 'Active', 'New cases'].sum().reset_index()
    temp = temp[temp['Date']==max(temp['Date'])].reset_index(drop=True)
    return temp['Confirmed'],temp['Deaths'], temp['Recovered'], temp['New cases']

# @app.callback(
#     Output('datatable-interactivity', 'style_data_conditional'),
#     [Input('datatable-interactivity', 'selected_columns')]
# )
# def update_styles(selected_columns):
#     return [{
#         'if': { 'column_id': i },
#         'background_color': '#D2F3FF'
#     } for i in selected_columns]

@app.callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    [Input('datatable-interactivity', 'selected_columns')]
)
def update_styles(selected_columns):
    return [{
        'if': { 'column_id': i },
        'background_color': '#D2F3FF'
    } for i in selected_columns]

@app.callback(
    Output('datatable-interactivity-container', "children"),
    [Input('datatable-interactivity', "derived_virtual_data"),
     Input('datatable-interactivity', "derived_virtual_selected_rows")])
def update_graphs(rows, derived_virtual_selected_rows):
    # When the table is first rendered, `derived_virtual_data` and
    # `derived_virtual_selected_rows` will be `None`. This is due to an
    # idiosyncracy in Dash (unsupplied properties are always None and Dash
    # calls the dependent callbacks when the component is first rendered).
    # So, if `rows` is `None`, then the component was just rendered
    # and its value will be the same as the component's dataframe.
    # Instead of setting `None` in here, you could also set
    # `derived_virtual_data=df.to_rows('dict')` when you initialize
    # the component.
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    dff = country_wise if rows is None else pd.DataFrame(rows)
    dff = dff.sort_values(by=['New cases'],ascending=False).head(50)

    colors = ['#7FDBFF' if i in derived_virtual_selected_rows else '#0074D9'
              for i in range(len(dff))]

    return [
        dcc.Graph(
            id=column,
            figure={
                "data": [
                    {
                        "x": dff["Country"],
                        "y": dff[column],
                        "type": "bar",
                        "marker": {"color": colors},
                    }
                ],
                "layout": {
                    "xaxis": {"automargin": True},
                    "yaxis": {
                        "automargin": True,
                        "title": {"text": column}
                    },
                    "height": 250,
                    "margin": {"t": 10, "l": 10, "r": 10},
                },
            },
        )
        # check if column exists - user may have deleted it
        # If `column.deletable=False`, then you don't
        # need to do this check.
        for column in ["New cases","Confirmed", "Deaths", "Recovered", "Active"] if column in dff
    ]
# @app.callback(
#     Output('count_graph', "children"),
@app.callback(
    dash.dependencies.Output("world_matrix", "figure"),
    [dash.dependencies.Input("value-selected", "value")]
)
def update_figure(selected):
    
    dff =country_wise

    # def title(text):
    #     if text == "pop":
    #         return "Poplulation (million)"
    #     elif text == "gdpPercap":
    #         return "GDP Per Capita (USD)"
    #     else:
    #         return "Life Expectancy (Years)"
    trace = go.Choropleth(locations=dff['iso_alpha'],z=dff[selected],text=dff['Country'],autocolorscale=True,
                          colorscale="GnBu",marker={'line': {'color': 'rgb(180,180,180)','width': 0.5}},
                          colorbar={
                                    'title': {"text": selected, "side": "bottom"}})
    return {"data": [trace],
            "layout": go.Layout(title=selected,height=500,geo={'showframe': False,'showcoastlines': False,
                                                                      'projection': {'type': "miller"}})}


@app.callback(
    Output(component_id='country_metric', component_property='children'),
    [Input(component_id='country_dropdown', component_property='value'),
    Input(component_id='value-selected_left', component_property='value')]
)
def update_value(country_dropdown, selected_left):
    # day_wise.reset_index(inplace=True)
    # day_wise.set_index("Date", inplace=True)
    dff= covid19_country[covid19_country['Country']==country_dropdown]
    dff.reset_index(inplace=True)
    dff.set_index("Date", inplace=True)

    return dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': dff.index, 'y': dff[selected_left], 'type': 'lines+markers', 'name': country_dropdown, 'mode':'lines+markers'},
            ],
            'layout': {
                'title': "Total New cases ("+country_dropdown+")",
                 'yaxis_title': "New confirmed Cases",
                 'x_axis_tickangle': 315
            }
        }
    )

@app.callback(
    Output(component_id='world_wide_graph', component_property='children'),
    [Input(component_id='country_dropdown', component_property='value')]
)
def update_value(country_dropdown):
    # day_wise.reset_index(inplace=True)
    # day_wise.set_index("Date", inplace=True)
    dff= day_wise
    dff.reset_index(inplace=True)
    dff.set_index("Date", inplace=True)

    return dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                dict(
                    type="scatter",
                    mode="lines",
                    name="Confirmed",
                    x=dff.index,
                    y=dff['Confirmed'],
                    line=dict(shape="spline", smoothing="2", color="#F9ADA0"),
                    ),
                dict(
                    type="scatter",
                    mode="lines",
                    name="Death's",
                    x=dff.index,
                    y=dff['Deaths'],
                    line=dict(shape="spline", smoothing="2", color="#849E68"),
                    ),
                dict(
                    type="scatter",
                    mode="lines",
                    name="Recovered",
                    x=dff.index,
                    y=dff['Recovered'],
                    line=dict(shape="spline", smoothing="2", color="#59C3C3"),
                    ),
            ],
            'layout': {
                'title': "World Wide Report",
                 'yaxis_title': "New confirmed Cases",
                 'x_axis_tickangle': 315
            }
        }
    )

@app.callback(
    Output(component_id='country_wide_graph', component_property='children'),
    [Input(component_id='country_dropdown', component_property='value')]
)
def update_value(country_dropdown):
    #layout_aggregate = copy.deepcopy(layout)
    # day_wise.reset_index(inplace=True)
    # day_wise.set_index("Date", inplace=True)
    dff= covid19_country[covid19_country['Country']==country_dropdown]


    return dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                #{'x': dff.index, 'y': dff['Confirmed'], 'type': 'lines', 'name': country_dropdown, 'mode':'lines+markers', 'name':"Confirmed"},
                dict(
                    type="scatter",
                    mode="lines",
                    name="Confirmed",
                    x=dff['Date'],
                    y=dff['Confirmed'],
                    line=dict(shape="spline", smoothing="2", color="#F9ADA0"),
                    ),
                dict(
                    type="scatter",
                    mode="lines",
                    name="Death's",
                    x=dff['Date'],
                    y=dff['Deaths'],
                    line=dict(shape="spline", smoothing="2", color="#849E68"),
                    ),
                dict(
                    type="scatter",
                    mode="lines",
                    name="Recovered",
                    x=dff['Date'],
                    y=dff['Recovered'],
                    line=dict(shape="spline", smoothing="2", color="#59C3C3"),
                    ),
                
            ],
            'layout': {
                'title': "Country Wide Report ("+country_dropdown+")",
                 'y_title': "New confirmed Cases",
                 'x_axis_tickangle': 180
            }
        }
    )
@app.callback(
    Output(component_id='country_sir_pred', component_property='children'),
    [Input(component_id='country_dropdown', component_property='value')]
)
def update_value(country_dropdown):
    #layout_aggregate = copy.deepcopy(layout)
    # day_wise.reset_index(inplace=True)
    # day_wise.set_index("Date", inplace=True)
    dff = pd.read_csv(DATA_PATH.joinpath(country_dropdown+".csv"),low_memory=False, index_col=0)
    # dff.reset_index(inplace=True)
    # dff.set_index("Date", inplace=True)

    return dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                #{'x': dff.index, 'y': dff['Confirmed'], 'type': 'lines', 'name': country_dropdown, 'mode':'lines+markers', 'name':"Confirmed"},
                dict(
                    type="scatter",
                    mode="lines",
                    name="Susceptible",
                    x=dff.index,
                    y=dff['Susceptible'],
                    line=dict(shape="spline", smoothing="2", color="#F9ADA0"),
                    ),
                dict(
                    type="scatter",
                    mode="lines",
                    name="Infected",
                    x=dff.index,
                    y=dff['Infected'],
                    line=dict(shape="spline", smoothing="2", color="#849E68"),
                    ),
                dict(
                    type="scatter",
                    mode="lines",
                    name="Recovered",
                    x=dff.index,
                    y=dff['Recovered'],
                    line=dict(shape="spline", smoothing="2", color="#59C3C3"),
                    ),
                
            ],
            'layout': {
                'title': "Predicting Suspect Infection Curve Report ("+country_dropdown+")",
                 'y_title': "New confirmed Cases",
                 'x_axis_tickangle': 180
            }
        }
    )
@app.callback(
    Output(component_id='death_recovery_martix', component_property='children'),
    [Input(component_id='country_dropdown', component_property='value')]
)
def update_value(country_dropdown):
    #layout_aggregate = copy.deepcopy(layout)
    # day_wise.reset_index(inplace=True)
    # day_wise.set_index("Date", inplace=True)
    dff = day_wise
    dff.reset_index(inplace=True)
    dff.set_index("Date", inplace=True)

    return dcc.Graph(
        id='example-graph1',
        figure={
            'data': [
                #{'x': dff.index, 'y': dff['Confirmed'], 'type': 'lines', 'name': country_dropdown, 'mode':'lines+markers', 'name':"Confirmed"},
                dict(
                    type="scatter",
                    mode="lines",
                    name="Deaths / 100 Cases",
                    x=dff.index,
                    y=dff['Deaths / 100 Cases'],
                    line=dict(shape="spline", smoothing="2", color="#F9ADA0"),
                    ),
                dict(
                    type="scatter",
                    mode="lines",
                    name="Recovered / 100 Cases",
                    x=dff.index,
                    y=dff['Recovered / 100 Cases'],
                    line=dict(shape="spline", smoothing="2", color="#849E68"),
                    ),
                # dict(
                #     type="scatter",
                #     mode="lines",
                #     name="Deaths / 100 Recovered",
                #     x=dff.index,
                #     y=dff['Deaths / 100 Recovered'],
                #     line=dict(shape="spline", smoothing="2", color="#59C3C3"),
                #     ),
                
            ],
            'layout': {
                'title': "Death's and Recovered Matrix Per 100 cases",
                 'y_title': "New confirmed Cases",
                 'x_axis_tickangle': 180
            }
        }
    )
# Main
if __name__ == "__main__":
    app.run_server(debug=True)
