# Generated by Django 3.0.5 on 2020-09-23 10:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_admintransaction'),
    ]

    operations = [
        migrations.RenameField(
            model_name='admintransaction',
            old_name='admin',
            new_name='user',
        ),
        migrations.RemoveField(
            model_name='admintransaction',
            name='refunded',
        ),
    ]
