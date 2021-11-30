from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Qna(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    content = Column(String(3000))
    user_email = Column(String(300))
    user_phone = Column(String(30))
    is_solved = Column(Boolean, default=False)

    # Many To One
    user = relationship("User")
