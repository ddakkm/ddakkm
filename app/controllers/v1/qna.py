from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas, models, crud
from app.controllers import deps


router = APIRouter()


@router.post("", name="QNA 등록")
async def create_qna(
        obj_in: schemas.QnaCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user),
) -> schemas.BaseResponse:
    """
    <h1> 문의를 등록합니다. </h1> </br>
    __*파라미터 설명__
    |파라미터|타입|내용|
    |------|---|---|
    |content|string|문의의 본문입니다.|
    |user_email|Optional[str]|응답받을 이메일주소입니다.|
    |user_phone|Optional[str]|응답받을 전화번호입니다.|
    """
    params = dict(obj_in)
    params["user_id"] = current_user.id
    qna = crud.qna.create(db=db, obj_in=params)
    db.commit()
    return schemas.BaseResponse(object=qna.id, message=f"유저 ID: #{current_user.id}가 문의를 등록했습니다.")


@router.post("/{qna_id}/process", name="문의 처리 체크 (어드민용)")
async def process_qna(
        qna_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user),
) -> schemas.BaseResponse:
    """
    <h1> 문의의 처리상태를 처리됨으로 변경합니다. 어드민만 사용할 수 있습니다.</h1> </br>
    """
    if current_user.is_super is False:
        raise HTTPException(400, "관리자만 이 요청을 처리할 수 있습니다.")
    qna = crud.qna.get(db=db, id=qna_id)
    if qna is None:
        raise HTTPException(400, "처리하고자 하는 문의건을 찾을 수 없습니다.")
    if qna.is_solved is True:
        raise HTTPException(400, "이미 처리된 문의건입니다.")
    crud.qna.update(db=db, db_obj=qna, obj_in={"is_solved": True})
    return schemas.BaseResponse(object=qna_id, message=f"유저 ID: #{current_user.id}가 문의 #{qna_id}를 처리하였습니다.")


@router.get("/list", name="문의 리스트 불러오기 (어드민용)")
async def get_qna_list(
        page_request: dict = Depends(deps.get_page_request),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user),
) -> List[schemas.Qna]:
    """
    <h1> 등록된 문의 리스트를 확인합니다. 어드민만 사용할 수 있습니다. </h1> </br>
    pagination이 구현되어있어, "page_meta"에 페이지네이션에 대한 정보가 기록되어 옵니다.</br>
    """
    if current_user.is_super is False:
        raise HTTPException(400, "관리자만 이 요청을 처리할 수 있습니다.")
    return crud.qna.get_list_pagenated(db=db, page_request=page_request)
