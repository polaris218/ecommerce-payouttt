# Generated by Django 3.0.5 on 2020-05-03 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bidpayment',
            name='admin_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='bidpayment',
            name='seller_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]