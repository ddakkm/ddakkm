from typing import Any, List

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Body, HTTPException
from fastapi.encoders import jsonable_encoder

from app.controllers import deps
from app import crud, schemas, models

router = APIRouter()


@router.get("/join-survey", response_model=schemas.JoinSurveyStatusResponse, name="회원가입 설문 여부 확인")
async def get_join_survey_status(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
) -> schemas.JoinSurveyStatusResponse:
    """
    <h1>푸시알림수신 동의 여부 및 회원가입 설문의 상태를 리턴합니다.</h1>
    """
    user = crud.user.get(db=db, id=current_user.id)
    return schemas.JoinSurveyStatusResponse(
        done_survey=user.join_survey_code != "NONE"
    )


@router.post("/join-survey", name="회원가입 설문 등록")
async def create_join_survey(
        *,
        survey_in: schemas.SurveyCreate = Body(..., examples=schemas.survey_details_example),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
) -> models.User:
    """
    <h1> 회원 가입 설문을 등록합니다. </h1>
    설문 타입 A 만 등록할 수 있는 리뷰 작성 (POST /v1/review) 과 다르게, 설문 타입 A, B, C 중 한개를 선택하여 보낼 수 있습니다. </br>
    각 설문 타입의 예시 JSON Object에 대해서는 Swagger의 Example을 참조해주세요. </br>
    </br>
    <h3> Request Body 설명 </h3>
    __설문 타입 A__는 기본 질문 + 설문으로 이루어져있습니다. </br>
    __기본질문__은 백신 종류, 기저질환 여부, 교차접종 여부를 묻는 질문으로 "survey_details" 이하의 is_crossed / is_pregnant 등 이고,
    Enum이나 Boolean 타입으로 구성되어 있습니다. </br>
    __설문__은 "survey_details" 이하의 "data" Object 에 입력되어야 하며 각 질문에 맞게 q1 ~ q5 까지 구성되어있습니다. </br>
    발열 지속 기간에 대해 묻는 q2_1 문항은 q2의 응답이 1번(발열이 없었어요) 일 때는 null이 입력되어야 합니다.
    복수 이미지를 업로드하는 예제 코드는 아래를 참조하세요. </br>
    </br>
    __설문 타입 B__는 설문으로만 이루어져있습니다. </br>
    __설문__은 접종하려는 이유를 묻는 q1과 접종시 우려사항을 묻는 q2로 구성되어있습니다. </br>
    </br>
    __설문 타입 C__는 설문으로만 이루어져있습니다. </br>
    __설문__은 접종하지 않는 이유를 묻는 q1과 앞으로의 접종 계획을 묻는 q2로 구성되어있습니다. </br>
    </br>
    <h3> Request Body 의 Validation 설명 </h3>
    __단수의 응답만 허용하는 객관식 질문 (예:A타입 q2, q2_1 등)__은 int 타입의 값만 허용하며 첫번째 답변일경우 1 부터 인덱스를 시작합니다. </br>
    응답이 선택지의 범위를 벗어나는 경우 (제시된 객관식 응답이 1~5번인데, 0번이나 6번의 응답이 입력된 경우)에는 422 에러와 함께 잘못 입력된 위치와 잘못 입력된 값을 반환합니다. </br>
    </br>
    __복수의 응답을 허용하는 객관식 질문(예:B타입 q2, C타입 q2 등)__은 int 로 이루어진 값들의 배열만 허용합니다. </br>
    응답의 갯수가 선택지의 최대 갯수를 초과하는 경우 (제시된 객관식 응답이 1~5번으로 총 5개인데, 입력된 배열의 인자 갯수가 6개 이상인경우)에는
    422 에러와 함께 잘못 입력된 위치와 잘못 입력된 값을 반환합니다. </br>
    각 개별 응답이 선택지의 범위를 벗어나는 경우 (제시된 객관식 응답이 1~5번인데, 0번이나 6번의 응답값이 배열에 포함된 경우)에는
    422 에러와 함께 잘못 입력된 위치와 잘못 입력된 값을 반환합니다. </br>
    </br>
    __복수의 응답을 허용하는 객관식 + 주관식 질문(예:A타입 q1, B타입 q1 등)__은 int 값들과 최대 1개의 string으로 이루어진 값들의 배열만 허용합니다. </br>
    응답의 갯수가 선택지의 최대 갯수를 초과하는 경우 (제시된 객관식 응답이 1~5번으로 총 5개인데, 입력된 배열의 인자 갯수가 6개 이상인경우)에는
    422 에러와 함께 잘못 입력된 위치와 잘못 입력된 값을 반환합니다. </br>
    각 개별 응답이 선택지의 범위를 벗어나는 경우 (제시된 객관식 응답이 1~5번인데, 0번이나 6번의 응답값이 배열에 포함된 경우)에는
    422 에러와 함께 잘못 입력된 위치와 잘못 입력된 값을 반환합니다. </br>
    배열 내에 2개 이상의 문자열 인자가 입력된 경우 (설문 양식에 2개 이상의 직접입력값을 받는 문항이 없기 때문에) 422 에러와 함께 잘못 입력된 위치와 잘못 입력된 값을 반환합니다. </br>
    </br>
    __선택한 설문 타입 (survey_type)과 입력된 설문 양식 (survey_details)이 매칭되지 않는 경우__에도 입력되지 않습니다.. </br>
    </br>
    __이미 가입 설문을 마친 유저__가 설문을 할 경우 400 에러를 반환합니다.
    """
    if current_user.join_survey_code != models.JoinSurveyCode.NONE:
        raise HTTPException(400, "이미 회원가입 설문을 마친 회원입니다.")
    return crud.user.create_join_survey(db=db, survey_in=survey_in, user_id=current_user.id)


