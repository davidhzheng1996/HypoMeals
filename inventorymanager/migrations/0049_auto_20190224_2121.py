# Generated by Django 2.1.5 on 2019-02-24 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventorymanager', '0048_auto_20190224_0424'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manufacture_goal',
            name='desired_quantity',
            field=models.FloatField(),
        ),
    ]