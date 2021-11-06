from typing import TypeVar, List

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import crud
from app.crud.base import CRUDBase
from app.models.reviews import ReviewKeyword
from app.models.users import User

CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDReviewKeyword(CRUDBase[ReviewKeyword, CreateSchemaType, UpdateSchemaType]):
    def bulk_create(self, db: Session, review_id: int, keywords: List[str]):
        keywords = [self.model(review_id=review_id, keyword=keyword) for keyword in keywords]
        db_obj = db.bulk_save_objects(keywords)
        db.flush()
        return db_obj

    # def bulk_update(self, db: Session, review_id: int, keywords: List[str]):
    #     # 기존의 키워드
    #     original_keywords = crud.review.get_review(db=db, id=review_id).keywords
    #     k = [for orginal_keyword in original_keywords]


review_keyword = CRUDReviewKeyword(ReviewKeyword)
