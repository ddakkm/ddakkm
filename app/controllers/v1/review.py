from typing import Any, Union, List

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, BackgroundTasks, Body
from fastapi.encoders import jsonable_encoder
from pydantic import EmailStr

from app.core.config import settings
from app.controllers import deps
from app.utils.smpt import email_sender
from app.utils.comment import comment_model_to_dto
from app.utils.review import symtom_randomizer
from app import crud, schemas, models

router = APIRouter()


@router.post("")
async def create_review(
        *,
        db: Session = Depends(deps.get_db),
        review_in: schemas.ReviewCreate = Body(None, examples=schemas.survey_details_example),
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
    |survey > survey_type|enum(string)|"A", "B", "C"|
    |survey_details > vaccine_type|enum(string)|"ETC" , "PFIZER", "AZ", "MODERNA", "JANSSEN"|
    |survey_details > vaccine_round|enum(string)|"FIRST", "SECOND", "THIRD"|
    |survey_details > date_from|enum(string)| 백신을 맞은지 얼마나 지났는가에 대한 데이터로 "ZERO_DAY", "TWO_DAY", "THREE_DAY", "OVER_FIVE", "OVER_WEEK", "OVER_MONTH" 의 값을 받습니다.|
    |survey_details > data > q1| 1~7 범위의 정수 + 문자열의 배열| 근육통에 대한 설문입니다. (피그마 설문A그룹참조) </br> 1~7 범위를 벗어난 정수가 배열에 있거나, 8개 이상의 인자가 배열에 있을 경우 에러를 반환합니다.|
    |survey_details > data > q2| 1~6 범위의 정수 | 발열에 대한 설문입니다. 여기서 1번을 택한 경우 발열 증상이 없다는 뜻이기 떄문에, </br> 발열 증상의 지속 기간에 대해 묻는 "q2_1" 은 빈 값을 줘야 합니다. 그렇지 않으면 에러를 반환합니다.|
    |survey_details > data > q2_1| 1~4 범위의 정수 | 발열 증상의 지속 기간에 대한 설문입니다. </br> "q2" 에서 1을 입력한 경우 이 파라미터는 비어있어야 합니다.|
    |survey_details > data > q3~q5 |TODO|TODO|
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
        filters: dict = Depends(deps.review_params),
        current_user: Union[models.User, None] = Depends(deps.get_current_user_optional)
) -> schemas.PageResponse:
    """
    <h1> 메인 페이지를 위해 리뷰 리스트를 불러옵니다. </h1> </br>
    __로그인 액세스 토큰 없이(비회원도) 접근 가능한 API 입니다.__ </br> </br>
    pagination이 구현되어있어, "page_meta"에 페이지 네이션에 대한 정보가 기록되어 옵니다.  </br>
    필터를 적용하였으며, 각 필터값에 해당하는 Query parameter를 안보내면 기본적으로 전체값을 리턴합니다. </br>
    로그인 한 유저 (Reqeust Header > Authorization에 Access Token을 넣어 요청하는 경우)는 "user_is_like"
    파라미터를 통해 내가 좋아요 한 리뷰인지의 여부를 알 수 있습니다. </br>
    </br>
    __*예시__ </br>
    /v1/review -> 검색이나 필터링 없이 전체 리뷰 반환 </br>
    /v1/review?q=아파요 -> "아파요" 라는 본문 내용을 포함하는 전체 리뷰 반환 </br>
    /v1/review?q=아파요&is_crossed=false -> "아파요" 라는 본문 내용을 포함하며 교차접종이 아닌 전체 리뷰 반환
    """
    # 로그인 상태면 현재 유저의 좋아요 기록 불러오기 / 로그인 상태가 아니면 좋아요 기록은 비어있음
    try:
        user_like_list = crud.user_like.get_like_review_list_by_current_user(db, current_user)
    except AttributeError as e:
        user_like_list = []

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
        comment_count=len(review.comments),
        user_is_like=review.id in user_like_list
    ) for review in query.get("contents")]
    return schemas.PageResponse(
        page_meta=query.get("page_meta"),
        contents=review_list
    )


