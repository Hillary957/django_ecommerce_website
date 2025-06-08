import requests
import json
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
import base64
from django.conf import settings

class MpesaAccessToken:
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    access_token = None
    token_expiry = None

    @classmethod
    def validated_mpesa_access_token(cls):
        # If token exists and is still valid, return it
        if cls.access_token and cls.token_expiry and datetime.now() < cls.token_expiry:
            return cls.access_token
        
        # Request a new token
        response = requests.get(cls.api_URL, auth=HTTPBasicAuth(cls.consumer_key, cls.consumer_secret))
        
        if response.status_code == 200:
            cls.access_token = response.json().get('access_token')
            cls.token_expiry = datetime.now() + timedelta(seconds=3500)  # Token lasts ~3600s
            return cls.access_token
        else:
            print("Failed to get access token. Check your credentials.")
            return None

        

class LipanaMpesaPassword:
    lipa_time = datetime.now().strftime('%Y%m%d%H%M%S')
    Business_short_code = "174379"
    passkey = settings.MPESA_PASSKEY
    data_to_encode = Business_short_code + passkey + lipa_time
    online_password = base64.b64encode(data_to_encode.encode())
    decode_password = online_password.decode('utf-8')




























# import requests
# import json
# from requests.auth import HTTPBasicAuth
# from datetime import datetime
# import base64
# from django.conf import settings

# class MpesaAccessToken:
#     consumer_key = settings.MPESA_CONSUMER_KEY
#     consumer_secret =  settings.MPESA_CONSUMER_SECRET
#     api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

#     @classmethod
#     def validated_mpesa_access_token(cls):
#         response = requests.get(cls.api_URL, auth=HTTPBasicAuth(cls.consumer_key, cls.consumer_secret))
#         print("Response Status Code:", response.status_code)
#         print("Response Text:", response.text)  # <-- This will show the full response
        
#         if response.status_code == 200:
#             mpesa_access_token = response.json().get('access_token')
#             print("Access Token:", mpesa_access_token)
#             return mpesa_access_token
#         else:
#             print("Failed to get access token. Check your credentials.")
#             return None


# class LipanaMpesaPassword:
#     lipa_time = datetime.now().strftime('%Y%m%d%H%M%S')
#     Business_short_code = "174379"
#     passkey =settings.MPESA_PASSKEY
#     data_to_encode = Business_short_code + passkey + lipa_time
#     online_password = base64.b64encode(data_to_encode.encode())
#     decode_password = online_password.decode('utf-8')