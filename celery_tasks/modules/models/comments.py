from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from ..db.base_class import Base


class Comment(Base):
    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey('review.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    content = Column(String(500), nullable=False, default="")
    depth = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    parent_id = Column(Integer, default=None)
    is_delete = Column(Boolean, default=False)

    # Many to One
    user = relationship("User", back_populates="comments", join_depth=0, uselist=False, lazy="noload")
    review = relationship("Review", back_populates="comments", join_depth=1, uselist=False)

    # Many to Many
    user_comment_like = relationship("UserCommentLike", back_populates="comment")
