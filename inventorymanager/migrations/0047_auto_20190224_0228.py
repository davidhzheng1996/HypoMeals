# Generated by Django 2.1.5 on 2019-02-24 02:28

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventorymanager', '0046_auto_20190222_0839'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manufacture_line',
            name='ml_short_name',
            field=models.CharField(max_length=5, primary_key=True, serialize=False, unique=True, validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9\\S]{1,5}$', code='invalid Short name', message='Short name can have only Alphabets and Numbers')]),
        ),
    ]
