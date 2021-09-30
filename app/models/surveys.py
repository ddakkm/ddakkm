from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import ENUM, JSON

from app.db.base_class import Base

VACCINE_TYPE = ("PFIZER", "MODERNA", "AZ", "JANSSEN", "ETC")
DATE_FROM = ("0", "2", "3", "over5", "over1week", "over1month")


class SurveyA(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    vaccine_type = Column(ENUM(*VACCINE_TYPE), default=VACCINE_TYPE[0])
    is_crossed = Column(Boolean, default=False)
    is_pregnant = Column(Boolean, default=False)
    is_underlying_disease = Column(Boolean, default=False)
    date_from = Column(ENUM(*DATE_FROM), default=DATE_FROM[0])
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