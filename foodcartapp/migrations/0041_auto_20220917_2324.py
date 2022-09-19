from django.db import migrations
from django.db.models import Subquery, OuterRef


def fill_empty_order_position_prices(apps, schema_editor):
    OrderPosition = apps.get_model('foodcartapp', 'OrderPosition')
    OrderPosition.objects.filter(price=0).update(price=Subquery(
        OrderPosition.objects.filter(
            pk=OuterRef('pk')
        ).values('product__price')[:1])
    )


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0040_auto_20220917_2323'),
    ]

    operations = [
        migrations.RunPython(fill_empty_order_position_prices),
    ]
