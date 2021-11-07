from typing import TypeVar, List

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.users import UserKeyword
from app.schemas.response import BaseResponse
from app.schemas.keyword import UserKeywordUpdate

CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)


class CRUDUserKeyword(CRUDBase[UserKeyword, CreateSchemaType, UserKeywordUpdate]):
    def get_keywords_by_user_id(self, db: Session, user_id: int):
        return db.query(self.model.keyword).filter(self.model.user_id == user_id).all()

    def bulk_update(self, db: Session, user_id: int, keywords: List[str]):
        original_keywords_model = self.get_keywords_by_user_id(db=db, user_id=user_id)
        original_keywords = [dict(keyword).get("keyword") for keyword in original_keywords_model]

        to_delete = [original_keyword for original_keyword in original_keywords if original_keyword not in keywords]
        [self.__delete_by_keyword(db=db, user_id=user_id, keyword=keyword_to_delete) for keyword_to_delete in to_delete]

        to_insert = [keyword for keyword in keywords if keyword not in original_keywords]
        [self.create(db=db, obj_in=UserKeywordUpdate(user_id=user_id, keyword=keyword_to_insert))
         for keyword_to_insert in to_insert]
        db.flush()
        return BaseResponse(message=f"키워드 {len(to_delete)}개 삭제됨 : {to_delete} \n 키워드 {len(to_insert)}개 입력됨 : {to_insert}")

    def __delete_by_keyword(self, db: Session, user_id: int, keyword: str):
        db_obj = db.query(self.model)\
            .filter(self.model.user_id == user_id).filter(self.model.keyword == keyword).first()
        db.delete(db_obj)
        db.flush()


user_keyword = CRUDUserKeyword(UserKeyword)
