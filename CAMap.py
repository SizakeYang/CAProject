import folium
import requests
import numpy as np
import pandas as pd
from folium.plugins import HeatMap


def getLocation(text):
    url = "http://api.map.baidu.com/geocoding/v3/"
    payload = {
        'output': 'json',
        'ak': 'wQ6MXrttpBaDqGxhBDKN4wkaIijnAzEL',
        'city': '汕头市'
    }
    payload['address'] = text
    content = requests.get(url, params=payload, timeout=(5, 5)).json()
    print(content['result']['location'])
    return content['result']['location']


def main():
    data = pd.read_excel('/mnt/c/Users/HP/Desktop/address.xlsx')
    data['location'] = data['pre_address'].apply(getLocation)
    data.to_excel('/home/yangzake/OI/ca_final.xlsx', index=False)