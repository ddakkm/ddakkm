from typing import TypeVar, Generic, List, Callable

from sqlalchemy.orm import Query
from pydantic.generics import GenericModel
from pydantic import BaseModel

from app import schemas

ModelType = TypeVar("ModelType")


class PageMeta(BaseModel):
    total: int
    page: int
    size: int
    has_next: bool


class PageResponse(GenericModel, Generic[ModelType]):
    page_meta: PageMeta


class PageResponseReviews(PageResponse):
    contents: List[schemas.ReviewResponse]


def paginated_query(page_request: dict, base_query: Query, query_executor: Callable):
    page = page_request.get("page", 1)
    size = page_request.get("size", 10)
    total = base_query.count()

    return {
        "page_meta": {
            "page": page,
            "size": size,
            "total": total,
            "has_next": page * size < total,
        },
        "contents": query_executor(base_query),
    }
