from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from app.controllers import deps
from app import crud, schemas, models

router = APIRouter()


@router.post("/{comment_id}")
async def create_nested_comment(
        comment_id: int,
        comment_in: schemas.CommentCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
):
    """
    <h1> 코멘트에 코멘트를 추가합니다. (대댓글) </h1> </br>
    </br>
    댓글 내용은 {"content": "댓글 내용"} <- 형식의 json Body로 받고,  </br>
    글을 작성하고자 하는 review_id 와 대댓글의 comment_id 를 Path Parameter 로 받습니다.
    """
    return crud.comment.create_nested_comment(
        db, obj_in=comment_in, current_user=current_user, comment_id=comment_id)


@router.delete("/{comment_id}")
async def delete_comment(
        comment_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
):
    """
    <h1> 코멘트를 삭제합니다. </h1> </br>
    </br>
    Path Parameter 로 입력된 코멘트가 없는 경우 404 에러를 반환합니다.
    """
    db_obj = crud.comment.get_comment(db, comment_id)
    return crud.comment.set_comment_status_as_deleted(db, db_obj=db_obj, current_user=current_user)