from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ReviewTag(Base):
    review_id = Column(Integer, ForeignKey("review.id"), primary_key=True, index=True)
    tag_id = Column(Integer, ForeignKey("tag.id"), primary_key=True, index=True)

    # Many to Many relation
    review = relationship('Review', back_populates='review_tag')
    tag = relationship('Tag', back_populates='review_tag')
