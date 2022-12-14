import requests
from django.conf import settings
from django.utils import timezone
from geopy import distance

from location.models import Location


def fetch_coordinates(
    address: str, apikey: str = settings.YANDEX_GEOCODER_APIKEY
) -> tuple:
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(
        base_url, params={
            "geocode": address,
            "apikey": apikey,
            "format": "json",
        }
        )
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection'][
        'featureMember']

    if not found_places:
        return None, None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_distance(location1: tuple, location2: tuple) -> float:
    return distance.distance(location1, location2).km


def get_coordinates(address: str) -> [tuple, None]:
    try:
        lat, lon = fetch_coordinates(address)
        Location.objects.update_or_create(
            address=address,
            defaults={'lat': lat, 'lon': lon}
        )
        return lat, lon
    except requests.HTTPError:
        return None


def get_address_coordinates(address_list: list) -> dict:
    address_coordinates = {}
    for location in Location.objects.filter(address__in=address_list):
        if (timezone.now() - location.updated_at).days < \
                settings.LOCATION_UPDATE_TIMEOUT:
            address_coordinates[location.address] = (location.lat, location.lon)
    return address_coordinates
