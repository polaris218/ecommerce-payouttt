# Generated by Django 3.0.5 on 2020-05-07 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20200507_1719'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shoesize',
            name='country',
            field=models.CharField(choices=[('USA', 'USA'), ('UK', 'UK'), ('EU', 'EU'), ('CM', 'CM')], default='UK', max_length=50),
        ),
    ]