@router.get("/{review_id}", response_model=schemas.Review)
async def get_review_details(
        review_id: int,
        db: Session = Depends(deps.get_db),
        current_user: Union[models.User, None] = Depends(deps.get_current_user_optional)
) -> schemas.Review:
    """
    <h1> 요청한 id에 해당하는 리뷰의 상세 정보를 반환합니다. </h1> </br>
    __로그인 액세스 토큰 없이(비회원도) 접근 가능한 API 입니다.__ </br> </br> </br>
    __*파라미터 설명__
    |파라미터|타입|내용|
    |------|---|--|
    |id|int|review의 id값|
    |user_id|int|작성자의 id값|
    |nickname|string|작성자의 닉네임|
    |content|string|리뷰내용|
    |images|object|첨부 이미지 url (*없는 url에는 null 리턴)|
    |survey|object|설문지 타입과 설문 내용 (*리뷰에는 설문 타입 A만 리턴됩니다. 설문 내용은 리뷰 생성/가입설문 A의 설문 양식과 동일합니다.)|
    |is_writer|bool|로그인 사용자가 작성자인지 아닌지를 판별 (*글 작성자가 자기의 글을 볼 때 이 값이 true로 리턴됩니다.)|
    |comment|list of objects|comment 리스트를 반환|

    __*comment object 파라미터 설명__
    |파라미터|타입|내용|
    |------|---|--|
    |id|int|comment의 id값|
    |user_id|int|작성자의 id값|
    |nickname|string|작성자의 닉네임|
    |content|string|댓글 내용|
    |nested_comment|list of objects|댓글의 댓글 리스트|
    <h2> TODO : 태그 관련 기능
    </h3>
    """
    # 비회원인 경우 id 값이 없기 때문에, 작성자인지 여부를 판별할 수 없음 -> 이에 따라 임시 orm 모델로 변환시켜줌
    if current_user is None:
        current_user = models.User(id=0)
    review_obj = crud.review.get_review_details(db=db, review_id=review_id)
    delattr(review_obj.survey, "id")
    review_details = schemas.Review(
        id=review_obj.id,
        content=review_obj.content,
        images=review_obj.images,
        user_id=review_obj.user_id,
        survey=schemas.Survey(survey_type=schemas.SurveyType.A, survey_details=jsonable_encoder(review_obj.survey)),
        is_writer=review_obj.user_id == current_user.id,
        nickname=review_obj.user.nickname,
        comments=comment_model_to_dto(review_obj.comments)
    )
    return review_details


@router.patch("/{review_id}")
async def edit_review(
        review_id: int,
        review_in: schemas.ReviewUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
) -> models.Review:
    """
    <h1> 사용자가 게시한 리뷰를 수정합니다. </h1> </br>
    <h2> TODO : 삭제한 리뷰 수정 못하게
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
    슈퍼 유저는 본인이 작성한 게시글이 아니어도 삭제할 수 있습니다. </br>
    <h2> TODO: 이미 삭제된 리뷰인 경우 반환값 조정 필요
    </h2>
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
) -> dict:
    """
    <h1> 리뷰를 신고합니다. </h1> </br>
    신고 목록을 관리하는 DB를 따로 구현하지 않아, ddakkm@kakao.com 이메일 계정으로 신고 내역이 전달됩니다. </br>
    review_id: 신고하려는 리뷰 id </br>
    </br>
    </br>
    파라미터로 넘어온 리뷰 id 에 해당하는 리뷰가 존재하지 않는 경우, 404에러를 반환합니다. (성공시 200) </br>
    <h2>
    TODO: 삭제한 리뷰 신고 못하게
    </h2>
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
) -> models.Comment:
    """
    <h1> 리뷰에 코멘트를 추가합니다. </h1> </br>
    </br>
    댓글 내용은 {"content": "댓글 내용"} <- 형식의 json Body로 받고,  </br>
    글을 작성하고자 하는 review_id 를 Path Parameter 로 받습니다. </br>
    <h2>
    TODO: 삭제한 리뷰 댓글 못달게
    </h2>
    """
    return crud.comment.create_by_current_user(db, obj_in=comment_in, current_user=current_user, review_id=review_id)


@router.post("/{review_id}/like_status")
async def change_review_like_status(
        review_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
) -> Union[models.UserLike, dict]:
    """
    <h1> 게시글에 대한 좋아요 상태를 변경합니다. </h1> </br>
    성공시 200 을 반환합니다. </br>
    잘못된 Path Parameter로 요청할 경우 (= 없는 리뷰의 id로 요청할 경우) 404 에러를 반환합니다. </br>
    좋아요를 한 회원이 본 API 를 호출하면, 좋아요가 취소됩니다. -> {"status": "ok", "details": "취소에 대한 상세 내역"} 형태의 json을 반환합니다. </br>
    좋아요를 하지 않은 회원이 본 API 를 호출하면, 리뷰에 대한 좋아요가 등록됩니다. -> 생성된 모델을 반환 </br>
    </br>
    <h2>_PS. 빠르게 만들기 위해 하나의 API로 좋아요/좋아요 취소를 모두 처리하도록 했습니다. 혹시 클라에서 분기가 불편해지거나 하면 말해주세요 그냥 2개로 나눌께요_</h2>
    """
    return crud.user_like.change_user_like_review_status(db, current_user=current_user, review_id=review_id)
