from time import sleep
import traceback

from sqlalchemy.orm import Session
from celery import states

from worker import celery
from modules.push.push import KeywordPushController
from modules.db.session import SessionLocal

@celery.task(name='hello.task', bind=True)
def hello_world(self, name):
    try:
        if name == 'error':
            k = 1 / 0
        for i in range(60):
            sleep(1)
            self.update_state(state='PROGRESS', meta={'done': i, 'total': 60})
        return {"result": "hello {}".format(str(name))}
    except Exception as ex:
        self.update_state(
            state=states.FAILURE,
            meta={
                'exc_type': type(ex).__name__,
                'exc_message': traceback.format_exc().split('\n')
            })
        raise ex


@celery.task(name='send_push.task', bind=True)
def send_push(self, review_id: int, title: str, body: str):
    db = SessionLocal()
    kc = KeywordPushController(review_id=review_id, title=title, body=body, db=db)
    kc.send_push()
    self.update_state(state="PROGRESS")
    db.close()
