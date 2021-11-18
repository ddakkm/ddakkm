import logging
from typing import Optional
from datetime import timedelta

import requests
from fastapi import HTTPException

from app import schemas, models, crud
from app.core import security
from app.core.config import settings

logger = logging.getLogger('ddakkm_logger')


def get_sns_id(sns_access_token: str, sns_provider: models.SnsProviderType) -> Optional[str]:

    headers = {"Authorization": f"Bearer {sns_access_token}"}

    if sns_provider == models.SnsProviderType.KAKAO:
        response = requests.get('https://kapi.kakao.com/v1/user/access_token_info', headers=headers)
        # 카카오 서버에서 준 엑세스토큰 이상한 경우 > 400
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="카카오 인증서버를 통해 인증할 수 없는 ACCESS TOKEN 입니다.")
        return str(response.json().get('id'))

    if sns_provider == models.SnsProviderType.NAVER:
        response = requests.get("https://openapi.naver.com/v1/nid/me", headers=headers)
        # 네이버 서버에서 준 액세스토큰 이상한 경우 > 400
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="네이버 인증서버를 통해 인증할 수 없는 ACCESS TOKEN 입니다.")
        logger.info(response.json())
        return str(response.json().get('id'))

    else:
        raise HTTPException(status_code=400, detail="로컬 회원은 본 API로 인증할 수 없습니다.")


def generate_access_token_for_sns_user(user: Optional[models.User]) -> schemas.login.LoginResponse:
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    if user:
        return schemas.login.LoginResponse(
            is_user=True,
            access_token=security.create_access_token(subject=user.id, expires_delta=access_token_expires),
            nickname=user.nickname
        )
    elif user is None:
        return schemas.login.LoginResponse(
            is_user=False,
            access_token=None,
            nickname=None
        )
