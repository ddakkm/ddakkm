from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from ..db.base_class import Base


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    agree_keyword_push = Column(Boolean, nullable=False, default=True)
    agree_activity_push = Column(Boolean, nullable=False, default=True)
    fcm_token = Column(String(300))

    # One to Many
    reviews = relationship("Review", back_populates="user", uselist=True)
    comments = relationship("Comment", back_populates="user", uselist=True)
    keywords = relationship("UserKeyword", back_populates="user", uselist=True)

    # Many to Many
    user_comment_like = relationship("UserCommentLike", back_populates="user", join_depth=1)
    user_like = relationship("UserLike", back_populates="user", join_depth=1)


class UserKeyword(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    keyword = Column(String(30))

    # Many to One
    user = relationship("User", back_populates="keywords")
