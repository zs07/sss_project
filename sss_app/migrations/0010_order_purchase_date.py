# Generated by Django 5.0.4 on 2024-04-15 20:27

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sss_app', '0009_remove_cart_total_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='purchase_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
