# Generated by Django 3.0.5 on 2020-07-29 11:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0012_auto_20200617_0920'),
    ]

    operations = [
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buyer', to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Product')),
                ('shoe_size', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.ShoeSize')),
            ],
        ),
        migrations.CreateModel(
            name='SuggestProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_valid', models.BooleanField(default=False)),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CartModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_valid', models.BooleanField(default=False)),
                ('paid', models.BooleanField(default=False)),
                ('transaction_id', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('PENDING', 'PENDING'), ('PAID', 'PAID'), ('DISPATCH', 'DISPATCH'), ('DELIVERED', 'DELIVERED')], default='PENDING', max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('cart_item', models.ManyToManyField(blank=True, null=True, to='api.CartItem')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
