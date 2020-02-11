import requests
import json
import pandas as pd
from pandas import json_normalize
from datetime import date, datetime, timedelta

# key can be obtained from https://darksky.net/dev
key = '6015f7479c39552c4dbac4583b4bfa7e'
output_df = pd.DataFrame()
sdate = date(2017, 12, 10)
edate = date(2019, 8, 31)
# to save api calls
# edate = date(2017, 12, 15)

delta = edate - sdate       # as timedelta

days = []
for i in range(delta.days + 1):
    day = sdate + timedelta(days=i)
    days.append(day)

min_time = datetime.min.time()
dts = [datetime.strftime(datetime.combine(day, min_time), '%Y-%m-%dT%H:%M:%S') for day in days]

for i, dt in enumerate(dts):
    url = 'https://api.darksky.net/forecast/' + key + '/42.3601,-71.0589,' + dt + \
          '?exclude=currently,flags'
    response = requests.get(url)
    parsed = json.loads(response.content)
    df = json_normalize(parsed['daily']['data'][0])
    df['time'] = pd.to_datetime(df['time'],unit='s')
    output_df = output_df.append(df)

output_df.rename(columns={'time': 'date'}, inplace=True)
output_df['date'] = [datetime.strftime(dt, '%Y-%m-%d') for dt in output_df['date']]
output_df.to_csv('historical_daily_weathers.csv', index=False)




