# Generated by Django 2.1.5 on 2019-04-11 02:47

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventorymanager', '0002_manufacture_goal_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sku',
            name='manufacture_rate',
            field=models.FloatField(default=1.0, validators=[django.core.validators.MinValueValidator(1e-07)]),
        ),
        migrations.AlterField(
            model_name='sku',
            name='manufacture_run_cost',
            field=models.DecimalField(decimal_places=2, default=1.0, max_digits=32, validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
        migrations.AlterField(
            model_name='sku',
            name='manufacture_setup_cost',
            field=models.DecimalField(decimal_places=2, default=1.0, max_digits=32, validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
    ]
