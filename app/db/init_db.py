from sqlalchemy.orm import Session
import pymysql

from app.db.base import Base, Tag   # noqa
from app.db.session import engine, SessionLocal

pymysql.install_as_MySQLdb()


def init_db(db: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    #     engine.execute(tbl.delete())

    # DB 다시 만들때 이부분 돌리기
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # user = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    # if not user:
    #     user_in = schemas.UserCreate(
    #         email=settings.FIRST_SUPERUSER,
    #         password=settings.FIRST_SUPERUSER_PASSWORD,
    #         is_superuser=True,
    #     )
    #     user = crud.user.create(db, obj_in=user_in)  # noqa: F841
    pass


if __name__ == "__main__":
    init_db(db=SessionLocal)
