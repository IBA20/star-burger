import requests
from datetime import datetime
from django.conf import settings
from geopy import distance

from location.models import Location


def fetch_coordinates(address, apikey=settings.YANDEX_GEOCODER_APIKEY):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_distance(location1: tuple, location2: tuple) -> float:
    return distance.distance(location1, location2).km


def get_coordinates(address):
    try:
        location = Location.objects.get(address=address)
        if (datetime.now() - location.updated_at).days < 3:
            return location.lat, location.lon
    except Location.DoesNotExist:
        try:
            return fetch_coordinates(address)
        except Exception:
            return None