@router.get("/push", response_model=schemas.PushStatusResponse, name="푸시알림 동의 여부 확인 (키워드/활동 둘다)")
async def get_agree_push_status(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
) -> schemas.PushStatusResponse:
    """
    <h1> push 알림 수신 동의 여부를 확인합니다. </h1>
    """
    """
    <h1>푸시알림수신 동의 여부 및 회원가입 설문의 상태를 리턴합니다.</h1>
    """
    user = crud.user.get(db=db, id=current_user.id)
    return schemas.PushStatusResponse(
        agree_activity_push=user.agree_activity_push,
        agree_keyword_push=user.agree_keyword_push
    )


@router.post("/push/keyword", name="키워드 푸시 알림 동의 상태 변경")
async def change_push_status(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
) -> models.User:
    """
    <h1> 키워드 push 알림 수신 동의 여부를 변경합니다. </h1>
    동의 상태의 유저가 호출하면 동의 상태를 false 로 // 비동의 상태의 유저가 호출하면 동의 상태가 true가 됩니다. </br>
    </br>
    ```동의 / 동의취소 따로 만들어야하면 말해주세요.```
    """
    return crud.user.change_user_agree_keyword_push_status(db=db, current_user=current_user)


@router.post("/push/activity", name="활동 푸시 알림 동의 상태 변경")
async def change_push_status(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
) -> models.User:
    """
    <h1> 활동 push 알림 수신 동의 여부를 변경합니다. </h1>
    동의 상태의 유저가 호출하면 동의 상태를 false 로 // 비동의 상태의 유저가 호출하면 동의 상태가 true가 됩니다. </br>
    </br>
    ```동의 / 동의취소 따로 만들어야하면 말해주세요.```
    """
    return crud.user.change_user_agree_activity_push_status(db=db, current_user=current_user)


