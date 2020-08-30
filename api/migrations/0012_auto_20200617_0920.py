# Generated by Django 3.0.5 on 2020-06-17 09:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_bid_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='bid',
            name='sku_number',
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='on_hold',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='bid',
            name='product_to_bid_on',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_selection', to='api.Product'),
        ),
    ]
