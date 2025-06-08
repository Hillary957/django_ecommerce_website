from django.conf import settings
from decouple import config

# paypal_credentials.py
PAYPAL_CLIENT_ID = config('PAYPAL_CLIENT_ID')
PAYPAL_SECRET= config('PAYPAL_SECRET')
