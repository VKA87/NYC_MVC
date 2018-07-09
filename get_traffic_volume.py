import pandas as pd
import numpy as np
import requests
import re
import json
import time
import datetime
from configparser import ConfigParser

'''
This python scripts does
'''

def get_traffic_count(API_KEY = None):
    '''
    This function query the data from NYC traffic count in 2012-2013
    (see https://data.cityofnewyork.us/Transportation/Traffic-Volume-Counts-2012-2013-/p424-amsu)
    
    Arguments:
        - API_KEY: (string) the API key of SODA (None by default)
    
    Return:
        - data frame
    '''
    
    # url to request
    url = 'https://data.cityofnewyork.us/resource/ry4b-kref.json'
    
    # set the limit of objects to return
    params = {'$limit' : 30000}
    
    # add API key
    if API_KEY:
        params['$$app_token'] = API_KEY

    # retrieve data
    result = requests.get(url, params = params)
    data = result.json()
    
    # return data (if no error)
    try:
        return pd.DataFrame(data)
    except:
        print('ERROR RETRIEVING THE DATA')
        print(data['message'])
        return None



def get_coord(address, API_KEY = None):
    '''
    This function takes an address and an API_KEY and return a list corresponding to the latitude and the longitude and the borough

    Arguments:
        - address: (string) corresponds to the place we are looking at
        - API_KEY: (string) the API key of google (None by default)
    
    Return:
        - [latitude (float), longitude (float), borough (str)]: list of three floats
    '''

    # URL to request
    url = "https://maps.googleapis.com/maps/api/geocode/json?"
    
    # add address
    params = {'address': address}
    
    # add API key
    if API_KEY:
        params['key'] = API_KEY
    
    # Get the result and store it in a dictionary (data)
    result = requests.get(url, params = params)
    data = result.json()

    # If the status is not "OK" return None
    if data['status'] != 'OK':
        print('STATUS', data['status'])
        return None
    

    # Get the coordinates
    coord = data['results'][0]['geometry']['location']
    #borough = data['results'][0]['address_components'][1]['long_name']
    address_components = data['results'][0]['address_components']

    borough = ''
    for ac in address_components:
        if ac['long_name'] in ['Bronx','Brooklyn','Manhattan','Queens','Staten Island']:
            borough = ac['long_name']

    # pattern = (r'[\S\s]*({}|{}|{}|{}|{})[\S\s]*').format('Bronx','Brooklyn','Manhattan','Queens','Staten Island')
    # m = re.match(pattern,address)
    # if m:
    #     borough = m.group(1)
    # else:
    #     print(address)
    #     borough = ''
    if borough == '':
        print(address)
    return [coord['lat'],coord['lng'],borough.upper()]

def add_suffix(address):
    '''
    This function add the suffix 'ST', 'ND', 'RD' or 'TH' to numbers if they are missing

    argument:
        - address (str)
    
    returns:
        - address (str) with suffix added
    '''

    m = re.match(r'.*([\d]+)\s',address)
    s = re.split(r'([\d]+)\s',address)

    if m:
        dgt = int(m.group(1))
        if dgt == 1:
            SUF = 'ST '
        elif dgt == 2:
            SUF = 'ND '
        elif dgt == 3:
            SUF = 'RD '
        else:
            SUF = 'TH '

        return SUF.join(s[1:])
    return address
    
def get_coord_segment(main_road, From, To, API_KEY, wait = 10):
    """
    A segment is given by a main street (main_raod) and two end points (From and To)
    This function returns the coordinates of the middle point taken to be the average of the coordinates of the two endpoints

    Argument:
        - main_road: (string) main_road
        - From: (string) begining of segment
        - To: (string) end of segment
        - API_KEY: (string) API key (None by default)
        - wait: (int or float) waiting time in mins if we go above quota (10 by default)
    
    Return:
        - [latitude, longitude]: list of two floats

    """

    
    main_road = add_suffix(main_road)
    From = add_suffix(From)
    To = add_suffix(To)

    address_from = main_road + '+' + From+ '+NEW YORK CITY' # address of beginning of segment
    address_to = main_road + '+' + To + '+NEW YORK CITY' # address of end of segment
    
    while True:
        # Get GPS coordinates of beginning and end of segment
        coord_from = get_coord(address_from, API_KEY)
        coord_to = get_coord(address_to, API_KEY)
        time.sleep(0.5)

        # If request is denied wait for "wait" mins
        if (not coord_from) or (not coord_to):
            print('waiting for ', wait, ' mins @ ',datetime.datetime.now().strftime("%H:%M"), '\r')
            time.sleep(wait*60)
        else:
            # Compute the latitude and longitude as average of the coord of the two points
            lat = (coord_from[0]+coord_to[0])/2
            lng = (coord_from[1]+coord_to[1])/2
            return [lat,lng,coord_from[2]]


def main():

    # get API_KEY from config.ini
    cfg = ConfigParser()
    cfg.read('config.ini')
    GOOGLE_KEY = cfg.get('API KEYS','GOOGLE_KEY')
    SODA_KEY = cfg.get('API KEYS','SODA_KEY')
    
    
    # import the traffic data set
    df_traffic = get_traffic_count(API_KEY = SODA_KEY)
    
    # define a new feature 'Segment' as a tuple of ('Roadway Name', 'From', 'To)
    df_traffic['segment'] = list(zip(df_traffic['roadway_name'],
                                df_traffic['from'],df_traffic['to']))

    # get all the segments
    segments = df_traffic['segment'].unique()                                                       
    print("Total number of requests = ",  2*len(segments))
    
    n_requests = 0 #counter to update the number of requests done
    
    # define two dictionaries {key = segment : value = latitude/longitude}
    LATITUDE_DICT = {}
    LONGITUDE_DICT = {}
    BOROUGH_DICT = {}
    
    for segment in segments:
        main_road = segment[0].strip()
        From = segment[1].strip()
        To = segment[2].strip()
        coord = get_coord_segment(main_road, From, To, GOOGLE_KEY, wait = 1)
        n_requests += 2
        print("Number of requests done: ", n_requests ,end = '\r')

        LATITUDE_DICT[segment] = coord[0]
        LONGITUDE_DICT[segment] = coord[1]
        BOROUGH_DICT[segment] = coord[2]

    # add two features LATITUDE and LONGITUDE
    df_traffic['LATITUDE'] = df_traffic['segment'].map(LATITUDE_DICT)
    df_traffic['LONGITUDE'] = df_traffic['segment'].map(LONGITUDE_DICT)
    df_traffic['BOROUGH'] = df_traffic['segment'].map(BOROUGH_DICT)

    # remove segment
    del  df_traffic['segment']
    
    # column names in upper case
    # column case in upper case
    df_traffic.columns = df_traffic.columns.str.upper()

    # export
    df_traffic.to_csv('Traffic_Volume.csv', index = False)

if __name__ == "__main__":
    main()

