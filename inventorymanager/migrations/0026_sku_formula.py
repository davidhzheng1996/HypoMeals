# Generated by Django 2.1.5 on 2019-02-18 22:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventorymanager', '0025_auto_20190218_2224'),
    ]

    operations = [
        migrations.AddField(
            model_name='sku',
            name='formula',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='inventorymanager.Formula'),
        ),
    ]
