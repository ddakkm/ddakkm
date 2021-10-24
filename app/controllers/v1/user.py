from typing import Any, Union

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Body, HTTPException

from app.controllers import deps
from app import crud, schemas, models

router = APIRouter()


@router.delete("", response_model=schemas.BaseResponse, deprecated=True)
async def delete_user(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
) -> schemas.BaseResponse:
    """
    <h1> 회원을 삭제합니다. 본 API는 테스트용으로만 사용합니다. </h1> </br>
    헤더에 [ Authorization: Baerer 액세스 토큰 ]을 넣으면 해당하는 유저의 리뷰/코멘트/좋아요기록 등 모든 관련 정보가 삭제됩니다.
    """
    return crud.user.delete_by_user_id(db=db, user_id=current_user.id)


@router.post("/join_survey")
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


# TODO A타입 vaccine_round 는 최신 survey에서 가져와야 함
@router.get("/me/profile", response_model=schemas.UserProfileResponse)
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
    return schemas.UserProfileResponse(vaccine_status=vaccine_status,
                                       post_counts=post_counts, comment_counts=comment_counts, like_counts=like_counts)


@router.get("/me/post")
async def get_my_posts(
        *,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
) -> Any:
    """
    <h1> TODO
    </h2>
    """
    return


@router.get("/me/comment")
async def get_my_comments(
        *,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
) -> Any:
    """
    <h1> TODO
    </h2>
    """
    return


@router.get("/{user_id}")
async def get_user_info(
        *,
        db: Session = Depends(deps.get_db),
) -> Any:
    """
    <h1> TODO
    </h2>
    """
    return


@router.post("/keyword")
async def set_keyword(
        *,
        db: Session = Depends(deps.get_db),
) -> Any:
    """
    <h1> TODO
    </h2>
    """
    return
