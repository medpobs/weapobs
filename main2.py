import json
import os
from datetime import date, datetime, timedelta
from ftplib import FTP, error_perm

import pandas as pd
import requests
from pandas import json_normalize

# key can be obtained from https://darksky.net/dev
key = '6015f7479c39552c4dbac4583b4bfa7e'
bw_days = 1
fw_days = 5
sdate = date.today()
ldate = sdate - timedelta(days=1)
edate = sdate + timedelta(days=5)
# to save api calls

days = []

path = "output/" + str(sdate)

try:
    os.mkdir(path)
except OSError:
    print ("Creation of the directory %s failed" % path)
else:
    print ("Successfully created the directory %s " % path)


with open('big_cities.json') as f:
    geo_data = json.load(f)


for i in range(fw_days):
    day = sdate + timedelta(days=i)
    days.append(day)

min_time = datetime.min.time()
last_dt = datetime.strftime(datetime.combine(ldate, min_time), '%Y-%m-%dT%H:%M:%S')
dts = [datetime.strftime(datetime.combine(day, min_time), '%Y-%m-%dT%H:%M:%S') for day in days]

for j, city in enumerate(geo_data):
    hist_df = pd.DataFrame()
    city_path = path + '/' + str(city['name'])
    try:
        os.mkdir(city_path)
    except OSError:
        print ("Creation of the directory %s failed" % city_path)
    else:
        print ("Successfully created the directory %s " % city_path)

    lat = city['lat']
    lng = city['lng']
    url = 'https://api.darksky.net/forecast/' + key + '/' + str(lat) + ',' + str(lng) + ',' + last_dt + \
          '?exclude=currently,flags'
    response = requests.get(url)
    parsed = json.loads(response.content)
    df = json_normalize(parsed['daily']['data'][0])
    df['time'] = pd.to_datetime(df['time'], unit='s')
    hist_df = hist_df.append(df)
    hist_df.rename(columns={'time': 'date'}, inplace=True)
    hist_df['date'] = [datetime.strftime(dt, '%Y-%m-%d') for dt in hist_df['date']]
    hist_df.to_csv(city_path + '/a0.csv', index=False)

for j, city in enumerate(geo_data):
    city_path = path + '/' + str(city['name'])

    for i, dt in enumerate(dts):
        forecast_df = pd.DataFrame()
        lat = city['lat']
        lng = city['lng']
        url = 'https://api.darksky.net/forecast/' + key + '/' + str(lat) + ',' + str(lng) + ',' + dt + \
              '?exclude=currently,flags'
        response = requests.get(url)
        parsed = json.loads(response.content)
        df = json_normalize(parsed['daily']['data'][0])
        df['time'] = pd.to_datetime(df['time'], unit='s')
        forecast_df = forecast_df.append(df)
        forecast_df.rename(columns={'time': 'date'}, inplace=True)
        forecast_df['date'] = [datetime.strftime(dt, '%Y-%m-%d') for dt in forecast_df['date']]
        forecast_df.to_csv(city_path + '/c' + str(i) + '.csv', index=False)

host = 'medpobs.com'
port = 21
username = 'val@medpobs.com'
password = 'voov2020'
store_path = '/public_html/medpobs.com/all_data/weather'
ftp = FTP()
ftp.connect(host,port)
ftp.login(username,password)
ftp.cwd(store_path)
ftp.mkd(str(sdate))
ftp.cwd(store_path + '/' + str(sdate))
filenameCV = path

def placeFiles(ftp, path):
    for name in os.listdir(path):
        localpath = os.path.join(path, name)
        if os.path.isfile(localpath):
            print("STOR", name, localpath)
            ftp.storbinary('STOR ' + name, open(localpath,'rb'))
        elif os.path.isdir(localpath):
            print("MKD", name)

            try:
                ftp.mkd(name)

            # ignore "directory already exists"
            except error_perm as e:
                if not e.args[0].startswith('550'):
                    raise

            print("CWD", name)
            ftp.cwd(name)
            placeFiles(ftp, localpath)
            print("CWD", "..")
            ftp.cwd("..")

placeFiles(ftp, filenameCV)

ftp.quit()



