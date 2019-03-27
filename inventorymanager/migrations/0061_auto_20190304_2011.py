# Generated by Django 2.1.5 on 2019-03-04 20:11

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventorymanager', '0060_auto_20190304_0302'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sale_Record',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sale_date', models.DateField(default=datetime.date.today)),
                ('customer_name', models.CharField(default='', max_length=128, unique=True)),
                ('sales', models.PositiveIntegerField()),
                ('price_per_case', models.DecimalField(decimal_places=2, default=1.0, max_digits=12)),
            ],
        ),
        migrations.AlterField(
            model_name='customer',
            name='name',
            field=models.CharField(max_length=128, unique=True),
        ),
        migrations.AddField(
            model_name='sale_record',
            name='customer_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventorymanager.Customer'),
        ),
        migrations.AddField(
            model_name='sale_record',
            name='sku',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventorymanager.Sku'),
        ),
    ]