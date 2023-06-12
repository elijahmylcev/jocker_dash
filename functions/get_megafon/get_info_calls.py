import requests
import json

URL = 'https://vats342618.megapbx.ru/history'
params = {
  "token": 'Barrier 7ba71630-c149-4f2f-beab-d24597155fa9'
}
res = requests.get(URL, params=params)

print(res.content)