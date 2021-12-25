import os
from typing import Union, List
import uuid
import logging

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, BackgroundTasks, File, UploadFile, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import EmailStr

from app.core.config import settings
from app.controllers import deps
from app.utils.smpt import email_sender
from app.utils.review import symtom_randomizer, check_is_deleted
from app.utils.storage import s3_client
from app.utils.report import get_report_reason
from app.utils.push import KeywordPushController
from app import crud, schemas, models

router = APIRouter()
logger = logging.getLogger('ddakkm_logger')


@router.post("", name="리뷰 생성", response_model=schemas.BaseResponse)
async def create_review(
        *,
        db: Session = Depends(deps.get_db),
        review_in: schemas.ReviewCreate,
        current_user: models.User = Depends(deps.get_current_user)
) -> schemas.BaseResponse:
    """
    <h1> 리뷰를 생성합니다. </h1> </br>
    리뷰에는 항상 A 형식의 설문지가 포함되어야 합니다. </br>
    __*파라미터 설명__
    |파라미터|타입|내용|
    |-----|---|---|
    |images|json|이미지 url을 json 형식으로 받습니다. 본 파라미터는 Optional 파라미터로, 첨부 이미지가 없는 경우 필수값이 아닙니다. 즉, __"images": null__ 과 같이 요청해도 됩니다.</br> 이미지가 있다면 최소 한개 이미지의 url은 보내야 합니다. </br> __이미지는 review/images API를 활용하여 업로드하고, url 리스트를 받을 수 있습니다.__|
    |keywords|list of string|태그 값을 입력 받습니다. 태그값은 다음의 구글 시트에서 참고하여 문자열 그데로 입력받습니다. [태그값 링크](https://docs.google.com/spreadsheets/d/10zEwbMWdP7f-PsNxSrAGY17noKYGPY_XngC222lNi1s/edit#gid=0/)|
    |survey|json|백신 후기 설문의 상세 내용을 받습니다.|
    |survey > survey_type|enum(string)|"A", "B", "C"|
    |survey_details > vaccine_type|enum(string)|"ETC" , "PFIZER", "AZ", "MODERNA", "JANSSEN"|
    |survey_details > vaccine_round|enum(string)|"FIRST", "SECOND", "THIRD"|
    |survey_details > date_from|enum(string)| 백신을 맞은지 얼마나 지났는가에 대한 데이터로 "ZERO_DAY", "TWO_DAY", "THREE_DAY", "OVER_FIVE", "OVER_WEEK", "OVER_MONTH" 의 값을 받습니다.|
    |survey_details > data > q1| 1~7 범위의 정수 + 문자열의 배열| 근육통에 대한 설문입니다. (피그마 설문A그룹참조) </br> 1~7 범위를 벗어난 정수가 배열에 있거나, 8개 이상의 인자가 배열에 있을 경우 에러를 반환합니다.|
    |survey_details > data > q2| 1~6 범위의 정수 | 발열에 대한 설문입니다. 여기서 1번을 택한 경우 발열 증상이 없다는 뜻이기 떄문에, </br> 발열 증상의 지속 기간에 대해 묻는 "q2_1" 은 빈 값을 줘야 합니다. 그렇지 않으면 에러를 반환합니다.|
    |survey_details > data > q2_1| 1~4 범위의 정수 | 발열 증상의 지속 기간에 대한 설문입니다. </br> "q2" 에서 1을 입력한 경우 이 파라미터는 비어있어야 합니다.|
    __자세한 내용은 하단 Schema 버튼을 눌러 참고해주세요.__
    """
    logger.info(f"리뷰 작성 요청 {jsonable_encoder(review_in)}")
    review_obj = crud.review.create_by_current_user(db, obj_in=review_in, user_id=current_user.id)
    crud.review_keyword.bulk_create(db, review_id=review_obj.id, keywords=review_in.keywords)
    db.commit()
    db.refresh(review_obj)
    response = schemas.BaseResponse(
        object=review_obj.id, message=f"리뷰 ID : #{review_obj.id}가 작성되었습니다."
    )
    kc = KeywordPushController(review_id=review_obj.id, title="관심 키워드 글이 작성되었습니다.", body=review_obj.content, db=db)
    kc.send_push()
    return response


