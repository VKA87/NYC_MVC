import numpy as np
import requests
import json

def get_boundary():

    url = 'http://polygons.openstreetmap.fr/get_geojson.py?id=175905&params=0'

    request  = requests.get(url)
    result = request.json()

    return np.array(result['geometries'][0]["coordinates"][0][0])

if __name__ == '__main__':
    print(get_boundary())