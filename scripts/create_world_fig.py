import json
import numpy as np
import pandas as pd

import plotly.express as px
from plotly import graph_objs as go

import utils_covid as f

################################################################################################
################################################################################################
################################################################################################

def process_pandemic_data(df, startdate = '2020-02-01'):

    # Focus on zones
    df['subzone'] = df[['Zone', 'Sub Zone']].apply(lambda line: line['Zone'] if pd.isnull(line['Sub Zone']) else line['Sub Zone'], axis=1)
    
    # Columns renaming
    df.columns = [col.lower() for col in df.columns]

    # Extracting latitute and longitude
    df['lat'] = df['location'].apply(lambda x: x.split(',')[0])
    df['lon'] = df['location'].apply(lambda x: x.split(',')[1])

    # Saving countries positions (latitude and longitude per subzones)
    country_position = df[['subzone', 'lat', 'lon']].drop_duplicates("subzone").set_index('subzone').to_dict(orient='index')
    
    # Droping unnecessary colunms
    df = df.drop(['zone', 'sub zone', 'location'], axis=1)

    # Pivoting per category
    df = pd.pivot_table(df, values='count', index=['date', 'subzone'], columns=['category'])
    df.columns = ['confirmed', 'deaths', 'recovered']

    # Keep only from a starting date
    df = df.reset_index()
    df = df[df['date'] > startdate]

    # Re insert country location
    df['lat'] = df['subzone'].apply(lambda x:country_position[x]['lat']).apply(float)
    df['lon'] = df['subzone'].apply(lambda x:country_position[x]['lon']).apply(float)

    # Define the buble sizes
    n_size = 100
    max_value = int(df['confirmed'].max())
    scales = np.array([i for i in range(0, max_value, int(max_value/n_size))]) 
    x = [i for i in range(n_size+2)]
    y = [np.sqrt(i) for i in range(n_size+2)]
    df['size'] = df['confirmed'].apply(lambda v: 0 if v==0 else np.argmin(np.abs(scales - v)) + 1)
    df['size'] = df['size'].apply(lambda v:y[v]*10)

    # Aggregatee data by date and zone
    df = df.groupby(['date', 'subzone']).agg({'confirmed':'sum', 'deaths':'sum', 'recovered':'sum','lat':'last', 'lon':'last', 'size':'last'})
    df['confirmed'] = df['confirmed'].fillna(0)
    df['recovered'] = df['recovered'].fillna(0)
    df['deaths'] = df['deaths'].fillna(0)
    
    return df


def create_world_fig(df, mapbox_access_token):
   
    days = df.index.levels[0].tolist()
    day = min(days)

    # Defining each Frame
    frames = [{
        'traces':[0],
        'name':'frame_{}'.format(day),
        'data':[{
            'type':'scattermapbox',
            'lat':df.xs(day)['lat'],
            'lon':df.xs(day)['lon'],
            'marker':go.scattermapbox.Marker(size=(df.xs(day)['size'])),
            'text':df.xs(day)['confirmed'],
        }],           
    } for day in days]  


    # Get the first frame data to set up the initial display
    data = frames[0]['data']         


    # Defining the slider to navigate between frames
    sliders = [{
        'transition':{'duration': 0},
        'x':0.05,     #slider starting position  
        'y':-0.05, 
        'len':0.9,
        'currentvalue':{
            'font':{'size':12}, 
            'prefix':'Day: ', 
            'visible':True, 
            'xanchor':'center'
            },  
        'steps':[{
            'method':'animate',
            'args':[
                ['frame_{}'.format(k)],
                {
                    'mode':'immediate',
                    'frame':{'duration':100, 'redraw': True},
                    'transition':{'duration':50}
                }
                ],
            'label':k
        } for k in days]
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
        updatemenus=[{
            'type':'buttons',
            'showactive':True,
            'y':-0.1,
            'x':0.03,
            'buttons':[{
                'label':'Play',
                'method':'animate',
                'args':[
                    None,
                    {
                        'frame':{'duration':100, 'redraw':True},
                        'transition':{'duration':50},
                        'fromcurrent':True,
                        'mode':'immediate',
                    }
                ]
            }]
        }],
        sliders=sliders,
    )

    FIG=go.Figure(data=data, layout=layout, frames=frames)
    FIG.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return FIG

################################################################################################
################################################################################################
################################################################################################


if __name__ =="__main__":

    mapbox_access_token = f.load_mapbox_token()

    raw_dataset_path = f.DATA_PATH + 'raw/covid-19-pandemic-worldwide-data.csv'
    df = pd.read_csv(raw_dataset_path, sep=';')

    df = process_pandemic_data(df)
    # f.save_pickle(df, 'df_world.p')

    FIG = create_world_fig(df, mapbox_access_token=mapbox_access_token)
    # f.save_pickle(FIG, 'fig_world.p')

    ind = df.groupby('date').sum().sort_index().iloc[-1]
    save = {
        'figure':FIG,
        'last_date':df.index[-1][0],
        'total_confirmed': f.spacify_number(int(ind['confirmed'])),
        'total_deaths': f.spacify_number(int(ind['deaths'])),
        'total_recovered': f.spacify_number(int(ind['recovered']))
    }
    f.save_pickle(save, 'world_info.p')


