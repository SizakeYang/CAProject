import requests
import numpy as np
import pandas as pd


def getLocation(text):
    text = '汕头市金平区' + text
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
    data = pd.read_excel('/mnt/c/Users/HP/Desktop/ca.xlsx')
    data = data[data['pre_address'].notna()]
    data['location'] = data['pre_address'].apply(getLocation)
    data.to_excel('/mnt/c/Users/HP/Desktop/ca_final.xlsx', index=False)


main()