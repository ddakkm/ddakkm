import sys
sys.path.append("..")
import json
import logging

import requests
from sqlalchemy.orm import Session, joinedload

from .. import models, const

logger = logging.getLogger('ddakkm_logger')


# 여기선 유저 fcm token
class PushController:
    def __init__(self,
                 push_type: str,
                 title: str,
                 body: str,
                 db: Session):
        if push_type == "keyword":
            self.type = "keyword",
        elif push_type == "activity":
            self.type = "activity"
        else:
            raise Exception("지원하지 않는 메시지 타입입니다.")
        self.target_users = []
        self.target_users_fcm_token = []
        self.title = title
        self.body = body
        self.db = db

    def __set_users_fcm_token(self):
        users = self.db.query(models.User).filter(models.User.id.in_(self.target_users)).all()
        self.target_users_fcm_token = [user.fcm_token for user in users]

    def send_push(self) -> bool:
        self.__set_users_fcm_token()
        headers = {
            "Authorization": f"Key={const.FCM_API_KEY}",
            "Content-Type": "application/json",
        }
        data = {
            "notification": {
                "title": self.title,
                "body": self.body,
                "click_action": "asd"
            },
            "data": {
            },
            "registration_ids": self.target_users_fcm_token,
        }
        response = requests.post('https://fcm.googleapis.com/fcm/send', data=json.dumps(data), headers=headers)
        print(response.content)
        if response.status_code != 200:
            logger.warning(f"푸시 메시지 발송에 실패하였습니다. {response.json()}")
            return False
        else:
            logger.info(f"푸시 메시지 발송에 성공했습니다. {response.json()}")
            return True


class KeywordPushController(PushController):
    def __init__(self, review_id: int, title: str, body: str, db: Session):
        super().__init__(
            push_type="keyword",
            title=title,
            body=body,
            db=db,
        )
        self.review_id = review_id
        self.keyword_list = []

    # 키워드 리스트를 좋아하는 유저 아이디를 클래스 속성에 할당
    def __set_target_users_id_list(self):
        db = self.db
        self.__set_keyword_list_from_review()
        target_users = db.query(models.User).join(models.UserKeyword).options(joinedload(models.User.keywords))\
            .filter(models.UserKeyword.keyword.in_(self.keyword_list)).all()
        self.target_users = [user.id for user in target_users]

    # 입력된 리뷰 아이디에서 키워드 리스트를 불러옴
    def __set_keyword_list_from_review(self):
        db = self.db
        review_keywords = db.query(models.ReviewKeyword).filter(models.ReviewKeyword.review_id == self.review_id).all()
        self.keyword_list = [review.keyword for review in review_keywords]

    def send_push(self):
        self.__set_target_users_id_list()
        super(KeywordPushController, self).send_push()
        # logging
        logger.info(
            f"타겟키워드 : {self.keyword_list}, "
            f"푸시 발송 유저 : {self.target_users}, "
            f"푸시 제목 : {self.title}, "
            f"푸시 내용 : {self.body}"
        )
