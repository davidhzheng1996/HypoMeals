# Generated by Django 2.1.5 on 2019-02-14 22:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventorymanager', '0017_remove_sku_product_line'),
    ]

    operations = [
        migrations.AddField(
            model_name='sku',
            name='product_line',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='inventorymanager.Product_Line'),
        ),
    ]