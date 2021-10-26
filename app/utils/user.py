import random
from datetime import datetime
from itertools import product

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.users import NicknameCounter

nicknames = []
character_images = ["koala", "panda", "lion", "tiger", "fox", "rabbit", "bear", "dog", "cat"]

def open_nickname_csv(file_path: str) -> list:
    with open(file_path, 'r') as csv_file:
        lines = csv_file.readlines()
    return lines


def make_nickname_list(lines: list, empty_list: list):
    first = []
    second = []
    for line in lines:
        data = line.split(',')
        first.append(data[0])
        trimed_second = data[1].rstrip('\n')
        if trimed_second == '':
            pass
        else:
            second.append(data[1].rstrip('\n'))

    nickname_combination = product(first, second)
    list_nickname = list(nickname_combination)
    [empty_list.append(i[0] + " " + i[1]) for i in list_nickname]
    random.seed(192021)
    random.shuffle(empty_list)
    return empty_list


# TODO 14000개 이후 순환하는 루틴 만들기
def nickname_randomizer(db: Session = SessionLocal()):
    try:
        counter = db.query(NicknameCounter).first()
        if counter is None:
            db_obj = NicknameCounter(counter=1)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            if len(nicknames) == 0:
                nickname_list = make_nickname_list(open_nickname_csv("../nickname_csv.csv"), [])
                return nickname_list[db.query(NicknameCounter).first().counter]
            return nicknames[db.query(NicknameCounter).first().counter]
        else:
            counter.counter += 1
            db.commit()
            db.refresh(counter)
            if len(nicknames) == 0:
                nickname_list = make_nickname_list(open_nickname_csv("../nickname_csv.csv"), [])
                return nickname_list[db.query(NicknameCounter).first().counter]
            return nicknames[db.query(NicknameCounter).first().counter]
    finally:
        db.close()


def character_image_randomizer() -> str:
    i = random.randrange(len(character_images))
    return character_images[i]


def calculate_birth_year_from_age(age: int) -> int:
    birth_age = datetime.now().year - age + 1
    return birth_age


# for debugging
if __name__ == "__main__":
    # print(nickname_randomizer())
    # print(calculate_birth_year_from_age(28))
    print(character_image_randomizer())
