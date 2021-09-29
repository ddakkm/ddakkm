from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import JSON

from app.db.base_class import Base


class Review(Base):
    id = Column(Integer, primary_key=True, index=True)
    writer_id = Column(Integer, ForeignKey('users.id'))
    is_delete = Column(Boolean, default=False)
    content = Column(String(3000))
    images = Column(JSON)

    # One to One
    survey_x = relationship("SurveyX", back_populates="review", uselist=False)

    # Many to One
    writer = relationship("User", back_populates="reviews", join_depth=1, uselist=False)

    # Many to Many
    user_like = relationship("UserLike", back_populates="review", join_depth=1)
    review_tag = relationship("ReviewTag", back_populates="review", join_depth=1)