from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import ENUM


from app.db.base_class import Base

SNS_PROVIDER = ('LOCAL', 'NAVER', 'KAKAO')
GENDER = ('ETC', 'MALE', 'FEMALE')
JOIN_SURVEY_CODE = ('None', 'A', 'B', 'C')


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    is_super = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    sns_provider = Column(ENUM(*SNS_PROVIDER), default=SNS_PROVIDER[0])
    email = Column(String(100), unique=True, index=True, nullable=False)
    nickname = Column(String(30), unique=True, nullable=False)
    gender = Column(ENUM(*GENDER), default=GENDER[0])
    age = Column(Integer, default=1980)
    join_survey_code = Column(ENUM(*JOIN_SURVEY_CODE), default=JOIN_SURVEY_CODE[0])

    # One to One
    survey_a = relationship("SurveyA", back_populates="user", uselist=False)
    survey_b = relationship("SurveyB", back_populates="user", uselist=False)
    survey_c = relationship("SurveyC", back_populates="user", uselist=False)

    # One to Many
    reviews = relationship("Review", back_populates="writer", uselist=True)
    comments = relationship("Comment", back_populates="writer", uselist=True)

    # Many to Many
    user_like = relationship("UserLike", back_populates="user", join_depth=1)
    user_tag = relationship("UserTag", back_populates="user", join_depth=1)
