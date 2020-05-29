# Generated by Django 3.0.5 on 2020-05-28 20:12

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_bid_order_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bid',
            name='order_id',
            field=models.CharField(blank=True, default=uuid.uuid4, max_length=100, unique=True),
        ),
    ]