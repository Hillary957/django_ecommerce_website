# Generated by Django 5.1.6 on 2025-03-26 19:23

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ecommerceapp', '0002_courses_remove_services_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('currency', models.CharField(default='USD', max_length=3)),
                ('checkout_id', models.CharField(max_length=100, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('transaction_id', models.CharField(default=uuid.uuid4, max_length=100, unique=True)),
                ('mpesa_code', models.CharField(blank=True, max_length=20, null=True)),
                ('phone_number', models.CharField(max_length=15)),
                ('status', models.CharField(max_length=15)),
                ('timestamp', models.DateField(auto_now_add=True)),
                ('courses', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ecommerceapp.courses')),
                ('service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ecommerceapp.services')),
            ],
        ),
    ]
