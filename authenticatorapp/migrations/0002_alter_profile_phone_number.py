# Generated by Django 5.1.6 on 2025-03-05 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authenticatorapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='phone_number',
            field=models.CharField(default='1234567890', max_length=15, unique=True),
        ),
    ]
