# Generated by Django 5.0.4 on 2024-04-15 18:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sss_app', '0008_cart_total_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='total_price',
        ),
    ]
