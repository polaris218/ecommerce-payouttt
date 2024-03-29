# Generated by Django 3.0.5 on 2020-08-05 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_cartmodel_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartmodel',
            name='order_note',
            field=models.TextField(blank=True, max_length=700, null=True),
        ),
        migrations.AddField(
            model_name='cartmodel',
            name='shipping_amount',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='cartmodel',
            name='shipping_type',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