@router.get("", response_model=schemas.PageResponseReviews, name="리뷰 목록 가져오기")
async def get_reviews(
        *,
        db: Session = Depends(deps.get_db),
        page_request: dict = Depends(deps.get_page_request),
        filters: dict = Depends(deps.review_params),
        current_user: Union[models.User, None] = Depends(deps.get_current_user_optional)
) -> schemas.PageResponseReviews:
    """
    <h1> 메인 페이지를 위해 리뷰 리스트를 불러옵니다. </h1> </br>
    __로그인 액세스 토큰 없이(비회원도) 접근 가능한 API 입니다.__ </br> </br>
    pagination이 구현되어있어, "page_meta"에 페이지네이션에 대한 정보가 기록되어 옵니다.  </br>
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
    except AttributeError:
        user_like_list = []

    query = crud.review.get_list_paginated(db, page_request, filters)
    review_list = [schemas.ReviewResponse(
        id=review.id,
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
    return schemas.PageResponseReviews(
        page_meta=query.get("page_meta"),
        contents=review_list
    )


@router.post("/images", response_model=schemas.Images, name="이미지 s3에 등록")
async def create_images(
        files: List[UploadFile] = File(...),
        current_user: Union[models.User, None] = Depends(deps.get_current_user)
) -> schemas.Images:
    """
    <h1> 이미지를 업로드하고, 업로드 된 이미지 url object를 반환받습니다. </h1>
    이미지는 5개까지 업로드 할 수 있으며, files 파라미터에 파일을 넣어 요청하면 됩니다. </br>
    복수 이미지를 업로드하는 예제 코드는 아래를 참조하세요. </br>
    <h2> TODO: 테스트 / 실사용 버킷 개별 구성 & 이미지 리사이징
    </h2>
    ```
    curl -X 'POST' \ \n
      'http://127.0.0.1:8000/v1/review/images' \ \n
      -H 'accept: application/json' \ \n
      -H 'Content-Type: multipart/form-data' \ \n
      -F 'files=@image1.jpeg;type=image/jpeg' \ \n
      -F 'files=@image2.png;type=image/png
    ```
    """
    logger.info(f"{len(files)} 개 이미지 입력")
    if len(files) > 5:
        raise HTTPException(422, "이미지는 5개까지만 첨부할 수 있습니다.")

    # 버킷에 업로드
    [s3_client.upload_fileobj(
        file.file,
        'ddakkm-public',
        f"images/{uuid.uuid5(uuid.NAMESPACE_OID, file.filename)}{os.path.splitext(file.filename)[1]}")
        for file in files]

    # 업로드된 이미지 url 스키마 리턴
    uploaded_files = schemas.Images()
    for i in range(3):
        try:
            setattr(uploaded_files,
                    f"image{i+1}_url",
                    f"https://ddakkm-public.s3.ap-northeast-2.amazonaws.com/images/"
                    f"{uuid.uuid5(uuid.NAMESPACE_OID, files[i].filename)}{os.path.splitext(files[i].filename)[1]}")
        except IndexError:
            setattr(uploaded_files, f"image{i+1}_url", None)
        finally:
            [await file.close() for file in files]
    return uploaded_files


@router.get("/{review_id}", response_model=schemas.Review, name="리뷰 상세보기")
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
    """
    # 비회원인 경우 id 값이 없기 때문에, 작성자인지 여부를 판별할 수 없음 -> 이에 따라 임시 orm 모델로 변환시켜줌
    if current_user is None:
        current_user = models.User(id=0)
    review_ids_like_by_user = [
        jsonable_encoder(review_id).get("review_id")
        for review_id in crud.user_like.get_review_id_by_user_id(db=db, user_id=current_user.id)
    ]
    review_obj = crud.review.get_review_details(db=db, review_id=review_id)
    delattr(review_obj.survey, "id")
    review_details = schemas.Review(
        id=review_obj.id,
        content=review_obj.content,
        images=review_obj.images,
        user_id=review_obj.user_id,
        survey=review_obj.survey,
        is_writer=review_obj.user_id == current_user.id,
        nickname=review_obj.user.nickname,
        keywords=[review_keyword.keyword for review_keyword in review_obj.keywords],
        like_count=review_obj.like_count,
        comment_count=crud.comment.get_comment_counts_by_review_id(db=db, review_id=review_id),
        user_is_like=review_obj.id in review_ids_like_by_user,
    )
    return review_details


@router.patch("/{review_id}", name="리뷰 수정", response_model=schemas.BaseResponse)
async def edit_review(
        review_id: int,
        review_in: schemas.ReviewUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
) -> schemas.BaseResponse:
    """
    <h1> 사용자가 게시한 리뷰를 수정합니다. </h1> </br>
    """
    db_obj = crud.review.get_review(db, id=review_id)
    check_is_deleted(db_obj)
    updated_review = crud.review.update_review(db, db_obj=db_obj, obj_in=review_in, current_user=current_user)
    crud.review_keyword.bulk_update(db, review_id=review_id, keywords=review_in.keywords)
    db.commit()
    db.refresh(updated_review)
    response = schemas.BaseResponse(
        object=updated_review.id, message=f"리뷰 ID : #{updated_review.id}가 수정되었습니다."
    )
    return response


