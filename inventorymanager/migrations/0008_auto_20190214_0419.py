# Generated by Django 2.1.5 on 2019-02-14 04:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventorymanager', '0007_auto_20190213_1934'),
    ]

    operations = [
        migrations.CreateModel(
            name='Formula',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('formula_name', models.CharField(default='', max_length=32)),
                ('comment', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Manufacture_line',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ml_name', models.CharField(default='', max_length=32)),
                ('ml_short_name', models.CharField(default='', max_length=5)),
                ('comment', models.TextField(null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='sku',
            name='caseupc',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='sku',
            name='sku_name',
            field=models.CharField(default='', max_length=32),
        ),
        migrations.AlterField(
            model_name='sku',
            name='unitupc',
            field=models.FloatField(default=0, null=True),
        ),
    ]