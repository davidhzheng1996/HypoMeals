# Generated by Django 2.1.5 on 2019-02-14 22:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventorymanager', '0016_auto_20190214_2158'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sku',
            name='product_line',
        ),
    ]