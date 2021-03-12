import pandas as pd
import time
import plotly.graph_objs as go
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from scipy import signal
import numpy as np 
import datetime
import pandas_datareader.data as web
import matplotlib.pyplot as plt
from scipy.stats.stats import pearsonr 
from collections import Counter
from calendar import month_abbr
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.tsa.stattools import acf, ccf

# Import data
percent = pd.read_csv('./../data/clean/percent_sector.csv')
SNP = pd.read_csv('./../data/clean/SNP.csv')
vaccine_stock = pd.read_csv('./../data/clean/vaccine_stock.csv')
vaccine_brand = pd.read_csv('./../data/clean/vaccine_brand.csv')
vaccine_country = pd.read_csv('./../data/clean/vaccine_country.csv')
gdp = pd.read_csv('./../data/clean/GDP.csv')
mb = pd.read_csv('./../data/clean/monetary_base.csv')
interest = pd.read_csv('./../data/clean/FRED-IR3MTBIlL.csv')
yields = pd.read_csv('./../data/clean/USTREASURY-YIELD.csv')

mask = (interest.Date > '2019-1-1 01:00:00')
interest = interest.loc[mask]
mask = (yields.Date > '2019-1-1 01:00:00')
yields = yields.loc[mask]

features = pd.read_csv('./../data/clean/features.csv')
policies = pd.read_csv('./../data/clean/policies.csv')
features.date = features.date.apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'))
policies.date = policies.date.apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'))

list_states = list(features['state'].unique())
list_features = list(features.columns)
list_features.remove('date')
list_features.remove('state')
list_policies = policies['policy_type'].unique()

list_industries = ['Airline', 'Hotel', 'IT', 'Entertainment']
national_data = features.groupby('date').sum()

start_date = features['date'].min()
end_date = features['date'].max()

stock_store = []

during_start_date = '2020-04-01'
during_stop_date = '2020-08-31'
post_start_date = '2020-09-01'
post_stop_date = '2021-01-14'

airline_stocks = ['DAL', 'AAL', 'UAL', 'LUV']
it_stocks = ['MSFT', 'AMZN', 'ZM', 'GOOGL']
hotel_stocks = ['H', 'MAR', 'HLT', 'WH']
entertainment_stocks = ['NFLX', 'DIS', 'VIAC', 'DISCA']

sectors = {'SPY': 'S&P500', 'XLK': 'Information Technology', 'XLY': 'Consumer Discretionary', 'XLB': 'Materials',
           'XLC': 'Communication Services', 'XLV': 'Health Care', 'XLI': 'Industrials', 'XLP': 'Consumer Staples', 
           'XLF': 'Financial Services', 'XLU': 'Utilities', 'XLRE': 'Real Estate', 'XLE': 'Energy'}
vaccines = {'AZN': 'AstraZeneca', 'PFE': 'Pfizer', 'JNJ': 'Johnson & Johnson', 'MRNA': 'Moderna', 'NVAX': 'Novavax'}
indicators = {'GDP': 'Gross Domestic Product', 'MB': 'Monetary Base', '3MTBILL': '3-Month Interest Rate', 
              '1MOYLD': '1-Month Bond Yield', '6MOYLD': '6-Month Bond Yield', '1YRYLD': '1-Year Bond Yield', 
             '5YRYLD': '5-Year Bond Yield'}

# Tabs with html text description of our visualizations
tab2txt = "This tab shows some financial and economical indicators under the impact of COVID-19. You can monitor " \
            "some key economic indicator such as GDP, Unemployment Rate. In the next section, the stock market trend of different " \
            "sectors is displayed. Also, the treemaps illustrate the change more directly."

tab3txt = "This tab focuses on some attributes related to COVID-19 vaccines. Firstly, graphs of stock prices of vaccine companies "\
            "are plotted. Then a barchart summarizes the total number of doses ordered from each vaccine company. "\
            "Lastly, the order distribution by country is generated."

tab4txt = '''This tab shows information on various policies that were implemented to curb COVID 19. 
                We look at when the policies were implemented, the change in deaths-per-day as a result, and finally the
                effect of these policies on various industries.'''


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
        html.P("The graph displays changes in economic indicators from 2020-01-01 to 2020-12-31. " \
               "Notice that there is a major dip in GDP in January 2020, the start of COVID, up until April. The " \
               "economy slowly recovers after April.",
               className="card-text"),
        html.P("Long term and short term interest rates are also high in January till March, but sharply drop down " \
               "near zero in April as the government tried to stimulate the economy. These rates have been kept low" \
               "throughout the rest of the year, with slight fluctuations. There is not a huge difference between " \
               "long and short term rates.",
               className="card-text"),
        html.P("Monetary base is expanding over time as the government is printing money, causing an increase in" \
               "reserve holdings at banks.",
               className="card-text")
    ])
],
    color="primary",   # primary
    inverse=True,   # change color of text (black or white)
    outline=False, 
)



