############################################################################################
########################################## IMPORTS #########################################
############################################################################################

# Classic libraries
import os
import numpy as np
import pandas as pd

# Logging information
import logging
import logzero
from logzero import logger

# Dash imports
import dash
import dash_core_components as dcc
import dash_html_components as html

# Custom function
import scripts.utils_covid as f

############################################################################################
############################## PARAMETERS and PRE-COMPUTATION ##############################
############################################################################################

# Load pre computed data
world = f.load_pickle('world_info.p')

# Deployment inforamtion
PORT = 8050

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
            href='https://towardsdatascience.com/how-to-create-animated-scatter-maps-with-plotly-and-dash-f10bb82d357a',
            children=[
                html.Img(src=app.get_asset_url('medium.png'), width=20, height=20),
                html.Span("Map")
            ]
        ),
        html.A(
            href='https://medium.com/@thibaud.lamothe2/deploying-dash-or-flask-web-application-on-heroku-easy-ci-cd-4111da3170b8',
            children=[
                html.Img(src=app.get_asset_url('medium.png'), width=20, height=20),
                html.Span("Deploy")
            ]
        ),
        html.A(
            href='https://github.com/ThibaudLamothe/dash-mapbox',
            children=[
                html.Img(src=app.get_asset_url('github.png'), width=20, height=20),
                # "Application code"
                html.Span("Code")
            ]
        ),
        html.A(
            href='https://public.opendatasoft.com/explore/dataset/covid-19-pandemic-worldwide-data/information/?disjunctive.zone&disjunctive.category&sort=date',
            children=[
                html.Img(src=app.get_asset_url('database.png'), width=20, height=20),
                # "Original COVID dataset"
                html.Span("Data")
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
                html.H1("COVID 19 🦠 - Day to day evolution all over the world", className="header__text"),
                html.Span('(Last update: {})'.format(world['last_date'])),
                # html.Hr(),
            ],
        ),

        # CONTENT
        html.Section([
            
            # Line 1 : KPIS - World
            html.Div(
                id='world_line_1',
                children = [ 
                    html.Div(children = ['🚨 Confirmed', html.Br(), world['total_confirmed']], id='confirmed_world_total', className='mini_container'),
                    html.Div(children = ['🏡 Recovered', html.Br(), world['total_recovered']], id='recovered_world_total', className='mini_container'),
                    html.Div(children = [' ⚰️ Victims',   html.Br(), world['total_deaths']],    id='deaths_world_total',    className='mini_container'),            
                ],
            ),
            # html.Br(),
            links,

            # Line 2 : MAP - WORLD
            html.Div(
                id='world_line_2',
                children = [
                    dcc.Graph(id='world_map', figure=world['figure'], config={'scrollZoom': False}),         
                ],
            ),
            # html.Br(),
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
    