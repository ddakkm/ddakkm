import random

from fastapi import HTTPException

from app import schemas
from app.schemas.survey import SurveyAData
from app.models.reviews import Review


# def symtom_randomizer(symptom: dict) -> dict:
#     candidate_list = ["q1", "q2", "q3", "q4", "q5"]
#     random.shuffle(candidate_list)
#     return {candidate_list[0]: symptom.get(candidate_list[0]), candidate_list[1]: symptom.get(candidate_list[1])}

def symtom_randomizer(symtom: dict) -> dict:
    candidates = dict(SurveyAData(q1=symtom.get("q1"),
                                  q2=symtom.get("q2"),
                                  q3=symtom.get("q3"),
                                  q4=symtom.get("q4"),
                                  q5=symtom.get("q5")))
    # q2_1 은 랜덤 증상에 포함되지 않는다.
    del(candidates["q2_1"])

    # 복수 선택 가능한 항목 중 문자열 답변만 있는 경우 랜덤 증상에 포함되지 않는다.
    for candidate in list(candidates.items()):
        if isinstance(candidate[1], list) and len(candidate[1]) == 1 and isinstance(candidate[1][0], str):
            del(candidates[candidate[0]])

    # 랜덤 선택을 위해 리스트로 만들고 셔플링
    candidates_list = list(candidates.items())
    random.shuffle(candidates_list)
    return dict((tuple(candidates_list[0]), tuple(candidates_list[1])))


def check_is_deleted(review: Review):
    if review.is_delete is True:
        raise HTTPException(400, "이미 삭제된 리뷰입니다.")


if __name__ == "__main__":
    symptom = {
        "q1": "asd",
        "q2": "asdassadfasfd",
        "q3": "asdadgfasd",
        "q4": "asdsgd",
        "q5": "asdasd"
    }
    print(symtom_randomizer(symptom))
