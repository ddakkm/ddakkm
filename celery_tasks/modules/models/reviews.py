from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from ..db.base_class import Base


class Review(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    content = Column(String(3000))
    like_count = Column(Integer, default=0, nullable=False)
    view_count = Column(Integer, default=0)

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
