import json
import numpy as np
import pandas as pd
from logzero import logger
from plotly import graph_objs as go
import plotly.express as px
import utils_covid as f
pd.set_option('chained_assignment', None)

################################################################################################
################################################################################################
################################################################################################

def process_pandemic_data(df, startdate = '2020-03-01'):

    # Columns renaming
    df.columns = [col.lower() for col in df.columns]

    # Keep only from a starting date
    df = df[df['date'] > startdate]

    # Create a zone per zone/subzone
    df['zone'] = df['zone'].apply(str) + ' ' + df['sub zone'].apply(lambda x: str(x).replace('nan', ''))
    
    # Extracting latitute and longitude
    df['lat'] = df['location'].apply(lambda x: x.split(',')[0])
    df['lon'] = df['location'].apply(lambda x: x.split(',')[1])

    # Saving countries positions (latitude and longitude per subzones)
    country_position = df[['zone', 'lat', 'lon']].drop_duplicates(['zone']).set_index(['zone'])

    # Pivoting per category
    df = pd.pivot_table(df, values='count', index=['date', 'zone'], columns=['category'])
    df.columns = ['confirmed', 'deaths', 'recovered']

    # Merging locations after pivoting
    df = df.join(country_position)

    # Filling nan values with 0
    df = df.fillna(0)

    # Compute bubble sizes
    df['size'] = df['confirmed'].apply(lambda x: (np.sqrt(x/100) + 1) if x > 500 else (np.log(x) / 2 + 1)).replace(np.NINF, 0)
    df['color'] = (df['recovered']/df['confirmed']).fillna(0).replace(np.inf , 0) * 100
    
    # Prepare display values for bubble hover
    df['confirmed_display'] = df['confirmed'].apply(int).apply(f.spacify_number)
    df['recovered_display'] = df['recovered'].apply(int).apply(f.spacify_number)
    df['deaths_display'] = df['deaths'].apply(int).apply(f.spacify_number)

    
    return df


def create_world_fig(df, mapbox_access_token):
   
    days = df.index.levels[0].tolist()
    # day = min(days)

    # Defining each Frame
    frames = [{
        # 'traces':[0],
        'name':'frame_{}'.format(day),
        'data':[{
            'type':'scattermapbox',
            'lat':df.xs(day)['lat'],
            'lon':df.xs(day)['lon'],
            'marker':go.scattermapbox.Marker(
                size=df.xs(day)['size'],
                color=df.xs(day)['color'],
                showscale=True,
                colorbar={'title':'Recovered', 'titleside':'top', 'thickness':4, 'ticksuffix':' %'},
                # color_continuous_scale=px.colors.cyclical.IceFire,
            ),
            'customdata':np.stack((df.xs(day)['confirmed_display'], df.xs(day)['recovered_display'],  df.xs(day)['deaths_display'], pd.Series(df.xs(day).index)), axis=-1),
            'hovertemplate': "<extra></extra><em>%{customdata[3]}  </em><br>🚨  %{customdata[0]}<br>🏡  %{customdata[1]}<br>⚰️  %{customdata[2]}",
        }],           
    } for day in days]  


    # Get the first frame data to set up the initial display
    data = frames[0]['data']         


    # Defining the slider to navigate between frames
    sliders = [{
        'transition':{'duration': 0},
        'x':0.08,     #slider starting position  
        'len':0.88,
        'currentvalue':{
            'font':{'size':15}, 
            'prefix':'📅 ', # Day:
            'visible':True, 
            'xanchor':'center'
            },  
        'steps':[{
            'method':'animate',
            'args':[
                ['frame_{}'.format(day)],
                {
                    'mode':'immediate',
                    'frame':{'duration':250, 'redraw': True}, #100
                    'transition':{'duration':100} #50
                }
                ],
            'label':day
        } for day in days]
    }]

    play_button = [{
        'type':'buttons',
        'showactive':True,
        'y':-0.08,
        'x':0.045,
        'buttons':[{
            'label':'🎬', # Play
            'method':'animate',
            'args':[
                None,
                {
                    'frame':{'duration':250, 'redraw':True}, #100
                    'transition':{'duration':100}, #50
                    'fromcurrent':True,
                    'mode':'immediate',
                }
            ]
        }]
    }]

    # Global Layout
    layout = go.Layout(
        height=600,
        autosize=True,
        hovermode='closest',
        paper_bgcolor='rgba(0,0,0,0)',
        mapbox={
            'accesstoken':mapbox_access_token,
            'bearing':0,
            'center':{"lat": 37.86, "lon": 2.15},
            'pitch':0,
            'zoom':1.7,
            'style':'light',
        },
        updatemenus=play_button,
        sliders=sliders,
        margin={"r":0,"t":0,"l":0,"b":0}
    )


    return go.Figure(data=data, layout=layout, frames=frames)

################################################################################################
################################################################################################
################################################################################################


if __name__ =="__main__":    

    # Loading necessary information
    mapbox_access_token = f.config['mapbox']['token']
    raw_dataset_path = f.RAW_PATH + f.config['path']['name']
    
    # Creating dataFrames
    df_raw = pd.read_csv(raw_dataset_path, sep=';')
    df_world = process_pandemic_data(df_raw)
    df_total_kpi = df_world.groupby('date').sum().sort_index().iloc[-1]
    
    # Preparing figure
    fig_world = create_world_fig(df_world, mapbox_access_token=mapbox_access_token)

    # Storing all necessay information for app
    save = {
        'figure':fig_world,
        'last_date':df_world.index[-1][0],
        'total_confirmed': f.spacify_number(int(df_total_kpi['confirmed'])),
        'total_deaths': f.spacify_number(int(df_total_kpi['deaths'])),
        'total_recovered': f.spacify_number(int(df_total_kpi['recovered']))
    }
    f.save_pickle(save, 'world_info.p')

    # Display information
    logger.info('World map updated.')
    logger.info('Data sotred for dash application.')
    logger.info('Last date in new dataset is {}'.format(df_world.index[-1][0]))


