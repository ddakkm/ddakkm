from pydantic import EmailStr
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, BackgroundTasks

from app import crud, schemas, models
from app.core.config import settings
from app.controllers import deps
from app.utils.smpt import email_sender

router = APIRouter()


@router.post("/{comment_id}")
async def create_nested_comment(
        comment_id: int,
        comment_in: schemas.CommentCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
) -> models.Comment:
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
) -> models.Comment:
    """
    <h1> 코멘트를 삭제합니다. </h1> </br>
    </br>
    Path Parameter 로 입력된 코멘트가 없는 경우 404 에러를 반환합니다.
    """
    db_obj = crud.comment.get_comment(db, comment_id)
    return crud.comment.set_comment_status_as_deleted(db, db_obj=db_obj, current_user=current_user)


# TODO : 백그라운드 테스크 celery 로 변경
# TODO : 신고사유 추가
@router.post("/{comment_id}/report")
async def report_comment(
        comment_id: int,
        background_task: BackgroundTasks,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
) -> dict:
    """
    <h1> 댓글을 신고합니다. </h1> </br>
    신고 목록을 관리하는 DB를 따로 구현하지 않아, ddakkm@kakao.com 이메일 계정으로 신고 내역이 전달됩니다. </br>
    comment_id: 신고하려는 댓글 id </br>
    </br>
    </br>
    파라미터로 넘어온 코멘트 id 에 해당하는 댓글이 존재하지 않는 경우, 404에러를 반환합니다. (성공시 200)
    """
    subject = f"[ddakkm 댓글 신고] 댓글 ID {comment_id}"
    comment_content = crud.comment.get_comment(db, comment_id).content
    text = f"""
    신고 댓글 내용: {comment_content}
    신고자_ID: {current_user.id}
    신고자_닉네임: {current_user.nickname}
    """
    background_task.add_task(email_sender, subject=subject, text=text, to=EmailStr(settings.SMTP_USER))
    return {"mail_subject": subject, "status": "이메일 처리 작업이 Background Worker 에게 정상적으로 전달되었습니다."}
