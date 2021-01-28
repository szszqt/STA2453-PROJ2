import dash 
import dash_core_components as dcc 
import dash_html_components as html 
from dash.dependencies import Input, Output
import plotly.graph_objs as go 
import numpy as np 
import pandas as pd 
import pandas_datareader.data as web 
import datetime 
import matplotlib.pyplot as plt 
import plotly.tools as tls
from plotly.subplots import make_subplots

# external css and js 
# external_css = ["https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/css/materialize.min.css"]
# external_js = ['https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/js/materialize.min.js']

# load state data 
state_data = pd.read_csv('cleaned_state_data.csv')
# convert dates to datetime object
state_data.date = state_data.date.apply(lambda x: datetime.datetime.strptime(x, '%d-%m-%Y'))

# load policy data
state_policy = pd.read_csv('cleaned_state_policies.csv')
# convert the dates to datetime object
state_policy.date = state_policy.date.apply(lambda x: datetime.datetime.strptime(x, '%d-%m-%Y'))

list_states = state_data.state.unique()
list_dates = state_data.date.unique()
list_features = list(state_data.columns)

# app = dash.Dash('CovDash',
#                 external_scripts=external_js,
#                 external_stylesheets=external_css)

app = dash.Dash()

app.layout = html.Div([
		
		# heading Div
		html.Div([ 
		html.H1('Social Factors', style={'float':'left'})
		]),
		
		# dropdown menu to select states and features
		html.Div([
		html.Div('Enter State:'),
		dcc.Dropdown(id='state_abbrev', options=[{'label':s, 'value':s} for s in list_states]),
		html.Div('Enter Feature:'),
		dcc.Dropdown(id='features', options=[{'label':s, 'value':s} for s in list_features]),
		], style={"width": "10%"}),
		
		# radio button to show policies
		html.Div([
		html.Div(children='Show Policies'),
		dcc.RadioItems(
	    options=[
	        {'label': 'Yes', 'value': 'yes'},
	        {'label': 'No', 'value': 'no'},
	    ],
	    value='yes'
		)
		]),

		# feature-policy graphs 
		html.Div([
		html.Div(id='policy_graph'),
    	dcc.Interval(
        id='graph_update',
        interval=1000,
        n_intervals=0)
        ]),

    	# stock graph
		html.Div([
	    html.Div(children='Stock Index:'),
    	dcc.Input(id='stock_index', value='', type='text'),
    	html.Div(id='stock_graph'),
    	# dcc.Interval(
     #    id='graph_update',
     #    interval=1000,
     #    n_intervals=0),
		]),


	], className='container', style={'margin-left':10, 'margin-right':10})

@app.callback(
    Output('policy_graph','children'),
    [
    Input('state_abbrev', 'value'),
    Input('features', 'value'),
    # dash.dependencies.Input('graph_update', 'n_intervals')
    ])

def update_graph(state_abbr, feature):
	filtered_data = state_data[state_data['state']==state_abbr]
	data1_y = filtered_data[feature]
	data1_x = filtered_data['date']
	print(data1_y)
	print(data1_x)
	print('-__________________-')
	policies_state_date = state_policy[state_policy['state']==state_abbr]
	data2_x = policies_state_date['date']
	data2_y = [100]*len(policies_state_date)
	print(data2_y)
	print(data2_x)
	

	return dcc.Graph(
        id='example-graph',
        figure={
            'data': [
            			{'x':data1_x, 'y':data1_y, 'type':'scatter', 'name':feature},
            			{'x':data2_x, 'y':data2_y, 'type':'bar', 'name':''},
            		],
            'layout': {
                'title': feature
            },
        }
    )

	
@app.callback(
    Output(component_id='stock_graph', component_property='children'),
    [
    Input(component_id='stock_index', component_property='value'),
    Input('graph_update', 'n_intervals')
    ]
)

def update_value(input_data, n):
    start = datetime.datetime(2019, 3, 1)
    end = datetime.datetime.now()
    df = web.DataReader(input_data, 'yahoo', start, end)
    df.reset_index(inplace=True)
    df.set_index("Date", inplace=True)

    return dcc.Graph(
        id='example-graph',
        animate=True,
        figure={
            'data': [
                {'x': df.index, 'y': df.Close, 'type': 'line', 'name': input_data},
            ],
            'layout': {
                'title': input_data
            }
        }
    )

if __name__=='__main__':
	app.run_server(debug=True)




