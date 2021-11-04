from typing import TypeVar, List

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.reviews import ReviewKeyword

CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDReviewKeyword(CRUDBase[ReviewKeyword, CreateSchemaType, UpdateSchemaType]):
    def bulk_create(self, db: Session, review_id: int, keywords: List[str]):
        keywords = [self.model(review_id=review_id, keyword=keyword) for keyword in keywords]
        db_obj = db.bulk_save_objects(keywords)
        db.flush()
        return db_obj


review_keyword = CRUDReviewKeyword(ReviewKeyword)