card1c = dbc.Card([
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



card1d = dbc.Card([
    dbc.CardBody([
        html.P("The heatmap on the left displays correlations between stock indexes and particular economic indicators. "\
               "A positive correlation implies that a positive change in an indicator would result in a positive change in "\
               "a stock price. The S&P500 is very positively correlated with GDP (r = 0.81), while information services "\
               "index is less correlated.",
               className="card-text"),
        html.P("The graph on the right is a cross-correlation plot, which can help you determine whether a particular "\
               "economic indicator is leading or lagging when its being used to forecast a particular stock price. "\
               "For instance, GDP is lagging, along with interest rates.",
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

card3a = dbc.Card([
    dbc.CardBody([
        html.P('''For our study we selected 10 major categories of policies. They are as follows: 
        1.Manufacturing 2.Entertainment 3.Non-essential Businesses 4.Outdoor and Recreation 5.Shelter in place 6.Travel 7.Phase1 8.Phase2 9.Phase3 and 10.Phase4.
        ''',
               className="card-text"),
        html.P('''Shelter in place is the first policy to be implemented in all states (end of March - start of April). 
        This is followed by Phase 1 (end of April - start of May). Phase 2 is implimented throughout a large time span (some 
        states start at the end of March, most states start mid-May and some states go as late as end of July). Some states 
        implement Phase 3 from May, most implement from June while Connecticut is on October. Only few states like Indiana and Illinois opt 
        for Phase 4 of lockdowns. Policies dealing with reopening like Manufacturing, entertainment, Non-essential businesses, and outdoor activities
        are implemented starting April. Finally policies dealing with travel restricitons were implemented all
        throughout 2020.''',
               className="card-text")
    ])
],
    color="primary",   # primary
    inverse=True,   # change color of text (black or white)
    outline=False, 
)

card3b = dbc.Card([
    dbc.CardBody([
        html.P('''
            This section and the next analyzes the effect of these policies on 4 industries - Airline, Hotel, Entertainment and IT. 
            For each industry, we consider the top 4 performing stocks for our study. 
            More than 90% of the policies considered above were implemented between April and September. So, we compare the performance
            of these stocks as 1. During Policy (April, 2020 - September, 2020) and 2. After Policy (September, 2020 - January, 2021).
        ''', className="card-text"),
        
        html.P('''
        The plots on the left represent the autocorrelation of stocks; the x axis represents time-lags in days, while the y axis represents correlation values.
        Higher autocorrelation implies greater predictability in stock prices, thus aiding investors.''', className='card-text'),
        
        html.P('''In the case of the major airline companies, the autocorrelation after the policies ceased were higher than
        the autocorrelation when the policies were in palce. The hotel industry follows the same trend as the major airline companies as the autocorrelation is higher 
        after the policies were eased. On the contrary, for the major IT companies, the stocks had higher predictability when policies were in place.
        Finally, for the entertainment industry, all companies except Netflix had a higher autocorrelation after the policies were lifted.''',
               className="card-text"),
    ])
],
    color="primary",   # primary
    inverse=True,   # change color of text (black or white)
    outline=False, 
)

card3c = dbc.Card([
    dbc.CardBody([
        html.P('''This section compares the mean-High, mean-Close and the Return Rate of the companies during the time 
        policies were in place and after the time the policies ceased. Similar to the previous section, the top 4 
        performing stocks/companies in each industry were taken representative of their respective industries.''',
               className="card-text"),
        html.P('''The top 4 airline companies in the US had a higher mean-close and a higher mean-high after policies were stopped. 
        All of them with the exception of United Airlines had a lower return rate when the policies were in place. 
        Similarly, the major hotel chains in the US had higher mean-close and higher mean-high after the policies ceased. 
        However, they had a higher return rate during the time policies were implemented. 
        The same trend follows for the 4 major IT giants in the US. All the major entertainment companies had a higher mean-high and a higher mean-close after policies were lifted.
        Netflix, Disney and Viacom had higher return rates when policies were in place.
        ''', className='card-text')
    ])
],
    color="primary",   # primary
    inverse=True,   # change color of text (black or white)
    outline=False, 
)

def get_filtered_stats(state_abbr, feature):
	filter_state = features[features['state']==state_abbr]
	filter_features = filter_state[feature]
	filter_dates = filter_state['date']
	return filter_features, filter_dates

# function that returns the start_dates and stop_dates and the comments of a particular policy was implemented for a query state
def get_filtered_policies(state_abbr, policy):
	filter_state = policies[policies['state']==state_abbr]
	filter_policies = filter_state[filter_state['policy_type']==policy]

	start_policies = filter_policies[filter_policies['start_stop']=='start']
	start_policies_desc = start_policies['comments']
	stop_policies = filter_policies[filter_policies['start_stop']=='stop']
	stop_policies_desc = stop_policies['comments']
	start_dates = start_policies['date']
	stop_dates = stop_policies['date']
	return list(start_dates), list(start_policies_desc), list(stop_dates), list(stop_policies_desc)

# function that returns dataframe of stock prices given the stock_abbrev, start_date and end_date
def fetch_stock(stock_abbrev, start_date, end_date):
	df = web.DataReader(stock_abbrev, 'yahoo', start_date, end_date)
	df.reset_index(inplace=True)
	df.set_index("Date", inplace=True)
	return df

# function that merges 2 dataframes
def merge_dfs(df, national_data):
	if len(df.index) <= len(national_data.index):
		merged = df.merge(national_data, how='inner', left_on=df.index, right_on=national_data.index)
	else:
		merged = national_data.merge(df, how='inner', left_on=national_data.index, right_on=df.index)
	merged = merged.rename(columns={'key_0': 'date'})
	merged = merged.set_index('date')
	return merged

# function to get the months in which a particular type of policy was started and stopped 
def get_policy_month(policy_type):
	start_month_list = []
	policy_start_df = policies[policies['policy_type']==policy_type]
	policy_start_df = policy_start_df[policy_start_df['start_stop']=='start']
	start_dates = list(policy_start_df['date'])
	for dt in start_dates:
		start_month_list.append(dt.month)
	return Counter(start_month_list)

policy_month_store = {}
for policy_type in list_policies:
	policy_month_store[policy_type] = dict(get_policy_month(policy_type))

# function to prettify the format for printing the policy months frwquencies
def pretty_print(policy_month_store, policy_type):
	month_names = [month_abbr[i] for i in range(13)]
	month_names.remove('')
	temp = policy_month_store[policy_type]
	sreturn = ''
	for i in list(temp.keys()):
		mname = month_names[i-1]
		val = temp[i]
		sreturn = sreturn + str(mname) + ' : ' + str(val) + ' | '
	return sreturn

# function that take a dataframe of stock prices and returns only the observations between 2 dates
def compare_stock(stock):
	during_policy = stock.loc[during_start_date : during_stop_date]
	post_policy = stock.loc[post_start_date : post_stop_date]
	mean_close_during = round(during_policy['Close'].mean(), 2)
	mean_close_post = round(post_policy['Close'].mean(), 2)
	mean_high_during = round(during_policy['High'].mean(), 2)
	mean_high_post = round(post_policy['High'].mean(), 2)
	during_return_rate = round((during_policy.loc['2020-08-31']['Close'] - during_policy.loc['2020-04-01']['Close'])/during_policy.loc['2020-04-01']['Close'], 3)
	post_return_rate = round((post_policy.loc['2021-01-14']['Close'] - post_policy.loc['2020-09-01']['Close'])/post_policy.loc['2020-09-01']['Close'], 3)
	return mean_close_during, mean_close_post, mean_high_during, mean_high_post, during_return_rate, post_return_rate

# function to compare effect of policies on stock
def get_stock_report(store_stocks, start_date, end_date):
    all_during_mean_close = []
    all_post_mean_close = []
    all_during_mean_high = []
    all_post_mean_high = []
    all_during_return_rate = []
    all_post_return_rate = []

    for astock in store_stocks:
        adf = fetch_stock(astock, start_date, end_date)
        merged = merge_dfs(adf, national_data)
        mean_close_during, mean_close_post, mean_high_during, mean_high_post, during_return_rate, post_return_rate = compare_stock(adf)
        all_during_mean_close.append(mean_close_during)
        all_post_mean_close.append(mean_close_post)
        all_during_mean_high.append(mean_high_during)
        all_post_mean_high.append(mean_high_post)
        all_during_return_rate.append(during_return_rate)
        all_post_return_rate.append(post_return_rate)
    return all_during_mean_close, all_post_mean_close, all_during_mean_high, all_post_mean_high, all_during_return_rate, all_post_return_rate

def get_autocorrelation_graph(stock_abbrev):
    time.sleep(1)
    during_df = fetch_stock(stock_abbrev, during_start_date, during_stop_date)
    during_df.reset_index(inplace=True)
    during_df.set_index("Date", inplace=True)
    after_df = fetch_stock(stock_abbrev, post_start_date, post_stop_date)
    after_df.reset_index(inplace=True)
    after_df.set_index("Date", inplace=True)
    during_close, after_close = during_df['Close'], after_df['Close']
    during_corr_vals = acf(during_close)
    after_corr_vals = acf(after_close)
    during_corr_fig = go.Figure(data=[go.Bar(x=list(range(len(during_corr_vals))), y=during_corr_vals, width=0.1, marker_color='crimson')])
    during_corr_fig.update_layout(title="Autocorrelation during Policy", title_x=0.5, xaxis_title="Lag", yaxis_title="ACF")
    after_corr_fig = go.Figure(data=[go.Bar(x=list(range(len(after_corr_vals))), y=after_corr_vals, width=0.1, marker_color='crimson')])
    after_corr_fig.update_layout(title="Autocorrelation after Policy", title_x=0.5, xaxis_title="Lag", yaxis_title="ACF")
    return during_corr_fig, after_corr_fig
 
 # Function that gets stock candle graph information
def get_stock(tab):
    if tab == 'finance':
        opts = [{'label': s, 'value': v} for v, s in sectors.items()]
        val = 'SPY'
    elif tab == 'vaccine':
        opts = [{'label': s, 'value': v} for v, s in vaccines.items()]
        val = 'AZN'
    return html.Div([
        dcc.Dropdown(id=tab+'_stock_dropdown', options=opts, value=val, style={"margin-top": "15px"}),
        dcc.Graph(id=tab+'_stock_graph')
    ])

# Get economic indicator values
def get_economic_indicator():
    opts = [{'label': s, 'value': v} for v, s in indicators.items()]
    val = '1MOYLD'
    return html.Div([
        dcc.Dropdown(id='economic_indicator_dropdown', options=opts, value=val, style={"margin-top": "15px"}),
        dcc.Graph(id='economic_indicator_graph')
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
                     margin=dict(l=10,r=10,t=60,b=60), title_x=0.5)
    
    return html.Div([
        dcc.Graph(figure=fig)
    ])

def get_correlation_heatmap():
    opts1 = [{'label': s, 'value': v} for v, s in sectors.items()]
    val1 = ['SPY', 'XLK']
    opts2 = [{'label': s, 'value': v} for v, s in indicators.items()]
    val2 = ['GDP', '1MOYLD']
    return html.Div([
        dcc.Dropdown(id='stock_corr_dropdown', options=opts1, value=val1, multi=True, style={"margin-top": "15px"}),
        dcc.Dropdown(id='indicator_corr_dropdown', options=opts2, value=val2, multi=True, style={"margin-top": "15px"}),
        dcc.Graph(id='correlation_matrix')
    ])

def get_autocorrelation():
    opts1 = [{'label': s, 'value': v} for v, s in sectors.items()]
    val1 = 'SPY'
    opts2 = [{'label': s, 'value': v} for v, s in indicators.items()]
    val2 = 'MB'
    return html.Div([
        dcc.Dropdown(id='stock_acf_dropdown', options=opts1, value=val1, style={"margin-top": "15px"}),
        dcc.Dropdown(id='indicator_acf_dropdown', options=opts2, value=val2, style={"margin-top": "15px"}),
        dcc.Graph(id='acf_graph')
    ])

def get_map():
    fig = px.scatter_geo(vaccine_country, locations="country", locationmode = 'country names',
                         hover_name="country", size="doses", #color='lightslategray',
                         projection="natural earth")
    fig.update_layout(title="Vaccine Orders by Country",
                     margin=dict(l=10,r=20,t=60,b=60), title_x=0.5)
    fig.update_traces(marker_color='lightslategray')
    return html.Div([
        dcc.Graph(figure=fig)
    ])

def get_bar():
    fig = px.bar(vaccine_brand, x='brand', y='doses')
    fig.update_layout(title="Vaccine Orders by Company",
                     margin=dict(l=0,r=20,t=60,b=60), title_x=0.5)
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
            
            # div 3: economic indicators
            html.Br(),
            html.H3("Economic Indicators, 2019 Jan - 2020 Dec", style={'textAlign': 'center'}),
            dbc.Row(html.Br(), style={'background-color':'#000000'}),
            html.Div(
                dbc.Row([dbc.Col(card1b, width=3),
                         dbc.Col(get_economic_indicator(), width=9)],justify="around",)
                ,style={'width':'100%','margin':'auto'}),
            
            # div 4: Sector Treemap
            html.Br(),
            html.H3("Treemaps by Sector, YoY% vs. COVID-19 Impact%", style={'textAlign': 'center'}),
            dbc.Row(html.Br(), style={'background-color':'#000000'}),
            html.Div(
                dbc.Row([dbc.Col(card1c, width=3),
                         dbc.Col(get_treemaps(), width=9)])
                ,style={'width':'100%','margin':'auto'}),
            
            # div 5: Correlation Matrix
            html.Br(),
            html.H3("Correlation of Stock Prices and Economic Indicators", style={'textAlign': 'center'}),
            dbc.Row(html.Br(), style={'background-color':'#000000'}),
            html.Div(
                dbc.Row([dbc.Col(card1d, width=3), 
                         dbc.Col(get_correlation_heatmap(), width=4),
                         dbc.Col(get_autocorrelation(), width=4)])
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
        ]), # end of 3rd tab

        dcc.Tab(label='Policy Information', value='policy-tab',children=[
            html.Br(),
            html.Div([html.P(tab4txt)], style={'width':'90%','margin':'auto'}),
            html.H3("Policies implemented across different states along with different features", style={'textAlign': 'center'}),
            dbc.Row(html.Br(), style={'background-color':'#000000'}),
            # div 1
            html.Div([
                dbc.Row([dbc.Col(card3a, width=3),
                         dbc.Col(html.Div([
                                html.H4('Enter State:'),
                                dcc.Dropdown(id='state_abbrev', options=[{'label':s, 'value':s} for s in list_states], value='AZ'),

                                html.H4('Enter Statistic:', style={'margin-top':'20px'}),
                                dcc.Dropdown(id='feature', options=[{'label':s, 'value':s} for s in list_features], value='deathIncrease'),

                                html.H4('Enter Policy:', style={'margin-top':'20px'}),
                                dcc.Dropdown(id='policy', options=[{'label':s, 'value':s} for s in list_policies], value='phase 1'),
                                ], style={"width": "80%", 'margin-top':'20px'}), width=3),
                         dbc.Col(html.Div([
                                # dropdown menu to select states and features
                                # feature-policy graph
                                html.Div(
                                    children=[
                                html.Div(id='policy_graph', children=[]),
                                            ]),
                                    ]),width=6),
                        ]),
                                    
                        html.H2('Policy Information', style={'textAlign': 'center'}),
                        dbc.Row(html.Br(), style={'background-color':'#000000'}),    
                        dbc.Row([dbc.Col(html.Div(id='left_box', 
                                        children=[
                                        html.H3('Start of Policy', style={'margin-left':'300px', 'margin-top':'10px'}),
                                        html.Div(id='start_policy', children=[], style={'margin-left':'20px', 'margin-top':'10px'}),
                                                ])),
                                dbc.Col(       
                                         html.Div(id='right_box', 
                                                    children=[
                                                        html.H3('End of Policy',style={'margin-left':'300px', 'margin-top':'10px'}),
                                                        html.Div(id='stop_policy', children=[], style={'margin-right':'20px', 'margin-top':'10px'}),
                                                            ], style={'display': 'inline-block', "margin-left": "50px"})
                                                    
                                        )]
                               ),           
        ]), 
       
        html.Div([
            html.H2('Autocorrelation of stocks', style={'textAlign': 'center', 'margin-top':'30px'}),
            dbc.Row(html.Br(), style={'background-color':'#000000'}),
            dbc.Row([
                dbc.Col(card3b, width=3),
                dbc.Col([
                    dcc.Dropdown(id='show_corr_ind', options=[{'label':s, 'value':s} for s in list_industries], value='Airline', style={'margin-top':'20px', 'margin-right':'20px'}),
                    html.Div(id='autocorr_graph_plot_during', children=[])
                ]),
                dbc.Col([
                    dcc.Dropdown(id='show_corr_cpy', options=[{'label':s, 'value':s} for s in airline_stocks], value='DAL', style={'margin-top':'20px', 'margin-right':'20px'}),
                    html.Div(id='autocorr_graph_plot_after', children=[])
                ])
            ])
        ]),

           #div3
            html.Div([
            html.H2('Show effect of policies on different industries', style={'textAlign': 'center'}),
            dbc.Row(html.Br(), style={'background-color':'#000000', "margin-top": "20px"}),
            dbc.Row([
                dbc.Col(card3c, width=3),
                dbc.Col([
                        dbc.Row([
                            dbc.Col([
                                dcc.Dropdown(id='show_general', options=[{'label':s, 'value':s} for s in list_industries], value='Airline', style={'margin-top':'20px', 'margin-right':'20px'})
                            ])
                        ]),
                        dbc.Row([
                            
                            dbc.Col(
                                html.Div( 
                                        id='mean_close_graph', children=[]
                                        ), width=4
                                    ),
                            dbc.Col(
                                html.Div( 
                                        id='mean_high_graph', children=[]
                                        ), width=4
                                ),
                            dbc.Col(
                                html.Div( 
                                        id='return_rate_graph', children=[]
                                        ), width=4
                                    ),
                            ])
                    ])
                
                    ])
                        
        ])

    ])
    ])
]) 


@app.callback(
    [Output('show_corr_cpy', 'options'),
    Output('show_corr_cpy', 'value')
    ],
    Input('show_corr_ind', 'value')
)
def get_company_names(industry_type):
    if industry_type=='Airline':
        return [{'label':s, 'value':s} for s in airline_stocks], 'DAL'
    elif industry_type=='IT':
        return [{'label':s, 'value':s} for s in it_stocks], 'MSFT'
    elif industry_type=='Hotel':
        return [{'label':s, 'value':s} for s in hotel_stocks], 'H'
    elif industry_type=='Entertainment':
        return [{'label':s, 'value':s} for s in entertainment_stocks], 'NFLX'


@app.callback(
    [Output('autocorr_graph_plot_during', 'children'),
     Output('autocorr_graph_plot_after', 'children')
    ],
    Input('show_corr_cpy', 'value'))
def get_corr_graph(stock_abbrev):
    during_acr_plot, after_acr_plot = get_autocorrelation_graph(stock_abbrev)
    return dcc.Graph(id='autocorr_graph1', figure=during_acr_plot), dcc.Graph(id='autocorr_graph2', figure=after_acr_plot)
            
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
    Output('economic_indicator_graph', 'figure'),
    Input('economic_indicator_dropdown', 'value'))
def update_figure(indicator):
    if indicator == 'GDP':
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=gdp['Date'], y=gdp['Value'], mode='lines'))
        fig.update_layout(margin=dict(l=10,r=20,t=20,b=60), yaxis_title='GDP ($)')
    elif indicator == 'MB':
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=mb['Date'], y=mb['Value'], mode='lines'))
        fig.update_layout(margin=dict(l=10,r=20,t=20,b=60), yaxis_title='Monetary Base ($)')
    elif indicator == '3MTBILL':
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=interest['Date'], y=interest['Value'], mode='lines'))
        fig.update_layout(margin=dict(l=10,r=20,t=20,b=60), yaxis_title='Interest Rates (%)')
    else:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=yields['Date'], y=yields[indicator], mode='lines'))
        fig.update_layout(margin=dict(l=10,r=20,t=20,b=60), yaxis_title='Bond Yield (%)')
    return fig

