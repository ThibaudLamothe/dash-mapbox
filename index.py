############################################################################################
########################################## IMPORTS #########################################
############################################################################################

# General libraries
import os

# Logging information
import logging
import logzero
from logzero import logger

# Classic libraries
import numpy as np
import pandas as pd

# Dash imports
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html

# Load data
import scripts.utils_covid as f

############################################################################################
############################## PARAMETERS and PRE-COMPUTATION ##############################
############################################################################################

# Load data
df_world = f.load_pickle('df_world.p')
FIG_world = f.load_pickle('fig_world.p')

# Deployment inforamtion
PORT = 8050

# Pre compute data
ind = df_world.groupby('date').sum().sort_index().iloc[-1]
last_date = df_world.index[-1][0]
total_confirmed = int(ind['confirmed'])
total_deaths = int(ind['deaths'])
total_recovered = int(ind['recovered'])

############################################################################################
########################################## APP #############################################
############################################################################################

# Creating app
app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)

# Associating server
server = app.server
app.title = 'COVID 19 - World cases'
app.config.suppress_callback_exceptions = True

############################################################################################
######################################### LAYOUT ###########################################
############################################################################################

links = html.Div(
    id='platforms_links',
    children=[                   
        html.A(
            href='http://etomal.com',
            children=[
                html.Img(src=app.get_asset_url('medium.png'), width=20, height=20),
                # "How to build a dynamic map with Plotly and Dash"
            ]
        ),
        html.A(
            href='http://etomal.com',
            children=[
                html.Img(src=app.get_asset_url('github.png'), width=20, height=20),
                # "Application code"
            ]
        ),
        html.A(
            href='http://etomal.com',
            children=[
                html.Img(src=app.get_asset_url('database.png'), width=20, height=20),
                # "Original COVID dataset"
            ],
        ),
    ],
)



app.layout = html.Div(
    children=[

        # HEADER
        html.Div(
            className="header",
            children=[
                html.H1("COVID 19 🦠 - Cases evolution all over the world", className="header__text"),
                html.Span('(Last update: {})'.format(last_date)),
                # html.Hr(),
            ],
        ),

        # CONTENT
        html.Section([
            
            # Line 1 : KPIS - World
            html.Div(
                id='world_line_1',
                children = [ 
                    html.Div(children = ['🚨 Confirmed', html.Br(), total_confirmed], id='confirmed_world_total', className='mini_container'),
                    html.Div(children = ['🏡 Recovered', html.Br(), total_recovered], id='recovered_world_total', className='mini_container'),
                    html.Div(children = [' ⚰️ Victims',   html.Br(), total_deaths],    id='deaths_world_total',    className='mini_container'),            
                ],
            ),
            # html.Br(),
            links,

            # Line 2 : MAP - WORLD
            html.Div(
                id='world_line_2',
                children = [
                    dcc.Graph(id='world_map', figure=FIG_world, config={'scrollZoom': False}),         
                ],
            ),
            html.Br(),
        ]),
    ],
)

############################################################################################
######################################### RUNNING ##########################################
############################################################################################

if __name__ == "__main__":
    
    # Display app start
    logger.error('*' * 80)
    logger.error('App initialisation')
    logger.error('*' * 80)

    # Starting flask server
    app.run_server(debug=True, port=PORT)
    