# TODO A타입 vaccine_round 는 최신 survey에서 가져와야 함
@router.get("/me/profile", response_model=schemas.UserProfileResponse, name="내 프로필 확인")
async def get_my_profile(
        *,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
) -> schemas.UserProfileResponse:
    """
    <h1> 회원 정보 요약본을 가져옵니다. </h2> </br>
    __vaccine_status__이하 __join_survey_code__에서 유저가 어떤 설문을 선택했는지를 반환합니다. </br>
    __join_survey_code__의 값이 A인 유저는 __vaccine_status__의 하위 속성으로 __details__라는 object를 갖는데,
    이곳에서 __vaccine_round__(몇차수인지), __vaccine_type__(어떤 백신인지), __is_crossed__(교차접종인지)에 대한 정보를 함께 반환합니다. </br>
    </br>
    __join_survey_code__의 값이 B인 유저는 접종예정 유저로 접종 내역이 없기 때문에 __details__라는 object는 null 값을 반환합니다. </br>
    </br>
    __join_survey_code__의 값이 C나 NONE인 유저는 미접종 유저로 접종 내역이 없기 때문에 __details__라는 object는 null 값을 반환합니다. </br>
    """
    user = crud.user.get(db=db, id=current_user.id)
    post_counts = crud.review.get_review_counts_by_user_id(db=db, user_id=current_user.id)
    comment_counts = crud.comment.get_comment_counts_by_user_id(db=db, user_id=current_user.id)
    like_counts = crud.user_like.get_like_counts_by_user_id(db=db, user_id=current_user.id)
    if user.join_survey_code == models.JoinSurveyCode.A:
        details = {"vaccine_round": user.survey_a.vaccine_round,
                   "vaccine_type": user.survey_a.vaccine_type,
                   "is_crossed": user.survey_a.is_crossed}
        vaccine_status = schemas.VaccineStatus(join_survey_code=user.join_survey_code, details=details)

    else:
        vaccine_status = schemas.VaccineStatus(join_survey_code=user.join_survey_code)
    return schemas.UserProfileResponse(vaccine_status=vaccine_status, character_image=user.character_image, nickname=user.nickname,
                                       post_counts=post_counts, comment_counts=comment_counts, like_counts=like_counts)


@router.get("/me/post", response_model=List[schemas.UserProfilePostResponse], name="내가 쓴 글 확인")
async def get_my_posts(
        *,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
) -> Any:
    """
    <h1> 내가 올린 후기들의 리스트를 불러옵니다. </h1>
    2회차-화이자-교차접종 /// 1회차-모더나 /// 등등의 제목을 만들기 위해 "vaccine_status"라는 Object를 줍니다. </br>
    </br>
    이 "vaccine_status"라는 Object는 회원 프로필을 가져오는 API __([GET] /v1/user/me/profile)에서 사용되는 "vaccine_status"와 동일__합니다. </br>
    __다만__ 회원 프로필을 가져오는 API에서는 회원들이 입력한 survey_code가 다양할 수 있기 때문에 "vaccine_status" object의 "join_survey_code" 값이
    A, B, C, null 중 하나이지만, </br>
    __본 API에서는__ 모든 후기가 "A" 타입의 survey이며, join_survey도 아니기 때문에 해당 값은 항상 null 입니다.
    """
    user_reviews_model = crud.review.get_reviews_by_user_id(db=db, user_id=current_user.id)
    user_reviews = [schemas.UserProfilePostResponse(
        id=review.id,
        nickname=review.user.nickname,
        like_count=len(review.user_like),
        comment_count=len(review.comments),
        created_at=review.created_at,
        vaccine_status=schemas.VaccineStatus(join_survey_code=None,
                                             details={"vaccine_round": review.survey.vaccine_round,
                                                      "vaccine_type": review.survey.vaccine_type,
                                                      "is_crossed": review.survey.is_crossed}),
        ) for review in user_reviews_model]
    return user_reviews


@router.post("/keyword", name="회원의 키워드 설정")
async def set_keyword(
        *,
        obj_in: schemas.UserKeywordCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
) -> models.UserKeyword:
    """
    <h1> 유저의 키워드를 설정합니다. </h1>
    """
    return crud.user.create_keywords(db=db, user_id=current_user.id, obj_in=obj_in)


@router.patch("/keyword", name="회원의 키워드 수정")
async def edit_keyword(
        *,
        obj_in: schemas.UserKeywordCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
) -> Any:
    """
    <h2> TODO loop 돌며, 이미 등록된 경우 pass 새로 등록된 경우 insert -> 이래야 푸시 알림에 문제 없을듯
    </h2>
    """
    return


@router.delete("", response_model=schemas.BaseResponse, deprecated=True, name="회원삭제 (개발 테스트용)")
async def delete_user(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
) -> schemas.BaseResponse:
    """
    <h1> 회원을 삭제합니다. 본 API는 테스트용으로만 사용합니다. </h1> </br>
    헤더에 [ Authorization: Baerer 액세스 토큰 ]을 넣으면 해당하는 유저의 리뷰/코멘트/좋아요기록 등 모든 관련 정보가 삭제됩니다.
    """
    return crud.user.delete_by_user_id(db=db, user_id=current_user.id)


