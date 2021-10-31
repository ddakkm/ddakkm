from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from app.db.base_class import Base


# TODO : 태그는 우선 메모리로 관리
class Tag(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), nullable=False, index=True, unique=True)
    is_activate = Column(Boolean, default=True)

    # Many to Many
    review_tag = relationship("ReviewTag", back_populates="tag", join_depth=1)
    user_tag = relationship("UserTag", back_populates="tag", join_depth=1)