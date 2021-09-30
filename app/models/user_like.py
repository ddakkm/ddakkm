from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class UserLike(Base):
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("review.id"), primary_key=True, index=True)

    # Many to Many relation
    user = relationship('User', back_populates='user_like')
    review = relationship('Review', back_populates='user_like')