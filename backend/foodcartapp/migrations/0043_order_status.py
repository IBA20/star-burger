# Generated by Django 3.2.15 on 2022-09-18 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0042_alter_orderposition_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('NW', 'Новый'), ('AP', 'Распределен'), ('PR', 'Приготовление'), ('DL', 'Доставка'), ('CP', 'Исполнен'), ('CN', 'Отменен')], db_index=True, default='NW', max_length=2, verbose_name='Статус'),
        ),
    ]