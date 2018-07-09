import pandas as pd
import numpy as np
import requests
import json
import time
import datetime
from configparser import ConfigParser
'''
This python scripts does
'''

def get_MVC(year_min = 2013, year_max = 2017, API_KEY = None):
    '''
    This function query the data from NYC traffic count in 2012-2013
    (see https://data.cityofnewyork.us/Public-Safety/NYPD-Motor-Vehicle-Collisions/h9gi-nx95)
    
    Arguments:
        - year_min and year_max: year range
        - API_KEY: (string) the API key of SODA (None by default)
    
    Return:
        - data frame
    '''
    
    # url to request
    url = 'https://data.cityofnewyork.us/resource/qiz3-axqb.json'
    
    # set the limit of objects to return
    filter_year = "date between '{}-01-01T12:00:00' and '{}-12-31T12:00:00'".format(year_min,year_max)
    
    params = {'$limit' : 3000000,
    '$where': filter_year}
    
    # add API key
    if API_KEY:
        params['$$app_token'] = API_KEY

    # retrieve data
    result = requests.get(url, params = params)
    data = result.json()
    # return data (if no error)
    return pd.DataFrame(data)




def main():

    # enter API_KEY
    cfg = ConfigParser()
    cfg.read('config.ini')
    SODA_KEY = cfg.get('API KEYS','SODA_KEY')

    # enter year_min and year_max
    year_min = 2013
    year_max = 2017
    df_collision = get_MVC(year_min, year_max, API_KEY = SODA_KEY)
    
    # column names in upper case
    df_collision.columns = df_collision.columns.str.upper()
    df_collision.to_csv('Collisions.csv', index = False)

if __name__ == "__main__":
    main()

