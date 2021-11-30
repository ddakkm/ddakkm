from typing import List

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.qna import Qna
from app.schemas.page_response import paginated_query
from app.schemas.qna import QnaCreate, QnaUpdate


class CRUDQna(CRUDBase[Qna, QnaCreate, QnaUpdate]):
    def get_list_pagenated(self, db: Session, page_request: dict) -> List[Qna]:
        query = db.query(self.model)
        page = page_request.get("page", 1)
        size = page_request.get("size", 20)
        return paginated_query(
            page_request,
            query,
            lambda x: x.order_by(self.model.created_at.desc()).limit(size).offset((page - 1) * size).all()
        )


qna = CRUDQna(Qna)
