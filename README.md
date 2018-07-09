# Motor Vehicle Collisions in NYC

## Introduction

This repository contains an analysis of the road accidents in New York City as reported by the NYPD.
The data are available on the NYC open data website at

https://data.cityofnewyork.us/Public-Safety/NYPD-Motor-Vehicle-Collisions/h9gi-nx95

The data are analysed in light of the traffic data in NYC available on the NYC open data website as well at 

https://data.cityofnewyork.us/Transportation/Traffic-Volume-Counts-2012-2013-/p424-amsu

## Repository Files
The repository contains the following files

 Files                              | Description                                                         |
-----------------------------       |---------------------------------------------------------------------|
get_MVC.py                          | python script to get the motor vehicle collision data               |
get_traffic_volume.py               | python script to get the traffic volume                             |
NYC_boundaries.py                   | python script which returns the boundary of NYC (for creating maps) |
NYC Motor Vehicle Collisions.ipynb  | Notebook describing the analysis                                    |


## Getting the Data
The data are queried using an API. <b>The two scripts *get_MVC.py* and *get_traffic_volume.py* require an API_KEY which must be stored in an <b>*config.ini*</b> file which has the following structure</b>

```python
[API KEYS]
GOOGLE_KEY = your_google_apikey
SODA_KEY = your_soda_apikey
```
These keys can be obtained by registering here:
- GOOGLE MAP API: https://cloud.google.com/maps-platform/
- SODA API: https://dev.socrata.com/

### Getting Collision Data  (get_MVC.py)
The script *get_MVC.py* get the Motor Vehicle Collision data between two years to be specified (in this analysis 2013 to 2017 included) and export it as a csv file <b>*Collisions.csv*</b>

### Getting Collision Data  (get_traffic_volume.py)
The script *get_traffic_volume.py* get traffic volume in NYC (in 2012-2013). 
It  uses the googlemap API to find the longitude, latitude and borough of the road segments on which the traffic is measured.

### Maps  (NYC_boundaries.py)
The script *NYC_boundaries.py* gets the boundaries of NYC (in order to create map).
