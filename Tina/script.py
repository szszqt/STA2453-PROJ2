import pandas as pd
import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

percent = pd.read_csv('./data/percent_sector.csv')
SNP = pd.read_csv('./data/SNP.csv')
vaccine_stock = pd.read_csv('./data/vaccine_stock.csv')

# Dash
sectors = {'SPY': 'S&P500', 'XLK': 'Information Technology', 'XLY': 'Consumer Discretionary', 'XLB': 'Materials',
           'XLC': 'Communication Services', 'XLV': 'Health Care', 'XLI': 'Industrials', 'XLP': 'Consumer Staples', 
           'XLF': 'Financial Services', 'XLU': 'Utilities', 'XLRE': 'Real Estate', 'XLE': 'Energy'}
vaccines = {'AZN': 'AstraZeneca', 'PFE': 'Pfizer', 'JNJ': 'Johnson & Johnson', 'MRNA': 'Moderna', 'NVAX': 'Novavax'}

tab2txt = "This tab shows some financial and economical indicators under the impact of COVID-19. You can monitor " \
            "some key economic indicator such as GDP, Unemployment Rate. In the next section, the stock market trend of different " \
            "sectors is displayed. Also, the treemaps illustrate the change more directly."

tab3txt = "This tab focuses on some attributes related to COVID-19 vaccines. Firstly, graphs of stock prices of vaccine companies "\
            "are plotted. Then a barchart summarizes the total number of doses ordered from each vaccine company. "\
            "Lastly, the order distribution by country is generated."


card1a = dbc.Card([
    dbc.CardBody([
        html.P("In the graph, the time for the 3 financial stimulus is displayed.\n"\
               "Phase 1: Coronavirus Preparedness and Response Supplemental Appropriations Act;\n"\
               "Phase 2: Families First Coronavirus Response Act;\n"\
               "Phase 3: CARES Act;\n"\
               "Phase 3.5: Paycheck Protection Program and Health Care Enhancement Act.",
               className="card-text"),
        html.P("Overall, roughly $2.59 trillion in new budgetary resources have been made to respond to the pandemic."\
               " It could be noticed that, the financial stimulus are released at the trough of the stock market. "\
               "After supporting the public with cash and tax reduction, the stock market has recovered and exceeded the pre-pandemic values.",
               className="card-text")
    ])
],
    color="primary",   # primary
    inverse=True,   # change color of text (black or white)
    outline=False, 
)


card1b = dbc.Card([
    dbc.CardBody([
        html.P("The graph on the left displays change in market values from 2020-01-01 to 2020-12-31 by industries, "\
               "and the graph on the right shows the change between the highest value during first quarter of 2020 and "\
               "the lowest value.",
               className="card-text"),
        html.P("It could be noticed that, with the highest proportion among all sectors, Information Technology has contributed "\
               "the greatest increase (27.5%) in stock values over the past year, where the Energy sector decreased 37%. "\
               "During pandemic, all sectors have incurred losses in value, with the most drop in Energy Sector (down by 61%), "\
               "and least impact in Consumer Staples (-25%) and Health Care (-29%).",
               className="card-text")
    ])
],
    color="primary",   # primary
    inverse=True,   # change color of text (black or white)
    outline=False, 
)


card2a = dbc.Card([
    dbc.CardBody([
        html.P("The top companies that are involved in COVID-19 vaccine development are: AstraZeneca, which co-operates with Oxford "\
               "University; Pfizer; Johnson & Johnson, which only requires one dose of injection; Moderna; and Novavax. "
               "Each vaccine has a different experiment timeline, and hence a much different stock price trend. ",
               className="card-text"),
        html.P("Some key events that might have driven the stock price is marked on the graph. It could be noticed that, "\
               "the positive news released could pull the stock price up, but only temporarily. The overall stock price also "\
               "depends on other factors of the company; for example, financial statements and other revenue streams.",
               className="card-text")
    ])
],
    color="primary",   # primary
    inverse=True,   # change color of text (black or white)
    outline=False, 
)

card2b = dbc.Card([
    dbc.CardBody([
        html.P("From the bar chart, it could be clearly viewed that AstraZeneca is current leading in the COVID-19 vaccine market, "\
               "with over 2.7B of doses ordered by different countries. And it is followed by vaccine produced by other research labs "\
               "and companies, including some in India, Russia and China. Note that the orders are mostly pre-order, meaning that "\
               "the vaccines might not be produced and ready for use yet.",
               className="card-text"),
        html.P("As shown on the map, US and India has ordered the most vaccines, followed by UK and Canada. "\
               "Except for the countries listed, also the organization, which is not displayed on the graph",
               className="card-text")
    ])
],
    color="primary",   # primary
    inverse=True,   # change color of text (black or white)
    outline=False, 
)


