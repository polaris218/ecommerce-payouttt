# Generated by Django 3.0.5 on 2020-07-14 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_dwollaaccount'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='return_address',
            field=models.TextField(blank=True, null=True),
        ),
    ]
