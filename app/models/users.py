import enum

from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class SnsProviderType(str, enum.Enum):
    LOCAL = "LOCAL"
    NAVER = "NAVER"
    KAKAO = "KAKAO"


class Gender(str, enum.Enum):
    ETC = "ETC"
    MALE = "MALE"
    FEMALE = "FEMALE"


class JoinSurveyCode(str, enum.Enum):
    NONE = "NONE"
    A = "A"
    B = "B"
    C = "C"


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    sns_id = Column(String(100))
    email = Column(String(100))
    is_super = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    sns_provider = Column(Enum(SnsProviderType), default=SnsProviderType.LOCAL)
    hashed_password = Column(String(100))
    nickname = Column(String(30), unique=True, nullable=False)
    gender = Column(Enum(Gender), default=Gender.ETC)
    age = Column(Integer, default=1980)
    join_survey_code = Column(Enum(JoinSurveyCode), default=JoinSurveyCode.NONE)
    agree_policy = Column(Boolean, nullable=False)
    agree_keyword_push = Column(Boolean, nullable=False, default=True)
    agree_activity_push = Column(Boolean, nullable=False, default=True)
    character_image = Column(String(100))
    fcm_token = Column(String(300))

    # One to One
    # TODO survey_a 1:Many 로 수정
    survey_a = relationship("SurveyA", back_populates="user", uselist=False, join_depth=1, lazy="joined")
    survey_b = relationship("SurveyB", back_populates="user", uselist=False, join_depth=1, lazy="joined")
    survey_c = relationship("SurveyC", back_populates="user", uselist=False, join_depth=1, lazy="joined")

    # One to Many
    reviews = relationship("Review", back_populates="user", uselist=True)
    comments = relationship("Comment", back_populates="user", uselist=True)
    keywords = relationship("UserKeyword", back_populates="user", uselist=True)

    # Many to Many
    user_comment_like = relationship("UserCommentLike", back_populates="user", join_depth=1)
    user_like = relationship("UserLike", back_populates="user", join_depth=1)


class UserKeyword(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    keyword = Column(String(30))

    # Many to One
    user = relationship("User", back_populates="keywords")


class NicknameCounter(Base):
    counter = Column(Integer, autoincrement=True, primary_key=True)