def get_stock(tab):
    if tab == 'finance':
        opts = [{'label': s, 'value': v} for v, s in sectors.items()]
        val = 'SPY'
    elif tab == 'vaccine':
        opts = [{'label': s, 'value': v} for v, s in vaccines.items()]
        val = 'AZN'
    return html.Div([
        dcc.Dropdown(id=tab+'_stock_dropdown', options=opts, value=val),
        dcc.Graph(id=tab+'_stock_graph')
    ])

def get_treemaps():
    return html.Div([
        html.Div(get_treemap('yoy'),
                 style={'width':'50%','display': 'inline-block',
                        'vertical-align':'top'}),
        html.Div(get_treemap('covid'),
                 style={'width':'50%','display': 'inline-block',
                        'vertical-align':'top'})
    ])

def get_treemap(s):
    if s == 'yoy':
        col = 'change_yoy'
        txt = "YoY change%"
    elif s == 'covid':
        col = 'drop_covid'
        txt = "COVID-19 impact%"
        
    fig = px.treemap(percent, path=['Sector'], values='Percent',
                     color=col, color_continuous_scale=["red","green"], range_color=[-0.8,0.8])
    fig.update_layout(title=txt,
                     margin=dict(l=10,r=10,t=60,b=60))
    
    return html.Div([
        dcc.Graph(figure=fig)
    ])

def get_map():
    fig = px.scatter_geo(vaccine_country, locations="country", locationmode = 'country names',
                         hover_name="country", size="doses", #color='lightslategray',
                         projection="natural earth")
    fig.update_layout(title="Vaccine Orders by Country",
                     margin=dict(l=10,r=20,t=60,b=60))
    fig.update_traces(marker_color='lightslategray')
    return html.Div([
        dcc.Graph(figure=fig)
    ])

def get_bar():
    fig = px.bar(vaccine_brand, x='brand', y='doses')
    fig.update_layout(title="Vaccine Orders by Company",
                     margin=dict(l=0,r=20,t=60,b=60))
    fig.update_traces(marker_color='lightslategray')
    return html.Div([
        dcc.Graph(figure=fig)
    ])


# Dash set up
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
app.title = 'Covid-19 Socioeconomic Dashboard'

# Base Layout
app.layout = html.Div([
    dbc.Row(html.Br(), style={'background-color':'#000000'}),
    dbc.Row([
        dbc.Col(
            html.H1(children='COVID-19 Socioeconomic Dashboard',
                    style={'textAlign': 'center', 'color':'#FFFFFF'}),md=12)],
        align="center", style={'margin':'auto', 'background-color':'#000000'}),
    dbc.Row(html.Br(), style={'background-color':'#000000'}),
    dcc.Tabs(id='dashboard-tabs', value='finance-tab',children=[
        # Tab 1: social factors
        #dcc.Tab(label='Social Factors', value='social-tab',children=[
            # div 1: number of death
        #]),
        # Tab 2: financial / economic factors
        dcc.Tab(label='Financial / Economic Factors', value='finance-tab',children=[
            # div 1: summary statistics: unemployement rate, GDP
            # div 2: stock prices line graph
            html.Br(),
            html.Div([html.P(tab2txt)], style={'width':'90%','margin':'auto'}),
            html.H3("Stock Maket Trend by Sector, 2019 Jan - 2020 Dec", style={'textAlign': 'center'}),
            dbc.Row(html.Br(), style={'background-color':'#000000'}),
            html.Div(
                dbc.Row([dbc.Col(card1a, width=3),
                         dbc.Col(get_stock('finance'), width=9)],justify="around",)
                ,style={'width':'100%','margin':'auto'}),
            # div 3: Sector Treemap
            html.Br(),
            html.H3("Treemaps by Sector, YoY% vs. COVID-19 Impact%", style={'textAlign': 'center'}),
            dbc.Row(html.Br(), style={'background-color':'#000000'}),
            html.Div(
                dbc.Row([dbc.Col(card1b, width=3),
                         dbc.Col(get_treemaps(), width=9)])
                ,style={'width':'100%','margin':'auto'})
        ]),
        # Tab 3: vaccine information
        dcc.Tab(label='Vaccine Information', value='vaccine-tab',children=[
            html.Br(),
            html.Div([html.P(tab3txt)], style={'width':'90%','margin':'auto'}),
            html.H3("Vaccine Company Stock Price, 2019 Jan - 2020 Dec", style={'textAlign': 'center'}),
            dbc.Row(html.Br(), style={'background-color':'#000000'}),
            # div 1: vaccine stock price line graphs
            html.Div(
                dbc.Row([dbc.Col(card2a, width=3),
                         dbc.Col(get_stock('vaccine'), width=9)]),
                style={'width':'100%','margin':'auto'}),
            # div 2: vaccine distribution bar
            html.Br(),
            html.H3("Vaccine Orders Summary & by Country", style={'textAlign': 'center'}),
            dbc.Row(html.Br(), style={'background-color':'#000000'}),
            html.Div(
                dbc.Row([dbc.Col(card2b, width=3),
                         dbc.Col(get_bar(), width=3),
                         dbc.Col(get_map(), width=6)]),style={'width':'100%','margin':'auto'}),
            # div 3: vaccine distribution map
        ])
    ])
])


