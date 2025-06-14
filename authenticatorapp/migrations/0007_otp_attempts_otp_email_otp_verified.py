# Generated by Django 5.1.6 on 2025-04-08 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authenticatorapp', '0006_remove_otp_attempts_remove_otp_last_sent'),
    ]

    operations = [
        migrations.AddField(
            model_name='otp',
            name='attempts',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='otp',
            name='email',
            field=models.EmailField(max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='otp',
            name='verified',
            field=models.BooleanField(default=False),
        ),
    ]
