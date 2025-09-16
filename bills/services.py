import base64
import datetime
import hashlib
import hmac
import random
import string
import time

from dotenv import load_dotenv
from flask import cli
import requests
import os

load_dotenv()


def generate_keys():
    # Get auth key from environment variable
    auth_key = os.getenv('EKO_AUTH_KEY')

    # Encode it using base64
    encoded_key = base64.b64encode(auth_key.encode()).decode()

    secret_key_timestamp = int(round(time.time() * 1000))

    signature = hmac.new(encoded_key.encode(), str(
        secret_key_timestamp).encode(), hashlib.sha256).digest()

    # Encode it using base64
    secret_key = base64.b64encode(signature).decode()

    return secret_key, secret_key_timestamp


def fetch_bills_from_eko(payload):
    url = f"https://api.eko.in:25002/ekoicici/v2/billpayments/fetchbill?initiator_id={os.getenv('EKO_INITIATOR_ID')}"

    secret_key, secret_key_timestamp = generate_keys()

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    random_chars = ''.join(random.choices(
        string.ascii_uppercase + string.digits, k=6))
    client_ref_id = timestamp + random_chars

    if len(client_ref_id) > 20:
        client_ref_id = client_ref_id[:20]
    elif len(client_ref_id) < 5:
        client_ref_id += ''.join(random.choices(string.ascii_uppercase + string.digits,
                                                k=5-len(client_ref_id)))

    headers = {
        'developer_key': os.getenv('EKO_DEVELOPER_KEY'),
        'secret-key': secret_key,
        'secret-key-timestamp': str(secret_key_timestamp),
        'Content-Type': 'application/json',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/3.9.0'
    }

    response = requests.request("POST",
                                url,
                                headers=headers,
                                json={**payload, "client_ref_id": client_ref_id, "user_code": os.getenv('EKO_USER_CODE')})

    return response.json()