@router.get("/me/comment", response_model=List[schemas.UserProfilePostResponse], deprecated=True, name="내가 쓴 댓글 확인")
async def get_my_comments(
        *,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
) -> List[schemas.UserProfilePostResponse]:
    """
    <h1> 내가 댓글 단 후기들의 리스트를 불러옵니다. </h1>
    2회차-화이자-교차접종 /// 1회차-모더나 /// 등등의 제목을 만들기 위해 "vaccine_status"라는 Object를 줍니다. </br>
    </br>
    이 "vaccine_status"라는 Object는 회원 프로필을 가져오는 API __([GET] /v1/user/me/profile)에서 사용되는 "vaccine_status"와 동일__합니다. </br>
    __다만__ 회원 프로필을 가져오는 API에서는 회원들이 입력한 survey_code가 다양할 수 있기 때문에 "vaccine_status" object의 "join_survey_code" 값이
    A, B, C, null 중 하나이지만, </br>
    __본 API에서는__ 모든 후기가 "A" 타입의 survey이며, join_survey도 아니기 때문에 해당 값은 항상 null 입니다.
    <h2> TODO "created_at" 파라미터가 현재는 리뷰 작성시간으로 리턴됨 -> 댓글 작성시간으로 변경해야함
    <h2>
    """
    review_ids_comment_by_user = [
        jsonable_encoder(review_id).get("review_id")
        for review_id in crud.comment.get_review_id_by_comment_user_id(db=db, user_id=current_user.id)
    ]
    reviews_model = crud.review.get_reviews_by_ids(db=db, ids=review_ids_comment_by_user)
    reviews = [schemas.UserProfilePostResponse(
        id=review.id,
        nickname=review.user.nickname,
        like_count=len(review.user_like),
        comment_count=len(review.comments),
        created_at=review.created_at,
        vaccine_status=schemas.VaccineStatus(join_survey_code=None,
                                             details={"vaccine_round": review.survey.vaccine_round,
                                                      "vaccine_type": review.survey.vaccine_type,
                                                      "is_crossed": review.survey.is_crossed}),
        ) for review in reviews_model]
    return reviews


@router.get("/me/like", response_model=List[schemas.UserProfilePostResponse], deprecated=True, name="내가 좋아요 한 글 확인")
async def get_user_info(
        *,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
) -> List[schemas.UserProfilePostResponse]:
    """
    <h1> 내가 좋아요 한 후기들의 리스트를 불러옵니다. </h1>
    2회차-화이자-교차접종 /// 1회차-모더나 /// 등등의 제목을 만들기 위해 "vaccine_status"라는 Object를 줍니다. </br>
    </br>
    이 "vaccine_status"라는 Object는 회원 프로필을 가져오는 API __([GET] /v1/user/me/profile)에서 사용되는 "vaccine_status"와 동일__합니다. </br>
    __다만__ 회원 프로필을 가져오는 API에서는 회원들이 입력한 survey_code가 다양할 수 있기 때문에 "vaccine_status" object의 "join_survey_code" 값이
    A, B, C, null 중 하나이지만, </br>
    __본 API에서는__ 모든 후기가 "A" 타입의 survey이며, join_survey도 아니기 때문에 해당 값은 항상 null 입니다.
    """
    review_ids_like_by_user = [
        jsonable_encoder(review_id).get("review_id")
        for review_id in crud.user_like.get_review_id_by_user_id(db=db, user_id=current_user.id)
    ]
    reviews_model = crud.review.get_reviews_by_ids(db=db, ids=review_ids_like_by_user)
    reviews = [schemas.UserProfilePostResponse(
        id=review.id,
        nickname=review.user.nickname,
        like_count=len(review.user_like),
        comment_count=len(review.comments),
        created_at=review.created_at,
        vaccine_status=schemas.VaccineStatus(join_survey_code=None,
                                             details={"vaccine_round": review.survey.vaccine_round,
                                                      "vaccine_type": review.survey.vaccine_type,
                                                      "is_crossed": review.survey.is_crossed}),
        ) for review in reviews_model]
    return reviews
