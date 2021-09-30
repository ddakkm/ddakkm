from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class UserTag(Base):
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True, index=True)
    tag_id = Column(Integer, ForeignKey("tag.id"), primary_key=True, index=True)

    # Many to Many relation
    user = relationship('User', back_populates='user_tag')
    tag = relationship('Tag', back_populates='user_tag')