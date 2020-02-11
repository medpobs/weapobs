import requests
url = 'https://api.darksky.net/forecast/d55d2612b4e19bcccf7d321006926d95/42.3601,-71.0589,2017-12-10T10:00:00?exclude=currently,flags'

response = requests.get(url)
print(response.content)




