# Generated by Django 2.1.5 on 2019-02-21 23:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventorymanager', '0034_auto_20190221_2302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sku',
            name='caseupc',
            field=models.BigIntegerField(default=100000000000, max_length=12, unique=True),
        ),
        migrations.AlterField(
            model_name='sku',
            name='unitupc',
            field=models.BigIntegerField(default=100000000000, max_length=12),
        ),
    ]