@app.callback(
    Output('correlation_matrix', 'figure'),
    Input('stock_corr_dropdown', 'value'),
    Input('indicator_corr_dropdown', 'value')
)
def update_figure(stocks, indicators):
    if (type(stocks) != list):
        stocks_lst = [stocks]
    else:
        stocks_lst = stocks
    if (type(indicators) != list):
        indicators_lst = [indicators]
    else:
        indicators_lst = indicators
    
    len_stocks = len(stocks_lst)
    df_stocks = SNP.loc[SNP['symbol'] == stocks_lst[0]][['Date', 'Close']]
    name = stocks_lst[0] + ' (Close)'
    df_stocks = df_stocks.rename(columns={'Close': name})
    
    for i in range(1, len(stocks_lst)):
        df_stock = SNP.loc[SNP['symbol'] == stocks_lst[i]]
        name = stocks_lst[i] + ' (Close)'
        df_stock = df_stock.rename(columns={'Close': name})
        df_stocks = df_stocks.merge(df_stock[['Date', name]], on='Date')
    
    if indicators_lst[0] == 'GDP':
        df_indicators = gdp
        df_indicators = df_indicators.rename(columns={'Value': 'GDP'})
    elif indicators_lst[0] == 'MB':
        df_indicators = mb
        df_indicators = df_indicators.rename(columns={'Value': 'MB'})
    elif indicators_lst[0] == '3MTBILL':
        df_indicators = interest
        df_indicators = df_indicators.rename(columns={'Value': '3MTBILL'})
    else:
        name = indicators_lst[0]
        df_indicators = yields[['Date', name]]
    
    for i in range(1, len(indicators_lst)):
        if indicators_lst[i] == 'GDP':
            df_ind = gdp
            df_ind = df_ind.rename(columns={'Value': 'GDP'})
        elif indicators_lst[i] == 'MB':
            df_ind = mb
            df_ind = df_ind.rename(columns={'Value': 'MB'})
        elif indicators_lst[i] == '3MTBILL':
            df_ind = interest
            df_ind = df_ind.rename(columns={'Value': '3MTBILL'})
        else:
            name = indicators_lst[i]
            df_ind = yields[['Date', name]]
        df_indicators = df_indicators.merge(df_ind, on='Date')
    
    df_stocks = df_stocks.merge(df_indicators, on='Date')
    df_stocks = df_stocks.drop(['Date'], axis=1)
    corr = df_stocks.corr()
    fig = px.imshow(corr)
    fig.update_layout(title="Correlation Heatmap",
                     margin=dict(l=10,r=20,t=60,b=60), title_x=0.5)
    return fig

