from typing import Any

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import EmailStr

from app.core.config import settings
from app.controllers import deps
from app.utils.smpt import email_sender
from app.utils.review import symtom_randomizer
from app import crud, schemas, models

router = APIRouter()


@router.post("")
async def create_review(
        *,
        db: Session = Depends(deps.get_db),
        review_in: schemas.ReviewCreate,
        current_user: models.User = Depends(deps.get_current_user)
) -> Any:
    """
    <h1> 리뷰를 생성합니다. </h1> </br>
    리뷰에는 항상 A 형식의 설문지가 포함되어야 합니다. </br>
    __*파라미터 설명__
    |파라미터|타입|내용|
    |-----|---|---|
    |images|json|이미지 url을 json 형식으로 받습니다. 본 파라미터는 Optional 파라미터로, 첨부 이미지가 없는 경우 필수값이 아닙니다. </br> 이미지가 있다면 최소 한개 이미지의 url은 보내야 합니다.|
    |survey|json|백신 후기 설문의 상세 내용을 받습니다.|
    |survey > vaccine_type|enum(string)|"ETC" , "PFIZER", "AZ", "MODERNA", "JANSSEN"|
    |survey > vaccine_round|enum(string)|"FIRST", "SECOND", "THIRD"|
    |survey > date_from|enum(string)| 백신을 맞은지 얼마나 지났는가에 대한 데이터로 "ZERO_DAY", "TWO_DAY", "THREE_DAY", "OVER_FIVE", "OVER_WEEK", "OVER_MONTH" 의 값을 받습니다.|
    |survey > data|json|설문조사에 대한 응답입니다. [설문 예시](https://www.notion.so/2ee64bf1b8a04e61b4a2bc01f076d686) 를 참고했습니다. </br> "q2_1"은 "q2" 가 1일때는 포함되어서는 안됩니다.|
    </br>
    </br>
    <h2>TODO: 리뷰 작성시 키워드 설정하는 부분은 기획 확정되면 넣을 예정 </h2> </br>
    __자세한 내용은 하단 Schema 버튼을 눌러 참고해주세요.__
    """
    return crud.review.create_by_current_user(db, obj_in=review_in, user_id=current_user.id)


@router.get("", response_model=schemas.PageResponse)
async def get_reviews(
        *,
        db: Session = Depends(deps.get_db),
        page_request: dict = Depends(deps.get_page_request),
        filters: dict = Depends(deps.review_params)
) -> schemas.PageResponse:
    """
    <h1> 메인 페이지를 위해 리뷰 리스트를 불러옵니다. </h1> </br>
    pagination이 구현되어있어, "page_meta"에 페이지 네이션에 대한 정보가 기록되어 옵니다.  </br>
    필터를 적용하였으며, 각 필터값에 해당하는 Query parameter를 안보내면 기본적으로 전체값을 리턴합니다. </br>
    </br>
    __*예시__ </br>
    /v1/review -> 검색이나 필터링 없이 전체 리뷰 반환 </br>
    /v1/review?q=아파요 -> "아파요" 라는 본문 내용을 포함하는 전체 리뷰 반환 </br>
    /v1/review?q=아파요&is_crossed=false -> "아파요" 라는 본문 내용을 포함하며 교차접종이 아닌 전체 리뷰 반환
    """
    query = crud.review.get_list_paginated(db, page_request, filters)
    review_list = [schemas.ReviewResponse(
        id=review.id,
        images=review.images,
        user_id=review.user_id,
        nickname=review.user.nickname,
        vaccine_round=review.survey.vaccine_round,
        vaccine_type=review.survey.vaccine_type,
        symptom=symtom_randomizer(review.survey.data),
        content=review.content,
        like_count=review.like_count,
        comment_count=len(review.comments)
    ) for review in query.get("contents")]
    return schemas.PageResponse(
        page_meta=query.get("page_meta"),
        contents=review_list
    )


@router.patch("/{review_id}")
async def edit_review(
        review_id: int,
        review_in: schemas.ReviewUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
) -> models.Review:
    """
    <h1> 사용자가 게시한 리뷰를 수정합니다. </h1> </br>
    <h2> TODO : 기획 내용에 맞게 설문조사 수정 가능여부 확인 후 반영
    </h2>
    """
    db_obj = crud.review.get_review(db, id=review_id)
    return crud.review.update_review(db, db_obj=db_obj, obj_in=review_in, current_user=current_user)


@router.delete("/{review_id}")
async def delete_review(
        review_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
) -> models.Review:
    """
    <h1> 게시글의 상태를 삭제됨으로 변경합니다.</h1> </br>
    삭제 상태의 게시글은 리스트에 표현되지 않으며, 상세 정보 조회가 불가능합니다.
    슈퍼 유저는 본인이 작성한 게시글이 아니어도 삭제할 수 있습니다.
    """
    db_obj = crud.review.get_review(db, id=review_id)
    return crud.review.set_review_status_as_deleted(db, db_obj=db_obj, current_user=current_user)


# TODO : 백그라운드 테스크 celery 로 변경
@router.post("/{review_id}/report")
async def report_review(
        review_id: int,
        background_task: BackgroundTasks,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
) -> Any:
    """
    <h1> 리뷰를 신고합니다. </h1> </br>
    신고 목록을 관리하는 DB를 따로 구현하지 않아, ddakkm@kakao.com 이메일 계정으로 신고 내역이 전달됩니다. </br>
    review_id: 신고하려는 리뷰 id </br>
    </br>
    </br>
    파라미터로 넘어온 리뷰 id 에 해당하는 리뷰가 존재하지 않는 경우, 404에러를 반환합니다. (성공시 200)
    """
    subject = f"[ddakkm 리뷰 신고] 게시글 ID {review_id}"
    review_content = crud.review.get_review(db, review_id).content
    text = f"""
    신고 게시글 내용: {review_content}
    신고자_ID: {current_user.id}
    신고자_닉네임: {current_user.nickname}
    """
    background_task.add_task(email_sender, subject=subject, text=text, to=EmailStr(settings.SMTP_USER))
    return {"mail_subject": subject, "status": "이메일 처리 작업이 Background Worker 에게 정상적으로 전달되었습니다."}


@router.post("/{review_id}}/comment")
async def create_comment(
        review_id: int,
        comment_in: schemas.CommentCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
):
    """
    <h1> 리뷰에 코멘트를 추가합니다. </h1> </br>
    </br>
    댓글 내용은 {"content": "댓글 내용"} <- 형식의 json Body로 받고,  </br>
    글을 작성하고자 하는 review_id 를 Path Parameter 로 받습니다.
    """
    return crud.comment.create_by_current_user(db, obj_in=comment_in, current_user=current_user, review_id=review_id)
