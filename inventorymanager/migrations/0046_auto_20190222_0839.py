# Generated by Django 2.1.5 on 2019-02-22 08:39

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventorymanager', '0045_auto_20190222_0838'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sku',
            name='unitupc',
            field=models.CharField(default=100000000000, max_length=12, validators=[django.core.validators.RegexValidator('^\\d{12,12}$', code='invalid UPC', message='UPC not 12 digits')]),
        ),
    ]