@app.callback(
    Output('acf_graph', 'figure'),
    Input('stock_acf_dropdown', 'value'),
    Input('indicator_acf_dropdown', 'value')
)
def update_figure(stock, indicator):
    df_stock = SNP.loc[SNP['symbol'] == stock][['Date', 'Close']]
    if indicator == 'GDP':
        df_ind = gdp
    elif indicator == 'MB':
        df_ind = mb
    elif indicator == '3MTBILL':
        df_ind = interest
    else:
        df_ind = yields[['Date', indicator]]
        df_ind = df_ind.rename(columns={indicator: 'Value'})
    
    df_stock = df_stock.merge(df_ind, on='Date')
    ccf_vals = ccf(df_stock['Close'], df_stock['Value'])
    fig = go.Figure(data=[go.Bar(x=list(range(len(ccf_vals))), y=ccf_vals, width=0.1, marker_color='crimson')])
    fig.update_layout(title="Cross-correlation of Stock Price and Indicator",
                     margin=dict(l=10,r=20,t=60,b=60), title_x=0.5, xaxis_title="Lag", yaxis_title="CCF")
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

@app.callback(
    Output('policy_graph','children'),
    [
    Input('state_abbrev', 'value'),
    Input('feature', 'value'),
    Input('policy', 'value')
    ])
