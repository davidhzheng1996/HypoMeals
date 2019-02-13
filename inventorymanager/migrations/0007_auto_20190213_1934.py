# Generated by Django 2.1.5 on 2019-02-13 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventorymanager', '0006_auto_20190206_0307'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sku',
            name='tuples',
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='cpp',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='id',
            field=models.BigIntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='sku',
            name='sku_name',
            field=models.CharField(default='', max_length=32, unique=True),
        ),
    ]
