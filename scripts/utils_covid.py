# Import packages
import os 
import pickle

 
DATA_PATH = '/Users/thibaud/Documents/Python_scripts/02_Projects/dash-choropleth-map/data/'
PICKLE_PATH = DATA_PATH + 'pickle/'


def load_pickle(file_name):
    file_path = PICKLE_PATH + file_name
    with open(file_path, 'rb') as pfile:
        my_pickle = pickle.load(pfile)
    return my_pickle


def save_pickle(object_, file_name):
    file_path = PICKLE_PATH + file_name
    with open(file_path, 'wb') as pfile:
        pickle.dump(object_, pfile, protocol=pickle.HIGHEST_PROTOCOL)


def list_pickle():
    file_list = os.listdir(PICKLE_PATH)
    pickle_list = [i for i in file_list if '.p' in i]
    print(pickle_list)


def load_mapbox_token():
    file_path = DATA_PATH + 'mapbox.token'
    with open(file_path, 'r') as pfile:
        token = pfile.read()
    return token
    

def spacify_number(number):
    nb_rev = str(number)[::-1]
    new_chain = ''
    for val, letter in enumerate(nb_rev):
        if val%3==0:
            new_chain += ' '
        new_chain += letter
    final_chain = new_chain[::-1]
    return final_chain