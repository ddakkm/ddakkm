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

router = APIRouter()


@router.post("/sign-up/local", deprecated=True)
async def create_user_local(
        *,
        db: Session = Depends(deps.get_db),
        user_in: schemas.UserCreate
) -> models.User:
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
    return crud.user.create_local(db, obj_in=user_in)


@router.post("/sign-up/sns")
async def create_user_sns(
        *,
        db: Session = Depends(deps.get_db),
        oauth_in: schemas.OauthIn,
        user_in: schemas.SNSUserCreate
) -> models.User:
    sns_id = get_sns_id(sns_access_token=oauth_in.sns_access_token, sns_provider=oauth_in.sns_provider)
    user_checker = crud.user.get_by_sns_id(db=db, sns_id=sns_id)
    if user_checker:
        raise HTTPException(status_code=400, detail="이미 가입된 회원입니다.")
    return crud.user.create_sns(db, obj_in=user_in, oauth_in=oauth_in, sns_id=sns_id)


@router.post("/login/local", deprecated=True)
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
        access_token=security.create_access_token(user.id, expires_delta=access_token_expires)
    )


@router.post("/login/sns")
async def login_sns(
        oauth_in: schemas.OauthIn,
        db: Session = Depends(deps.get_db)
) -> schemas.login.LoginResponse:
    sns_id = get_sns_id(sns_access_token=oauth_in.sns_access_token, sns_provider=oauth_in.sns_provider)
    user = crud.user.get_by_sns_id(db=db, sns_id=sns_id)
    return generate_access_token_for_sns_user(user)