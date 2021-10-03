
import numpy as np
import pandas as pd     #(version 1.0.0)
import plotly           #(version 4.5.4) pip install plotly==4.5.4
import plotly.express as px
import plotly.graph_objs as go
import dash             #(version 1.9.1) pip install dash==1.9.1
import dash_table
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import folium


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css','https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.13.0/css/font-awesome.min.css']

dash_app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app = dash_app.server

#Overwrite your CSS setting by including style locally
colors = {
    'background': '#2D2D2D',
    'text': '#E1E2E5',
    'figure_text': '#ffffff',
    'confirmed_text':'Orange',
    'deaths_text':'#f44336',
    'recovered_text':'#5A9E6F',
    'highest_case_bg':'#393939',

}

#Creating custom style for local use
divBorderStyle = {
    'backgroundColor' : '#393939',
    'borderRadius': '8px',
    'lineHeight': 0.5,
    'marginBottom': 10,
}

#Creating custom style for local use
boxBorderStyle = {
    'borderColor' : '#393939',
    'borderStyle': 'solid',
    'borderRadius': '8px',
    'borderWidth':5,
}

#fig = go.Figure()

#---------------------------------------------------------------
#Loading data right from the source:
death_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
confirmed_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
recovered_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')
country_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_country.csv')# changing province/state to state and country/region to country
confirmed_df = confirmed_df.rename(columns={'province/state': 'state', 'country/region': 'country'})
# renaming the df column names to lowercase

country_df.columns = map(str.lower, country_df.columns)
confirmed_df.columns = map(str.lower, confirmed_df.columns)
death_df.columns = map(str.lower, death_df.columns)
recovered_df.columns = map(str.lower, recovered_df.columns)

# changing province/state to state and country/region to country
confirmed_df = confirmed_df.rename(columns={'province/state': 'state', 'country/region': 'country'})
recovered_df = recovered_df.rename(columns={'province/state': 'state', 'country/region': 'country'})
death_df = death_df.rename(columns={'province/state': 'state', 'country/region': 'country'})
country_df = country_df.rename(columns={'country_region': 'country'})
#print(country_df.head(5))
#drop na
confirmed_df=confirmed_df.dropna(subset=['long'])

confirmed_df=confirmed_df.dropna(subset=['lat'])

death_df=death_df.dropna(subset=['long'])

death_df=death_df.dropna(subset=['lat'])

recovered_df=recovered_df.dropna(subset=['long'])

recovered_df=recovered_df.dropna(subset=['lat'])

#country_df= country_df.dropna(subset=['recovered'])

# total number of confirmed, death and recovered cases
confirmed_total = int(country_df['confirmed'].sum())
deaths_total = int(country_df['deaths'].sum())
recovered_total = int(country_df['recovered'].sum())
active_total = int(country_df['active'].sum())

country_dff = country_df.groupby('country', as_index=False)[['confirmed','deaths','recovered']].sum()
sorted_country_dff = country_dff.sort_values('confirmed',ascending=False)

