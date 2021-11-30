from typing import Any
from datetime import timedelta

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app import crud, schemas, models
from app.core import security
from app.core.config import settings
from app.controllers import deps
from app.utils.auth import generate_access_token_for_sns_user, get_sns_id
from app.schemas.response import BaseResponse

router = APIRouter()


@router.post("/sign-up", response_model=schemas.LoginResponse, name="회원가입")
async def create_user_sns(
        *,
        db: Session = Depends(deps.get_db),
        oauth_in: schemas.OauthIn,
        user_in: schemas.SNSUserCreate
) -> schemas.LoginResponse:
    """
    <h1>SNS 인증 서버를 통해 발급받은 SNS용 Access Token을 이용해 회원가입을 합니다. </h1> </br>
    "oauth_in" 키에는 SNS 인증정보 (SNS Provider와, SNS Access Token)를, "user_in" 키에는 회원정보 (성별과 생년)을 받습니다. </br>
    바로 로그인을 하기 위해 __회원가입 성공시 생성된 유저 모델 정보와 함께 access_token 값도 리턴__합니다. </br>
    이미 회원이거나, SNS에서 발급받은 access_token이 무효한 경우 400에러를 반환합니다.
    </br></br>
    현재 기획서상 비회원 유저의 서비스 사용 절차는 다음과 같습니다. </br>
    SNS 인증정보를 가지고 로그인 요청 > 로그인 실패 > 회원가입 요청 >
    회원가입 성공시 access_token 반환 > 회원 가입 성공의 리턴값으로 받은 access_token으로 다시 로그인 요청
    """
    sns_id = get_sns_id(sns_access_token=oauth_in.sns_access_token, sns_provider=oauth_in.sns_provider)
    user_checker = crud.user.get_by_sns_id(db=db, sns_id=sns_id)
    if user_checker:
        raise HTTPException(status_code=400, detail="이미 가입된 회원입니다.")
    new_user = crud.user.create_sns(db, obj_in=user_in, oauth_in=oauth_in, sns_id=sns_id)
    response = generate_access_token_for_sns_user(new_user)
    response.status = "회원가입 성공"
    response.done_survey = False
    return response


@router.post("/login", response_model=schemas.LoginResponse, name="로그인")
async def login_sns(
        oauth_in: schemas.OauthIn,
        db: Session = Depends(deps.get_db)
) -> schemas.login.LoginResponse:
    """
    <h1>SNS 인증 서버를 통해 발급받은 SNS용 Access Token을 이용해 로그인 합니다. </h1> </br>
    SNS 인증정보 (SNS Provider와, SNS Access Token)를 받습니다. </br>
    </br>
    회원일 경우 "is_user": true 플래그와 "access_token" 값을 리턴합니다. </br>
    비회원일 경우 "is_user" false 플래그와 "access_token" 을 null 값으로 리턴합니다. </br>
    SNS에서 발급받은 access_token이 무효한 경우 400에러를 반환합니다.
    """
    sns_id = get_sns_id(sns_access_token=oauth_in.sns_access_token, sns_provider=oauth_in.sns_provider)
    user = crud.user.get_by_sns_id(db=db, sns_id=sns_id)
    crud.user.update(db=db, db_obj=user, obj_in={"fcm_token": oauth_in.fcm_token})
    if user is None:
        return schemas.LoginResponse(status="비회원", is_user=False, done_survey=False, access_token=None)
    response = generate_access_token_for_sns_user(user)
    response.done_survey = user.join_survey_code != "NONE"
    return response


@router.delete("/deactive", name="회원탈퇴", response_model=BaseResponse)
async def delete_user(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
):
    """
    <h1> 회원의 상태를 비활성화 상태로 변경합니다.</h1>
    헤더에 로그인 토큰을 요청하면 해당하는 회원을 비활성화 상태로 변경합니다.
    """
    return crud.user.soft_delete_by_user_id(db=db, user_id=current_user.id)


@router.post("/logout", name="로그아웃", response_model=BaseResponse)
async def logout(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
) -> BaseResponse :
    """
    <h1> 회원을 로그아웃상태로 만들어 기존에 등록된 fcm_token을 제거합니다. </h1>
    """
    return crud.user.delete_fcm_token(db=db, user_id=current_user.id)


@router.post("/sign-up/local", deprecated=True, name="id/pw로 회원가입 (개발테스트용)")
async def create_user_local(
        *,
        db: Session = Depends(deps.get_db),
        user_in: schemas.UserCreate
) -> schemas.BaseResponse:
    """
    <h1>개발 테스트 용으로 임시 사용합니다. 상용서버에선 삭제할 예정</h1> </br>
    회원가입 API  </br>
    지금은 테스트용 로컬 계정만 생성 가능 </br>
    </br>
    __*파라미터 설명__
    |파라미터|타입|내용|
    |-----|---|---|
    |sns_providder|enum(string)|"LOCAL", "NAVER", "KAKAO" 세개 중 하나를 받습니다.|
    |gender|enum(string)|"ETC", "MALE", "FEMALE" 세개 중 하나를 받습니다.|
    |age|int|출생 연도를 받습니다.|
    |join_survey_code|enum(string)|가입 설문의 종류를 뜻하는 파라미터로, "NONE", "A", "B", "C" 를 받습니다.|
    """
    result = crud.user.create_local(db, obj_in=user_in)
    response = BaseResponse(object=result.id, message=f"user_id {result.id}가 생성되었습니다.")
    return response


@router.post("/login/local", deprecated=True, name="id/pw로 로그인 (개발테스트용)")
async def login_local(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(deps.get_db)
) -> schemas.LoginResponse:
    """
    <h1>개발 테스트 용으로 임시 사용합니다. 상용서버에선 삭제할 예정</h1>
    로그인 API로 서버 내에서 HS256 알고리즘으로 인코딩된 JWT를 발급합니다. \n
    일반 사용자에겐 오픈하지 않고, 운영/개발 용으로만 사용할 예정입니다. \n
    request body type은 application/json 이 아닌, x-www-form-urlencoded 입니다.
    """
    user = crud.user.authentication(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=400, detail="Inccorect email or password"
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return schemas.LoginResponse(
        is_user=True,
        access_token=security.create_access_token(user.id, expires_delta=access_token_expires),
        done_survey=user.join_survey_code != "NONE",
        nickname=user.nickname
    )
