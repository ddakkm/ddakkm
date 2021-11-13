import json

import requests
from typing import List

from app.core.config import settings


def send_push(title: str, body: str, tokens: List[str]) -> None:
    headers = {
        "Authorization": f"key={settings.FIREBASE_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "data": {
            "body": "asd",
            "title": "asd"
        },
        "registration_ids": tokens,
    }
    response = requests.post('https://fcm.googleapis.com/fcm/send', data=json.dumps(data), headers=headers)