#---------------------------------------------------------------
dash_app.layout = html.Div([


        # Header display
        html.Div(
            [
                html.H3(children='Covid-19 Coronavirus Tracker',
                        style={
                            'textAlign': 'left',
                            'color': 'white',
                            'backgroundColor': colors['background'],
                            'font-weight': 'bold',
                        },
                        className='twelve columns',)
            ], className="row",style={ 'marginBottom':0.15}
        ),

    # Paragrah Setup to Total Cases, Dec, Recovered
      html.Div([
            html.Div([
                html.H4(children='Total Cases: ',
                       style={
                           'textAlign': 'center',
                           'color': colors['confirmed_text'],
                       }
                       ),
                html.P(f"{confirmed_total:,}",
                       style={
                    'textAlign': 'center',
                    'color': colors['confirmed_text'],
                    'fontSize': 20,
                }
                )
                ],
                style=divBorderStyle,
                className='four columns'),
            html.Div([
                html.H4(children='Total Deceased: ',
                       style={
                           'textAlign': 'center',
                           'color': colors['deaths_text'],
                       }
                       ),
                html.P(f"{deaths_total:,}",
                       style={
                    'textAlign': 'center',
                    'color': colors['deaths_text'],
                    'fontSize': 20,
                }
                )
            ],
                style=divBorderStyle,
                className='four columns'),
            html.Div([
                html.H4(children='Total Recovered: ',
                       style={
                           'textAlign': 'center',
                           'color': colors['recovered_text'],
                       }
                       ),
                html.P(f"{recovered_total:,}",
                       style={
                    'textAlign': 'center',
                    'color': colors['recovered_text'],

                    'fontSize': 20,
                }
                )
            ],
                style=divBorderStyle,
                className='four columns'),
        ], className='row'),

   # Radio button,ticker and two graphs
     html.Div(
            [
                html.H6(children='Global Covid-19 cases by Country',
                         style={
                             'textAlign': 'center',
                             'color': colors['text'],
                             'backgroundColor': colors['background'],

                         },
                         className='twelve columns'
                         ),


                    html.Div([
                        dash_table.DataTable(
                            id='datatable_id',
                            data=country_dff.to_dict('records'),
                            columns=[
                                {"name": i, "id": i, "deletable": False, "selectable": False} for i in country_dff.columns
                            ],
                            fixed_rows={'headers': True, 'data': 0},
                                            style_header={
                                                'backgroundColor': 'rgb(30, 30, 30)',
                                                'fontWeight': 'bold'
                                            },
                                            style_cell={
                                                'backgroundColor': 'rgb(100, 100, 100)',
                                                'color': colors['text'],
                                                'maxWidth': 0,
                                                'fontSize':12,
                                            },
                                            style_table={
                                                'maxHeight': '350px',
                                                'overflowY': 'auto'
                                            },
                                            style_data={
                                                'whiteSpace': 'normal',
                                                'height': 'auto',

                                            },
                                            style_data_conditional=[
                                                {
                                                    'if': {'row_index': 'even'},
                                                    'backgroundColor': 'rgb(60, 60, 60)',
                                                },
                                                {
                                                    'if': {'column_id' : 'confirmed'},
                                                    'color':'Orange',
                                                    'fontWeight': 'bold'
                                                },
                                                {
                                                    'if': {'column_id' : 'deaths'},
                                                    'color':colors['deaths_text'],
                                                    'fontWeight': 'bold'
                                                },
                                                {
                                                    'if': {'column_id' : 'recovered'},
                                                    'color':colors['recovered_text'],
                                                    'fontWeight': 'bold'
                                                },
                                                ],
                                            style_cell_conditional=[
                                                {'if': {'column_id': 'country'},
                                                 'width': '40%','textAlign':'left'},
                                                {'if': {'column_id': 'cases'},
                                                 'width': '20%'},
                                                {'if': {'column_id': 'deaths'},
                                                 'width': '20%'},
                                                {'if': {'column_id': 'recovered'},
                                                 'width': '20%'},
                                            ],

                                            editable=False,
                                            filter_action="native",
                                            sort_action="native",
                                            sort_mode="single",
                                            row_selectable="single",
                                            row_deletable=False,
                                            selected_columns=[],
                                            selected_rows=[],
                                            page_current=0,
                                            page_size=1000
                                        ),
                                    ],
                                    className="four columns"
                                ),
                ################## Disabling tickbox as we have manual(no list comprihenson) traces in function
#                     html.Div([
#                         dcc.Checklist(id='piedropdown',
#                         options=[
#                         {'label': 'Cases', 'value': 'cases'},
#                          {'label': 'Deaths', 'value': 'deaths'},
#                          {'label': 'Recovering', 'value': 'recovering'}
#                             ,{'disabled':True}],
#                         value=['cases','deaths','recovering'],
#                         labelStyle={'display': 'inline-block'},
#                         style={
#                             'fontSize': 20,
#                          },

#                     )
#                 ],className='five columns'),


                html.Div([
                    dcc.Graph(id='lineChart'),
                        ],
                    className='seven columns')

            ], className="row",
            style={
                'marginBottom': 10,
                'textAlign': 'left',
                'color': colors['text'],
                'backgroundColor': colors['background']
            },
        ),


    html.Div([
                    dcc.RadioItems(id='radioButton',
                        options=[
                        {'label': 'Deaths', 'value': 'deaths'},
                            {'label': 'Confirmed', 'value': 'confirmed'}
                        ],
                        value='confirmed',
                        labelStyle={'display': 'inline-block'},
                            style={
                            'fontSize': 12,
                             },

                        )
                ],className='twelve columns'
            ),

 ########## Table
    html.Div([



                    html.Div([
                            dcc.Graph(id='scatterPlot'),
                                    ],className='six columns'),

                    html.Div([

                    html.Iframe(id='map-graph',srcDoc = open('abc.html','r').read(),width = '100%',height = '350'),
                        ],
                    className='six columns')





    ],className='row'),





])

###########function for Worldmap

world_map = folium.Map(location=[11,0], tiles="cartodbpositron", zoom_start=1.5, max_zoom = 5, min_zoom = 1.0)


for i in range(0,len(confirmed_df)):
    folium.Circle(
        location=[confirmed_df.iloc[i]['lat'], confirmed_df.iloc[i]['long']],
        fill=True,
        radius=(int((np.log(confirmed_df.iloc[i,-1]+1.00001)))+0.2)*50000,
        color='red',
        fill_color='indigo',
        tooltip = "<div style='margin: 0; background-color: black; color: white;'>"+
                    "<h4 style='text-align:center;font-weight: bold'>"+confirmed_df.iloc[i]['country'] + "</h4>"
                    "<hr style='margin:10px;color: white;'>"+
                    "<ul style='color: white;;list-style-type:circle;align-item:left;padding-left:20px;padding-right:20px'>"+
                        "<li>Confirmed: "+str(confirmed_df.iloc[i,-1])+"</li>"+
                        "<li>Deaths:   "+str(death_df.iloc[i,-1])+"</li>"+
                        "<li>Death Rate: "+ str(np.round(death_df.iloc[i,-1]/(confirmed_df.iloc[i,-1]+1.00001)*100,2))+ "</li>"+
                    "</ul></div>",
        ).add_to(world_map)

