# Generated by Django 5.0.4 on 2024-04-15 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sss_app', '0006_remove_orderitem_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='total_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
