import logging
from typing import TypeVar, List

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.users import UserKeyword
from app.schemas.response import BaseResponse
from app.schemas.keyword import UserKeywordUpdate

CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)

logger = logging.getLogger('ddakkm_logger')


class CRUDUserKeyword(CRUDBase[UserKeyword, CreateSchemaType, UserKeywordUpdate]):
    def get_keywords_by_user_id(self, db: Session, user_id: int):
        return db.query(self.model.keyword).filter(self.model.user_id == user_id).all()

    def bulk_update(self, db: Session, user_id: int, keywords: List[str], original_keywords: List[str]):
        original_keywords_model = original_keywords
        original_keywords = [dict(keyword).get("keyword") for keyword in original_keywords_model]

        to_delete = [original_keyword for original_keyword in original_keywords if original_keyword not in keywords]
        [self.__delete_by_keyword(db=db, user_id=user_id, keyword=keyword_to_delete) for keyword_to_delete in to_delete]

        to_insert = [keyword for keyword in keywords if keyword not in original_keywords]
        [self.create(db=db, obj_in=UserKeywordUpdate(user_id=user_id, keyword=keyword_to_insert))
         for keyword_to_insert in to_insert]
        db.flush()
        logger.info(f"삭제할 키워드 : {to_delete}, 추가할 키워드 : {to_insert}")
        return BaseResponse(object=user_id, message=f"유저 ID : #{user_id}의 관심 키워드가 수정되었습니다.")

    def __delete_by_keyword(self, db: Session, user_id: int, keyword: str):
        db_obj = db.query(self.model)\
            .filter(self.model.user_id == user_id).filter(self.model.keyword == keyword).first()
        db.delete(db_obj)
        db.flush()


user_keyword = CRUDUserKeyword(UserKeyword)
