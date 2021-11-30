import os, sys
from typing import Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.main import app
from app.test.utils import TestingSessionLocal


client = TestClient(app)


class TestQna:
    host = "v1/qna"
    db: Session = TestingSessionLocal()

    def test_post_qna(self, get_test_user_token: Dict[str, str]):
        json = {
            "content": "fC2R6yexYv",
            "user_email": "fC2R6yexYv@gmail.com",
            "user_phone": "777-8888-9999"
        }
        # Test [POST] /v1/qna
        response = client.post(f"{self.host}", headers=get_test_user_token, json=json)
        self.db.commit()
        self.db.close()
        qna_id = response.json().get("object")
        assert response.status_code == 200
        qna_model = crud.qna.get(self.db, qna_id)
        assert qna_model.content == "fC2R6yexYv"
        assert qna_model.user_email == "fC2R6yexYv@gmail.com"
        assert qna_model.user_phone == "777-8888-9999"
        self.db.delete(qna_model)
        self.db.commit()
        self.db.close()

    def test_get_list(self, get_test_admin_user_tokne: Dict[str, str]):
        response = client.get(f"{self.host}/list", headers=get_test_admin_user_tokne)
        assert response.status_code == 200

    def test_process_status(self, get_test_admin_user_tokne: Dict[str, str]):
        json = {
            "content": "fC2R6yexYv",
            "user_email": "fC2R6yexYv@gmail.com",
            "user_phone": "777-8888-9999"
        }
        # Test [POST] /v1/qna
        response = client.post(f"{self.host}", headers=get_test_admin_user_tokne, json=json)
        self.db.commit()
        self.db.close()
        qna_id = response.json().get("object")
        assert response.status_code == 200

        process_response = client.post(f"{self.host}/{qna_id}/process", headers=get_test_admin_user_tokne)
        assert process_response.status_code == 200
        qna_model = crud.qna.get(self.db, qna_id)
        assert qna_model.is_solved is True
        self.db.delete(qna_model)
        self.db.commit()
        self.db.close()