@app.callback(
    Output('finance_stock_graph', 'figure'),
    Input('finance_stock_dropdown', 'value'))
def update_figure(stock):
    mydf = SNP
    df = mydf.loc[mydf['symbol'] == stock]

    fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'])
                     ])
    
    fig.update_layout(
    margin=dict(l=10,r=20,t=20,b=60),
    yaxis_title='Stock Price',
    shapes = [dict(x0='2020-03-06', x1='2020-03-06', y0=0, y1=1, xref='x', yref='paper', line_width=2),
              dict(x0='2020-03-18', x1='2020-03-18', y0=0, y1=1, xref='x', yref='paper', line_width=2),
              dict(x0='2020-03-27', x1='2020-03-27', y0=0, y1=1, xref='x', yref='paper', line_width=2),
              dict(x0='2020-04-24', x1='2020-04-24', y0=0, y1=1, xref='x', yref='paper', line_width=2)],
    annotations=[dict(x='2020-03-06', y=0.95, xref='x', yref='paper', showarrow=False, xanchor='left', text='Phase 1', textangle=-90),
                 dict(x='2020-03-18', y=0.95, xref='x', yref='paper', showarrow=False, xanchor='left', text='Phase 2', textangle=-90),
                 dict(x='2020-03-27', y=0.95, xref='x', yref='paper', showarrow=False, xanchor='left', text='Phase 3', textangle=-90),
                 dict(x='2020-04-24', y=0.95, xref='x', yref='paper', showarrow=False, xanchor='left', text='Phase 3.5', textangle=-90)]
    )

    return fig

@app.callback(
    Output('vaccine_stock_graph', 'figure'),
    Input('vaccine_stock_dropdown', 'value'))
def update_figure(stock):
    mydf = vaccine_stock
    df = mydf.loc[mydf['symbol'] == stock]

    fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'])
                     ])
    if stock == 'PFE':
        fig.update_layout(
            margin=dict(l=10,r=20,t=20,b=60),
            yaxis_title='Stock Price',
            shapes = [dict(x0='2020-12-08', x1='2020-12-08', y0=0, y1=1, xref='x', yref='paper', line_width=2)],
            annotations=[dict(x='2020-12-08', y=0.95, xref='x', yref='paper', showarrow=False, xanchor='left', 
                              text='Released data, 95% effective', textangle=-90)]
        )
    elif stock == 'AZN':
        fig.update_layout(
            margin=dict(l=10,r=20,t=20,b=60),
            yaxis_title='Stock Price',
            shapes = [dict(x0='2020-07-20', x1='2020-07-20', y0=0, y1=1, xref='x', yref='paper', line_width=2)],
            annotations=[dict(x='2020-07-20', y=0.95, xref='x', yref='paper', showarrow=False, xanchor='left', 
                              text='Released data, 100% effective', textangle=-90)]
        )
    elif stock == 'MRNA':
        fig.update_layout(
            margin=dict(l=10,r=20,t=20,b=60),
            yaxis_title='Stock Price',
            shapes = [dict(x0='2020-11-30', x1='2020-11-30', y0=0, y1=1, xref='x', yref='paper', line_width=2)],
            annotations=[dict(x='2020-11-30', y=0.95, xref='x', yref='paper', showarrow=False, xanchor='left', 
                              text='Released data, 94% effective', textangle=-90)]
        )
    else:
        fig.update_layout(
            margin=dict(l=10,r=20,t=20,b=60),
            yaxis_title='Stock Price')

    return fig



if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False, port=8000)