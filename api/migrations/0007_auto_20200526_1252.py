# Generated by Django 3.0.5 on 2020-05-26 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20200526_1239'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bidpayment',
            name='buyer_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='bidpayment',
            name='success_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
