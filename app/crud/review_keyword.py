from typing import TypeVar, List

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.reviews import ReviewKeyword
from app.schemas.response import BaseResponse
from app.schemas.keyword import ReviewKeywordUpdate

CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)


class CRUDReviewKeyword(CRUDBase[ReviewKeyword, CreateSchemaType, ReviewKeywordUpdate]):
    def get_keywords_by_review_id(self, db: Session, review_id: int):
        return db.query(self.model.keyword).filter(self.model.review_id == review_id).all()

    def bulk_create(self, db: Session, review_id: int, keywords: List[str]):
        keywords = [self.model(review_id=review_id, keyword=keyword) for keyword in keywords]
        db_obj = db.bulk_save_objects(keywords)
        db.flush()
        return db_obj

    def bulk_update(self, db: Session, review_id: int, keywords: List[str]):
        # 같은값은 유지 / 다른값은 삭제 후 재생성 O(N)에 해결
        # 기존의 키워드
        original_keywords_model = self.get_keywords_by_review_id(db=db, review_id=review_id)
        original_keywords = [dict(keyword).get("keyword") for keyword in original_keywords_model]

        # 삭제할 키워드 -> 기존 키워드 중 입력된 키워드에 있는 것
        to_delete = [original_keyword for original_keyword in original_keywords if original_keyword not in keywords]
        [self.__delete_by_keyword(db=db, review_id=review_id, keyword=keyword_to_delete)
         for keyword_to_delete in to_delete]

        # 추가할 키워드 -> 입력된 키워드 중 원래 기존 키워드에 없던 것
        to_insert = [keyword for keyword in keywords if keyword not in original_keywords]
        [self.create(db=db, obj_in=ReviewKeywordUpdate(review_id=review_id, keyword=keyword_to_insert))
         for keyword_to_insert in to_insert]
        db.flush()
        return BaseResponse(object=review_id, message=f"키워드 {len(to_delete)}개 삭제됨 : {to_delete} \n 키워드 {len(to_insert)}개 입력됨 : {to_insert}")

    def __delete_by_keyword(self, db: Session, review_id: int, keyword: str):
        db_obj = db.query(self.model)\
            .filter(self.model.review_id == review_id).filter(self.model.keyword == keyword).first()
        db.delete(db_obj)
        db.flush()


review_keyword = CRUDReviewKeyword(ReviewKeyword)
