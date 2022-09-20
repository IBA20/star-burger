from django.db import migrations


def change_order_statuses_marker(apps, schema_editor):
    Order = apps.get_model('foodcartapp', 'Order')
    markers = {'NW': '10', 'AP': '20', 'PR': '30', 'DL': '40', 'CP': '50', 'CN': '90'}
    for old_marker in markers:
        Order.objects\
            .filter(status=old_marker)\
            .update(status=markers[old_marker])


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0048_auto_20220920_2217'),
    ]

    operations = [
        migrations.RunPython(change_order_statuses_marker),
    ]
