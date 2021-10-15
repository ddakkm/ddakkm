import requests
from typing import Any, Dict
from datetime import timedelta

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordRequestForm

from app import crud, schemas
from app.core import security
from app.core.config import settings
from app.controllers import deps
from app.models.users import SnsProviderType

router = APIRouter()


@router.post("/sign-up", deprecated=True)
async def create_user(
        *,
        db: Session = Depends(deps.get_db),
        user_in: schemas.UserCreate
) -> Any:
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


@router.post("/login/local", deprecated=True)
async def login_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(deps.get_db)
):
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
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/login/sns")
async def login_access_token(
        oauth_in: schemas.OauthLogin,
        db: Session = Depends(deps.get_db)
) -> Any:


    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # kakao
    if oauth_in.sns_provider == SnsProviderType.KAKAO:
        # TODO 유틸함수로 분리
        headers = {"Authorization": f"Bearer {oauth_in.sns_access_token}"}
        response = requests.get('https://kapi.kakao.com/v1/user/access_token_info', headers=headers)

        # 카카오 서버에서 준 엑세스토큰 이상한 경우 > 400
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="카카오 인증서버를 통해 인증할 수 없는 ACCESS TOKEN 입니다.")
        sns_id = str(response.json().get('id'))
        user = crud.user.get_by_sns_id(db, sns_id=sns_id)

        # 이미 회원인 경우 > is_user: True /  로그인용 액세스 토큰 발급
        if user:
            return schemas.login.LoginResponse(
                is_user=True,
                access_token=security.create_access_token(subject=user.id, expires_delta=access_token_expires)
            )

        # 회원 아닌경우 > is_user: False / 로그인용 액세스토큰 null
        else:
            return schemas.login.LoginResponse(
                is_user=False,
                access_token=None
            )

    # naver >>> 테스트 필요
    if oauth_in.sns_provider == SnsProviderType.NAVER:
        # TODO 유틸함수로 분리
        headers = {"Authorization": f"Bearer {oauth_in.sns_access_token}"}
        response = requests.get("https://openapi.naver.com/v1/nid/me", headers=headers)

        # 네이버 서버에서 준 액세스토큰 이상한 경우 > 400
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="네이버 인증서버를 통해 인증할 수 없는 ACCESS TOKEN 입니다.")
        sns_id = str(response.json().get('id'))
        user = crud.user.get_by_sns_id(db, sns_id=sns_id)

        # 이미 회원인 경우 > is_user: True / 로그인용 액세스 토큰 발급
        if user:
            return schemas.login.LoginResponse(
                is_user=True,
                access_token=security.create_access_token(subject=user.id, expires_delta=access_token_expires)
            )

        # 회원 아닌경우 > is_user: False / 로그인용 액세스토큰 null
        else:
            return schemas.login.LoginResponse(
                is_user=False,
                access_token=None
            )

    else:
        raise HTTPException(status_code=400, detail="로컬 회원은 본 API로 인증할 수 없습니다.")
