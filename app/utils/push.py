import json

import requests
from typing import List

from app.core.config import settings


def send_push(title: str, body: str, tokens: str) -> None:
    headers = {
        "Authorization": f"Bearer {settings.FCM_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "data": {
            "body": "asd",
            "title": "asd"
        },
        "token": tokens,
    }
    test = {
        "message": {
            "token": "3f5db3999e8b2105",
            "notification": {
                "body": "This is an FCM notification message!",
                "title": "FCM Message"
            }
        }
    }
    response = requests.post('https://fcm.googleapis.com/v1/projects/myproject-b5ae1/messages:send', data=json.dumps(test), headers=headers)
    print(response.json())


if __name__ == "__main__":
    send_push("a", "a", "3f5db3999e8b2105")

