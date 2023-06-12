from django.db import models


class Location(models.Model):
    address = models.CharField(
        'Адрес',
        max_length=100,
        db_index=True,
        unique=True
    )
    lat = models.FloatField('Широта', null=True)
    lon = models.FloatField('Долгота', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