@router.delete("/{review_id}", name="리뷰 삭제", response_model=schemas.BaseResponse)
async def delete_review(
        review_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
) -> schemas.BaseResponse:
    """
    <h1> 게시글의 상태를 삭제됨으로 변경합니다.</h1> </br>
    삭제 상태의 게시글은 리스트에 표현되지 않으며, 상세 정보 조회가 불가능합니다.
    슈퍼 유저는 본인이 작성한 게시글이 아니어도 삭제할 수 있습니다. </br>
    """
    db_obj = crud.review.get_review(db, id=review_id)
    check_is_deleted(db_obj)
    crud.review.set_review_status_as_deleted(db, db_obj=db_obj, current_user=current_user)
    response = schemas.BaseResponse(
        object=db_obj.id, message=f"리뷰 ID : #{db_obj.id}가 삭제되었습니다."
    )
    return response


@router.get("/{review_id}/content", name="설문 내용 없이 리뷰의 내용만 불러오기", response_model=schemas.ReviewContentResponse)
async def get_review_content(
        review_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
) -> schemas.ReviewContentResponse:
    """
    <h1> 설문 내용 없이 리뷰의 내용만 불러옵니다. </h1> </br>
    </br>
    리뷰 수정시 폼을 채우기 위한 기본 정보만 리턴하는 API 입니다.
    """
    review = crud.review.get_review(db=db, id=review_id)
    review_keyword = crud.review_keyword.get_keywords_by_review_id(db=db, review_id=review_id)
    keywords = [keyword.keyword for keyword in review_keyword]
    return schemas.ReviewContentResponse(content=review.content, images=review.images, keywords=keywords)


# TODO : 백그라운드 테스크 celery_tasks 로 변경
@router.post("/{review_id}/report", name="리뷰 신고", response_model=schemas.BaseResponse)
async def report_review(
        review_id: int,
        reason: schemas.ReportReason,
        background_task: BackgroundTasks,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
) -> schemas.BaseResponse:
    """
    <h1> 리뷰를 신고합니다. </h1> </br>
    신고 목록을 관리하는 DB를 따로 구현하지 않아, ddakkm@kakao.com 이메일 계정으로 신고 내역이 전달됩니다. </br>
    review_id: 신고하려는 리뷰 id </br>
    reason: 1 ~ 4 사이의 int 값 </br>
    __reason 번호별 사유__ </br>
    1. 부적절한 홍보 / 영리 목적 </br>
    2. 욕설 / 반말 / 부적절한 언어 사용 </br>
    3. 도배 / 스팸성 </br>
    4. 분란 유도 </br>
    ex: 신고사유가 "분란유도" 인 경우, body에 4번을 넣어서 보내주세요 </br>
    </br>
    </br>
    파라미터로 넘어온 리뷰 id 에 해당하는 리뷰가 존재하지 않는 경우, 404에러를 반환합니다. (성공시 200) </br>
    """
    review = crud.review.get_review(db, review_id)
    check_is_deleted(review)
    review_content = review.content
    report_reason = get_report_reason(reason.reason)
    subject = f"[ddakkm 리뷰 신고] 게시글 ID {review_id}"
    text = f"""
    신고 게시글 내용: {review_content}
    신고자_ID: {current_user.id}
    신고자_닉네임: {current_user.nickname}
    신고사유: {report_reason}
    """
    background_task.add_task(email_sender, subject=subject, text=text, to=EmailStr(settings.SMTP_USER))
    response = schemas.BaseResponse(
        object=review_id, message=f"리뷰 ID : #{review_id}가 신고처리되었습니다. 제목 \"{subject}\"으로 상세내용이 발송되었습니다.")
    return response


@router.post("/{review_id}/comment", name="리뷰에 댓글 작성", response_model=schemas.BaseResponse)
async def create_comment(
        review_id: int,
        comment_in: schemas.CommentCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
) -> schemas.BaseResponse:
    """
    <h1> 리뷰에 코멘트를 추가합니다. </h1> </br>
    </br>
    댓글 내용은 {"content": "댓글 내용"} <- 형식의 json Body로 받고,  </br>
    글을 작성하고자 하는 review_id 를 Path Parameter 로 받습니다. </br>
    """
    crud.comment.create_by_current_user(db, obj_in=comment_in, current_user=current_user, review_id=review_id)
    response = schemas.BaseResponse(
        object=review_id, message=f"리뷰 ID : #{review_id}에 댓글이 작성되었습니다."
    )
    return response


@router.post("/{review_id}/like_status", name="회원의 리뷰에 대한 좋아요 상태 변경", response_model=schemas.BaseResponse)
async def change_review_like_status(
        review_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
) -> schemas.BaseResponse:
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
