from typing import Generator, Optional, Union

from sqlalchemy.orm import Session
from pydantic import ValidationError
from fastapi import Depends, HTTPException, status, Query, Header
from fastapi.security import OAuth2PasswordBearer
from jose import jwt

from app import crud, models, schemas
from app.core.config import settings
from app.core import security
from app.db.session import SessionLocal
from app.schemas.review import ReviewParams

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login/local")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login/local", auto_error=False)


def review_params(q: Optional[str] = Query(None, description="검색용 쿼리, string"),
                  min_age: Optional[str] = Query(None, description="나이 필터, 최저 나이 입력 (생년 변환은 서버에서 함)"),
                  max_age: Optional[str] = Query(None, description="나이 필터, 최고 나이 입력 (생년 변환은 서버에서 함)"),
                  gender: Optional[str] = Query(None, description="성별 필터, \"ETC\", \"MALE\", \"FEMALE\""),
                  vaccine_type: Optional[str] = Query(None, description="백신 종류 필터, \"PFIZER\", \"MODERNA\", \"JANSSEN\", \"AZ\", \"ETC\""),
                  is_crossed: Optional[bool] = Query(None, description="교차접종 여부, \"true\", \"false\""),
                  round: Optional[str] = Query(None, description="접종 회차, \"FIRST\", \"SECOND\", \"THIRD\""),
                  is_pregnant: Optional[bool] = Query(None, description="임신 여부, \"true\", \"false\""),
                  is_underlying_disease: Optional[bool] = Query(None, description="기저질환 여부, \"true\", \"false\"")):
    return ReviewParams(q=q, min_age=min_age, max_age=max_age, gender=gender,
                        vaccine_type=vaccine_type, is_crossed=is_crossed,
                        round=round, is_pregnant=is_pregnant, is_underlying_disease= is_underlying_disease)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
        db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> models.User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError) as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="유효하지 않은 토큰 입니다."
        )
    user = crud.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="없는 회원입니다.")
    return user


def get_current_user_optional(
        db: Session = Depends(get_db), token: Optional[str] = Depends(oauth2_scheme_optional)
) -> Union[models.User, None]:
    """
    Access Token 없으면 Current User를 None 으로 반환함
    """
    if token is None:
        token = ""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError) as e:
        return None

    user = crud.user.get(db, id=token_data.sub)
    if not user:
        return None
    return user


def get_page_request(page: int = 1):
    return {"page": page, "size": 10}