from sqlalchemy.orm import Session
from fastapi import HTTPException

from app import crud, schemas
from app.crud.base import CRUDBase
from app.models.users import User
from app.models.user_like import UserLike
from app.schemas.user_like import UserCreate, UserUpdate


class CRUDUserLike(CRUDBase[UserLike, UserCreate, UserUpdate]):
    def change_user_like_review_status(self, db: Session, current_user: User, review_id: int) -> schemas.BaseResponse:
        review = crud.review.get_review(db, id=review_id)
        if not review:
            raise HTTPException(404, "좋아요 할 리뷰를 찾을 수 없습니다.")

        # 이미 좋아요 한 상태면 좋아요 기록 삭제
        check_like = db.query(self.model).\
            filter(self.model.user_id == current_user.id).filter(self.model.review_id == review_id).first()
        if check_like:
            db.delete(check_like)
            review.like_count -= 1
            db.add(review)
            db.commit()
            db.refresh(review)
            response = schemas.BaseResponse(
                object=review_id, message=f"리뷰 ID : #{review_id}에 대해 회원 ID : #{current_user.id}가 좋아요를 취소했습니다."
            )
            return response

        # 좋아요 안한 상태면 좋아요 기록 생성
        else:
            db_obj = self.model(user_id=current_user.id, review_id=review_id)
            review.like_count += 1
            db.add(review)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            response = schemas.BaseResponse(
                object=review_id, message=f"리뷰 ID : #{review_id}에 대해 회원 ID : #{current_user.id}가 좋아요하였습니다."
            )
            return response

    def get_like_review_list_by_current_user(self, db: Session, current_user: User):
        return [review_id_set[0] for review_id_set
                in db.query(self.model.review_id).filter(self.model.user_id == current_user.id).all()]

    def get_like_counts_by_user_id(self, db: Session, user_id: int) -> int:
        counts = db.query(self.model).filter(self.model.user_id == user_id).count()
        return counts

    def get_review_id_by_user_id(self, db: Session, user_id: int):
        result = db.query(self.model.review_id).\
            filter(self.model.user_id == user_id).group_by(self.model.review_id).all()
        return result


user_like = CRUDUserLike(UserLike)
