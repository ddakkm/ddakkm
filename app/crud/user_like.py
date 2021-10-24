from sqlalchemy.orm import Session
from fastapi import HTTPException

from app import crud
from app.crud.base import CRUDBase
from app.models.users import User
from app.models.user_like import UserLike
from app.schemas.user_like import UserCreate, UserUpdate


class CRUDUserLike(CRUDBase[UserLike, UserCreate, UserUpdate]):
    def change_user_like_review_status(self, db: Session, current_user: User, review_id: int):
        review = crud.review.get_review(db, id=review_id)
        if not review:
            raise HTTPException(404, "좋아요 할 리뷰를 찾을 수 없습니다.")

        # 이미 좋아요 한 상태면 좋아요 기록 삭제
        check_like = db.query(self.model).\
                filter(self.model.user_id == current_user.id).filter(self.model.review_id == review_id).first()
        review_obj = crud.review.get_review(db, id=review_id)
        if check_like:
            db.delete(check_like)
            review_obj.like_count -= 1
            db.add(review_obj)
            db.commit()
            db.refresh(review_obj)
            status = {"status": "ok", "detail": f"사용자 {check_like.user_id}가 리뷰 {check_like.review_id}에 대한 좋아요를 취소했습니다."}
            return status

        # 좋아요 안한 상태면 좋아요 기록 생성
        else:
            db_obj = self.model(user_id=current_user.id, review_id=review_id)
            review_obj.like_count += 1
            db.add(review_obj)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj

    def get_like_review_list_by_current_user(self, db: Session, current_user: User):
        return [review_id_set[0] for review_id_set
                in db.query(self.model.review_id).filter(self.model.user_id == current_user.id).all()]

    def get_like_counts_by_user_id(self, db: Session, user_id: int) -> int:
        counts = db.query(self.model).filter(self.model.user_id == user_id).count()
        return counts


user_like = CRUDUserLike(UserLike)
