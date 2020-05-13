# Generated by Django 3.0.5 on 2020-05-12 00:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_user_date_of_birth'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='stripe_customer_id',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='stripe_payment_method',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]