import requests
from bs4 import BeautifulSoup
import json

url = 'https://api.kinopoisk.dev/movie'
requested_genres = ['боевик']
requested_types = ''

params_1 = {
    'token': 'ZQQ8GMN-TN54SGK-NB3MKEC-ZKB8V06',
    'field': 'rating.kp',
    'search': '7-10',
}

response = requests.get(url=url, params=params_1)
# print(response.text)
# print(response.request.body)
ids = []
for item in response.json()['docs'][:50]:
    ids.append((item['id'], item['type']))

print(ids)

params_2 = {
    'token': 'ZQQ8GMN-TN54SGK-NB3MKEC-ZKB8V06',
    'search': '7-10',
}

result = []
for id_type in ids[:3]:
    id = id_type[0]
    response = requests.get(url, params={
        'token': 'ZQQ8GMN-TN54SGK-NB3MKEC-ZKB8V06',
        'search': id,
        'field': 'id',

    })

    film_info = response.json()
    print(film_info)
    genres = [x['name'].lower() for x in film_info['genres']]
    for genre in requested_genres:
        if genre in genres:
            result.append(film_info)
    # with open('res.json', 'w', encoding='utf-8') as file:
    #     json.dump(result, file, indent=4, ensure_ascii=False)


print(result)
# print(ids)
