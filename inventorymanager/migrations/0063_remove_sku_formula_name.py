# Generated by Django 2.1.5 on 2019-03-07 00:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventorymanager', '0062_sku_formula_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sku',
            name='formula_name',
        ),
    ]
