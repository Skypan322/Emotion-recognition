import requests
import json
from bs4 import BeautifulSoup
from auth import api_key
from random import choice
import aiogram

url_filter = 'https://kinopoiskapiunofficial.tech/api/v2.2/films/filters'
curl = 'https://kinopoiskapiunofficial.tech/api/v2.2/films/'

# requested_genre = input().lower()



headers = {
    'X-API-KEY': api_key,
    'Content-Type': 'application/json',
}


def get_filters():
    with open('genre_id.json', encoding='utf-8') as file:
        unformed_genre_ids = json.load(file)

    genre_ids = {
        dict['genre']: dict['id'] for dict in unformed_genre_ids
    }

    return genre_ids


def get_film(curl, requested_genre):
    genre_ids = get_filters()
    params = {'genres': genre_ids[requested_genre],
              'raitingFrom': '8'
              }

    films = requests.get(curl, headers=headers, params=params).json()
    film = choice(films['items'])

    url = f'https://www.kinopoisk.ru/film/{film["kinopoiskId"]}/'
    name = film['nameRu']
    image_url = film['posterUrl']

    return url, name, image_url


if __name__=='__main__':
    url, name, image_url = get_film(curl, 'боевик')

    a = ''
    while a != 'ок':
        url, name, image_url = get_film(curl)
        print(f'Попробуй посмотреть "{name}", \nСсылка на него - {url}')
        a = input().lower()