world_map

location_map = world_map
location_map.save('abc.html')
#------------------------------------------------------------------
#dummy function to invoke table sorting
#
# @dash_app.callback(
#         Output('dummy_table','children'),
#     [Input('datatable_id','data_timestamp')]
#
# )

def dummy_fx(timestamp):
    pass

@dash_app.callback(
    [
        Output('scatterPlot', 'figure'),
        Output('lineChart', 'figure')
     ],
    [Input('datatable_id', 'selected_rows'),
     #Input('piedropdown', 'value'),
     Input('radioButton', 'value')]
)



def update_data(chosen_rows,radioVal):
    if len(chosen_rows)==0:
        df_filterd = country_dff[country_dff['country'].isin(['Australia'])]
        #print(df_filterd)
    else:

        df_filterd = country_dff[country_dff.index.isin(chosen_rows)]


        #extract list of chosen countries
    list_chosen_countries=df_filterd['country'].tolist()
    #filter original df according to chosen countries
    #because original df has all the complete dates
    df_confirmed = confirmed_df[confirmed_df['country'].isin(list_chosen_countries)]
    df_death = death_df[death_df['country'].isin(list_chosen_countries)]
    df_recovered = recovered_df[recovered_df['country'].isin(list_chosen_countries)]

##################### ScatterPlot ######################3

    scatter_chart = px.scatter(
            sorted_country_dff.head(10),
            x='country',
            y=sorted_country_dff[radioVal].head(10),
            size = sorted_country_dff[radioVal].head(10),
            color='country',
            hover_name='country',
            size_max=40
            )
    layout = go.Layout()
    figure1 = go.Figure(data=scatter_chart,layout=layout)
    figure1.update_layout(

        font=dict(
            family="Courier New, monospace",
            size=12,
            color=colors['figure_text'],
        ),
        legend=dict(
            x=1,
            y=1,
            traceorder="normal",
            font=dict(
                family="sans-serif",
                size=12,
                color=colors['figure_text']
            ),
            bgcolor=colors['background'],
            borderwidth=2
        ),
        paper_bgcolor=colors['background'],
        plot_bgcolor=colors['background'],
        margin=dict(l=0,
                    r=0,
                    t=0,
                    b=0
                    ),
        height=350,

    )
    figure1.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#3A3A3A')
    figure1.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#3A3A3A')

    figure1.update_yaxes(zeroline=True, zerolinewidth=2, zerolinecolor='#3A3A3A')


    ############# Line Chart ###################

    trace1 = go.Scatter(x=np.array(list(df_confirmed.iloc[:,5:].columns)), y= np.sum(np.asarray(df_confirmed.iloc[:,5:]),axis = 0),
                            name='Confirmed',
                            marker_color='Orange'
                            )
    trace2 = go.Scatter(x=np.array(list(df_death.iloc[:,5:].columns)), y= np.sum(np.asarray(df_death.iloc[:,5:]),axis = 0),
                            name='Deceased',
                            marker_color='#FF3333'
                            )
    trace3 = go.Scatter(x=np.array(list(df_recovered.iloc[:,5:].columns)), y= np.sum(np.asarray(df_recovered.iloc[:,5:]),axis = 0),
                            name='Recovered',
                            marker_color='#33FF51'
                            )
    data1 = [trace1,trace2,trace3]
    #working code for for loop

#     traces = []
#     for tic in piedropval:

#         dfp=df_filterd
#         traces.append({'x':dfp['countriesAndTerritories'],'y':dfp[tic],'type':'bar'})
#     print(traces)
#     data1 = traces

    layout = go.Layout( title={
        'text': df_filterd['country'].iloc[0],
        'y':1,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})#df_filterd.iloc[0,0]))
    figure2 = go.Figure(data=data1,layout=layout)
    figure2.update_layout(
        hovermode='x',
        font=dict(
            family="Courier New, monospace",
            size=10,
            color=colors['figure_text'],
        ),
        legend=dict(
            x=0.1,
            y=1,
            traceorder="normal",
            font=dict(
                family="sans-serif",
                size=12,
                color=colors['figure_text']
            ),
            bgcolor=colors['background'],
            borderwidth=2
        ),
        paper_bgcolor=colors['background'],
        plot_bgcolor=colors['background'],
        margin=dict(l=0,
                    r=0,
                    t=0,
                    b=0
                    ),
        height=350,

    )
    figure2.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#3A3A3A')
    figure2.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#3A3A3A')




    return (figure1,figure2)



if __name__ == '__main__':
    dash_app.run_server()

