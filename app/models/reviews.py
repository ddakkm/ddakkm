from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import JSON

from app.db.base_class import Base


class Review(Base):
    id = Column(Integer, primary_key=True, index=True)
    writer_id = Column(Integer, ForeignKey('user.id'))
    survey_id = Column(Integer, ForeignKey('survey_a.id'))
    is_delete = Column(Boolean, default=False)
    content = Column(String(3000))
    images = Column(JSON)
    like_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)

    # One to One
    survey = relationship("SurveyA", back_populates="review", join_depth=1, uselist=False)

    # Many to One
    writer = relationship("User", back_populates="reviews", join_depth=1, uselist=False)

    # Many to Many
    user_like = relationship("UserLike", back_populates="review", join_depth=1)
    review_tag = relationship("ReviewTag", back_populates="review", join_depth=1)
