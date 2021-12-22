import json
from typing import List, Optional

import requests
from sqlalchemy.orm import Session, joinedload

from app import models
from app.core.config import settings


def send_push(title: str, body: str, tokens: str) -> None:
    headers = {
        "Authorization": f"Key={settings.FCM_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "notification": {
            "title": title,
            "body": body,
        },
        "data": {
        },
        "registration_ids": tokens,
    }
    response = requests.post('https://fcm.googleapis.com/fcm/send', data=json.dumps(data), headers=headers)
    print(response.json())


# 여기선 유저 fcm token
class PushController:
    def __init__(self,
                 push_type: str,
                 target_users: List[models.User],
                 title: str,
                 body: str,
                 db: Session):
        if push_type == "keyword":
            self.type = "keyword",
        elif push_type == "activity":
            self.type = "activity"
        else:
            raise Exception("지원하지 않는 메시지 타입입니다.")
        self.target_users = self.__get_users_id_list(target_users)
        self.title = title
        self.body = body
        self.db = db

    @classmethod
    def __get_users_id_list(cls, target_users: List[models.User]) -> List[int]:
        return [user.id for user in target_users]

    def _get_users_fcm_token(self):
        users = self.db.query(models.User).filter(models.User.id.in_(self.target_users)).all()
        return [user.fcm_token for user in users]

    def send_push(self):
        print("여기서 푸시알림 발송 로직")


# TODO keywordlist 도 클래스 내부에서 찾아오는 걸로 변경 (keywordlist 속성을 review_id로 변경)
class KeywordPushController(PushController):
    def __init__(self, keywords_list: List[str], title: str, body: str, db: Session):
        super().__init__(
            push_type="keyword",
            target_users=[],
            title=title,
            body=body,
            db=db,
        )
        self.keywords_list = keywords_list

    # 키워드 리스트를 좋아하는 유저 아이디를 클래스 속성에 할당
    def get_target_users_id_list(self):
        db = self.db
        self.target_users = db.query(models.User).join(models.UserKeyword).options(joinedload(models.User.keywords))\
            .filter(models.UserKeyword.keyword.in_(self.keywords_list)).all()

    def get_keyword_list_from_review(self):
        pass

    def send_push(self):
        super(KeywordPushController, self).send_push()
        # logging
        print("여기서 로깅")



if __name__ == "__main__":
    send_push("a", "a",
              "df7bIDt6TtOyw_S8xzPBqe:APA91bGmSRaxkyd1dp_gISJspjuS8xiiVpU3kbCx03k2qHKUB8jj3zzOouRLnZpqLmWLYvyf96NFsAhI8SvaIRLhwb1WoMSTiOh_AfT5LLkkvVa9TM8laK4QE-_OizTAvq2caT9e8gyj")
