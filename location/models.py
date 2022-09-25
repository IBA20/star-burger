from django.db import models


class Location(models.Model):
    address = models.CharField(
        'Адрес',
        max_length=100,
        db_index=True,
        unique=True
    )
    lat = models.FloatField('Широта')
    lon = models.FloatField('Долгота')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
