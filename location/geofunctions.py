import requests
from django.conf import settings
from django.utils import timezone
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
        if (timezone.now() - location.updated_at).days < 3:
            return location.lat, location.lon
        else:
            try:
                lat, lon = fetch_coordinates(address)
                location.lat = lat
                location.lon = lon
                location.save()
                return lat, lon
            except Exception:
                return location.lat, location.lon
    except Location.DoesNotExist:
        try:
            lat, lon = fetch_coordinates(address)
            Location.objects.create(
                address=address,
                lat=lat,
                lon=lon,
            )
            return fetch_coordinates(address)
        except Exception:
            return None
