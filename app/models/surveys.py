import enum

from sqlalchemy import Column, Integer, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import JSON

from app.db.base_class import Base


class VaccineType(str, enum.Enum):
    PFIZER = "PFIZER"
    MODERNA = "MODERNA"
    AZ = "AZ"
    JANSSEN = "JANSSEN"
    ETC = "ETC"


class DATE_FROM(str, enum.Enum):
     ZERO_DAY = "ZERO_DAY"
     TWO_DAY = "TWO_DAY"
     THREE_DAY = "THREE_DAY"
     OVER_FIVE = "OVER_FIVE"
     OVER_WEEK = "OVER_WEEK"
     OVER_MONTH = "OVER_MONTH"


class SurveyA(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    vaccine_type = Column(Enum(VaccineType), default=VaccineType.ETC)
    is_crossed = Column(Boolean, default=False)
    is_pregnant = Column(Boolean, default=False)
    is_underlying_disease = Column(Boolean, default=False)
    date_from = Column(Enum(DATE_FROM), default=DATE_FROM.ZERO_DAY)
    data = Column(JSON)

    # One to One
    user = relationship("User", back_populates="survey_a", uselist=False)
    review = relationship("Review", back_populates="survey", uselist=False)


class SurveyB(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    data = Column(JSON)

    # One to One
    user = relationship("User", back_populates="survey_b", uselist=False)


class SurveyC(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    data = Column(JSON)

    # One to One
    user = relationship("User", back_populates="survey_c", uselist=False)