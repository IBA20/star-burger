# Generated by Django 3.2.15 on 2022-09-18 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0045_auto_20220918_1217'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('CS', 'Наличными при получении'), ('CD', 'Картой на сайте'), ('EL', 'Электронно')], db_index=True, default='CS', max_length=2, verbose_name='Способ оплаты'),
        ),
    ]