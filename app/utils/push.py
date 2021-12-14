import json

import requests
from typing import List

from app.core.config import settings


def send_push(title: str, body: str, tokens: str) -> None:
    headers = {
        "Authorization": f"Key={settings.FCM_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "data": {
            "body": "asd",
            "title": "asd"
        },
        "to": tokens,
    }
    test = {
        "message": {
            "registration_ids": ["3f5db3999e8b2105"],
            "notification": {
                "body": "This is an FCM notification message!",
                "title": "FCM Message"
            }
        }
    }
    response = requests.post('https://fcm.googleapis.com/fcm/send', data=json.dumps(data), headers=headers)
    print(response.json())


if __name__ == "__main__":
    send_push("a", "a", "3f5db3999e8b2105")