def plot_features_and_policies(state_abbr, feature, policy):
    filter_features, filter_dates = get_filtered_stats(state_abbr, feature)
    policy_start_dates, start_policies_desc, policy_stop_dates, stop_policies_desc = get_filtered_policies(state_abbr, policy)
    policy_start_points = [max(filter_features)] * len(policy_start_dates)
    policy_stop_points = [max(filter_features)] * len(policy_stop_dates)

    fig_policy_feature = go.Figure(
        data=[go.Scatter(x=filter_dates, y=filter_features, name=feature),
             go.Scatter(x=policy_start_dates, y=policy_start_points, name='Start Date'),
             go.Scatter(x=policy_stop_dates, y=policy_stop_points, name='Stop Date')], 
        layout=go.Layout(
            title=go.layout.Title(text=feature)
        )
    )
    return dcc.Graph(
        id='policy_feature_graph',
        figure=fig_policy_feature
    )

@app.callback(
    [
    Output('start_policy','children'),
    Output('stop_policy','children'),
    ],
    [
    Input('state_abbrev', 'value'),
    Input('policy', 'value')
    ])
def print_policies(state_abbr, policy):
	policy_start_dates, start_policies_desc, policy_stop_dates, stop_policies_desc = get_filtered_policies(state_abbr, policy)
	start_store = ''
	if policy_start_dates:
		for index in range(len(policy_start_dates)):
			start_store = '{}, {}'.format(policy_start_dates[index].strftime("%m/%d/%Y"), start_policies_desc[index])
	else:
		start_store == 'No additional information.'

	stop_store = ''
	if policy_stop_dates:
		for index in range(len(policy_stop_dates)):
			stop_store = '{}, {}'.format(policy_stop_dates[index].strftime("%m/%d/%Y"), stop_policies_desc[index])
	else:
		stop_store == 'No additional information.'

	return start_store, stop_store

