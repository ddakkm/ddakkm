from typing import Union, List

from pydantic import EmailStr
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from fastapi.encoders import jsonable_encoder

from app import crud, schemas, models
from app.core.config import settings
from app.controllers import deps
from app.schemas.comment import Comment
from app.utils.report import get_report_reason
from app.utils.smpt import email_sender
from app.utils.comment import comment_model_to_dto

router = APIRouter()

# TODO POST 결과값에 통일된 응답값 이용


@router.get("/{review_id}", name="리뷰에 속한 댓글 리스트 가져오기", response_model=List[Comment])
async def get_comment_list(
        review_id: int,
        db: Session = Depends(deps.get_db),
        current_user: Union[models.User, None] = Depends(deps.get_current_user_optional)
) -> List[Comment]:
    if current_user is None:
        current_user = models.User(id=0)
    comments = crud.comment.get_comments_by_review_id(db=db, review_id=review_id)
    comment_ids_like_by_user = [
        jsonable_encoder(comment_id).get("comment_id")
        for comment_id in crud.user_comment_like.get_comment_id_by_user_id(db=db, user_id=current_user.id)
    ]
    return comment_model_to_dto(comments, comment_ids_like_by_user)


@router.post("/{comment_id}", name="대댓글 작성")
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


@router.delete("/{comment_id}", name="댓글 삭제")
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
    if db_obj.is_delete is True:
        raise HTTPException(400, "이미 삭제된 코멘트입니다.")
    return crud.comment.set_comment_status_as_deleted(db, db_obj=db_obj, current_user=current_user)


# TODO : 백그라운드 테스크 celery 로 변경
@router.post("/{comment_id}/report", name="댓글 삭제")
async def report_comment(
        comment_id: int,
        reason: schemas.ReportReason,
        background_task: BackgroundTasks,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
) -> dict:
    """
    <h1> 댓글을 신고합니다. </h1> </br>
    신고 목록을 관리하는 DB를 따로 구현하지 않아, ddakkm@kakao.com 이메일 계정으로 신고 내역이 전달됩니다. </br>
    comment_id: 신고하려는 댓글 id </br>
    reason: 1 ~ 4 사이의 int 값 </br>
    __reason 번호별 사유__ </br>
    1. 부적절한 홍보 / 영리 목적 </br>
    2. 욕설 / 반말 / 부적절한 언어 사용 </br>
    3. 도배 / 스팸성 </br>
    4. 분란 유도 </br>
    ex: 신고사유가 "분란유도" 인 경우, body에 4번을 넣어서 보내주세요 </br>
    </br>
    </br>
    파라미터로 넘어온 코멘트 id 에 해당하는 댓글이 존재하지 않는 경우, 404에러를 반환합니다. (성공시 200)
    """
    report_reason = get_report_reason(reason.reason)
    subject = f"[ddakkm 댓글 신고] 댓글 ID {comment_id}"
    comment_content = crud.comment.get_comment(db, comment_id).content
    text = f"""
    신고 댓글 내용: {comment_content}
    신고자_ID: {current_user.id}
    신고자_닉네임: {current_user.nickname}
    신고사유: {report_reason}
    """
    background_task.add_task(email_sender, subject=subject, text=text, to=EmailStr(settings.SMTP_USER))
    return {"mail_subject": subject, "status": "이메일 처리 작업이 Background Worker 에게 정상적으로 전달되었습니다."}


@router.post("/{comment_id}/like_status", name="회원의 댓글에 대한 좋아요 상태 변경")
async def change_comment_like_status(
        comment_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
) -> Union[models.UserCommentLike, dict]:
    """
    <h1> 댓글에 대한 좋아요 상태를 변경합니다. </h1> </br>
    성공시 200 을 반환합니다. </br>
    잘못된 Path Parameter로 요청할 경우 (= 없는 리뷰의 id로 요청할 경우) 404 에러를 반환합니다. </br>
    좋아요를 한 회원이 본 API 를 호출하면, 좋아요가 취소됩니다. -> {"status": "ok", "details": "취소에 대한 상세 내역"} 형태의 json을 반환합니다. </br>
    좋아요를 하지 않은 회원이 본 API 를 호출하면, 리뷰에 대한 좋아요가 등록됩니다. -> 생성된 모델을 반환 </br>
    </br>
    <h2>_PS. 빠르게 만들기 위해 하나의 API로 좋아요/좋아요 취소를 모두 처리하도록 했습니다. 혹시 클라에서 분기가 불편해지거나 하면 말해주세요 그냥 2개로 나눌께요_</h2>
    """
    return crud.user_comment_like.change_user_comment_like_status(db, current_user=current_user, comment_id=comment_id)
