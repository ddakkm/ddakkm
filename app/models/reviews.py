from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import JSON

from app.db.base_class import Base


class Review(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    survey_id = Column(Integer, ForeignKey('survey_a.id'))
    is_delete = Column(Boolean, default=False)
    content = Column(String(3000))
    images = Column(JSON)
    like_count = Column(Integer, default=0, nullable=False)
    view_count = Column(Integer, default=0)

    # One to One
    survey = relationship("SurveyA", back_populates="review", join_depth=1, uselist=False, lazy="joined")

    # One to Many
    comments = relationship("Comment", back_populates="review", join_depth=1, uselist=True, lazy="joined")
    keywords = relationship("ReviewKeyword", back_populates="review")

    # Many to One
    user = relationship("User", back_populates="reviews", join_depth=1, uselist=False, lazy="joined")

    # Many to Many
    user_like = relationship("UserLike", back_populates="review", join_depth=1, uselist=True, lazy="joined")


class ReviewKeyword(Base):
    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey('review.id'))
    keyword = Column(String(30))

    # Many to One
    review = relationship("Review", back_populates="keywords")