@app.callback(
    [Output(component_id='mean_close_graph', component_property='children'),
     Output(component_id='mean_high_graph', component_property='children'),
     Output(component_id='return_rate_graph', component_property='children'),
    ],
    [
    Input(component_id='show_general', component_property='value'),
    ]
)
def general_analysis(show_general):
    if show_general == 'Airline':
        all_during_mean_close, all_post_mean_close, all_during_mean_high, all_post_mean_high, all_during_return_rate, all_post_return_rate = get_stock_report(airline_stocks, start_date, end_date)
        mean_fig = go.Figure(data=[go.Bar(name='During Policy', x=airline_stocks, y=all_during_mean_close), go.Bar(name='After Policy', x=airline_stocks, y=all_post_mean_close)])
        high_fig = go.Figure(data=[go.Bar(name='During Policy', x=airline_stocks, y=all_during_mean_high), go.Bar(name='After Policy', x=airline_stocks, y=all_post_mean_high)])
        rr_fig = go.Figure(data=[go.Bar(name='During Policy', x=airline_stocks, y=all_during_return_rate), go.Bar(name='After Policy', x=airline_stocks, y=all_post_return_rate)])
        
    elif show_general == 'IT':
        all_during_mean_close, all_post_mean_close, all_during_mean_high, all_post_mean_high, all_during_return_rate, all_post_return_rate = get_stock_report(it_stocks, start_date, end_date)
        mean_fig = go.Figure(data=[go.Bar(name='During Policy', x=it_stocks, y=all_during_mean_close), go.Bar(name='After Policy', x=it_stocks, y=all_post_mean_close)])
        high_fig = go.Figure(data=[go.Bar(name='During Policy', x=it_stocks, y=all_during_mean_high), go.Bar(name='After Policy', x=it_stocks, y=all_post_mean_high)])
        rr_fig = go.Figure(data=[go.Bar(name='During Policy', x=it_stocks, y=all_during_return_rate), go.Bar(name='After Policy', x=it_stocks, y=all_post_return_rate)])
        
    elif show_general == 'Hotel':
        all_during_mean_close, all_post_mean_close, all_during_mean_high, all_post_mean_high, all_during_return_rate, all_post_return_rate = get_stock_report(hotel_stocks, start_date, end_date)
        mean_fig = go.Figure(data=[go.Bar(name='During Policy', x=hotel_stocks, y=all_during_mean_close), go.Bar(name='After Policy', x=hotel_stocks, y=all_post_mean_close)])
        high_fig = go.Figure(data=[go.Bar(name='During Policy', x=hotel_stocks, y=all_during_mean_high), go.Bar(name='After Policy', x=hotel_stocks, y=all_post_mean_high)])
        rr_fig = go.Figure(data=[go.Bar(name='During Policy', x=hotel_stocks, y=all_during_return_rate), go.Bar(name='After Policy', x=hotel_stocks, y=all_post_return_rate)])
        
    elif show_general == 'Entertainment':
        all_during_mean_close, all_post_mean_close, all_during_mean_high, all_post_mean_high, all_during_return_rate, all_post_return_rate = get_stock_report(entertainment_stocks, start_date, end_date)
        mean_fig = go.Figure(data=[go.Bar(name='During Policy', x=entertainment_stocks, y=all_during_mean_close), go.Bar(name='After Policy', x=entertainment_stocks, y=all_post_mean_close)])
        high_fig = go.Figure(data=[go.Bar(name='During Policy', x=entertainment_stocks, y=all_during_mean_high), go.Bar(name='After Policy', x=entertainment_stocks, y=all_post_mean_high)])
        rr_fig = go.Figure(data=[go.Bar(name='During Policy', x=entertainment_stocks, y=all_during_return_rate), go.Bar(name='After Policy', x=entertainment_stocks, y=all_post_return_rate)])
        
    mean_fig.update_layout(title='Mean Close during and after policy')
    mean_fig.update_layout(barmode='group')
    
    high_fig.update_layout(title='Mean High during and after policy')
    high_fig.update_layout(barmode='group')
    
    rr_fig.update_layout(title='Return Rate during and after policy')
    rr_fig.update_layout(barmode='group')
    
    return dcc.Graph(id='mean_graph',figure=mean_fig), dcc.Graph(id='high_graph',figure=high_fig), dcc.Graph(id='rr_graph', figure=rr_fig)

if __name__ == '__main__':
    app.run_server(use_reloader=False, port=8000)