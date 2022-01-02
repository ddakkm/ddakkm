import string
import random
from typing import Dict
from ast import literal_eval

from fastapi.encoders import jsonable_encoder
import requests
import openpyxl
from openpyxl.worksheet.worksheet import Worksheet


def get_excel_sheet(file_path: str) -> Worksheet:
    with open(file_path, 'rb') as f:
        excel_file = openpyxl.load_workbook(f)
        sheet = excel_file.active
    return sheet


def login(password: str, email: str, env: str) -> Dict[str, str]:
    if env == "prod":
        url = "http://13.125.229.9:10673/v1/auth/login/local"
    else:
        url = "http://3.34.44.39/v1/auth/login/local"
    login_data = {
        "username": email,
        "password": password
    }
    r = requests.post(url, data=login_data)
    response = r.json()
    access_token = response.get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}
    return headers


def join(request_body: dict, env: str):
    if env == "prod":
        url = "http://13.125.229.9:10673/v1/auth/sign-up/local"
    else:
        url = "http://3.34.44.39/v1/auth/sign-up/local"
    r = requests.post(url, json=request_body)


def join_survey(request_body: dict, auth: dict, env: str) -> int:
    if env == "prod":
        url = "http://13.125.229.9:10673/v1/user/join-survey"
    else:
        url = "http://3.34.44.39/v1/user/join-survey"
    r = requests.post(url, json=request_body, headers=auth)
    print(r.json())
    return r.status_code


class JoinFormFactory:
    __DEFAULT_JOIN_FORM = {
        "agree_policy": True,
        "fcm_token": None
    }

    def __init__(self, gender: str, age: str):
        self.__gender = gender
        self.__age = age

    @classmethod
    def __rand_string_gen(cls) -> str:
        string_pool = string.ascii_lowercase
        result = ""
        for i in range(6):
            result += random.choice(string_pool)
        return result

    # gender = row[13], age = row[14]
    def gen_dict(self) -> dict:
        self.__DEFAULT_JOIN_FORM["age"] = int(self.__age)
        if self.__gender == "남자":
            self.__DEFAULT_JOIN_FORM["gender"] = "MALE"
        else:
            self.__DEFAULT_JOIN_FORM["gender"] = "FEMALE"
        self.__DEFAULT_JOIN_FORM["password"] = self.__rand_string_gen()
        self.__DEFAULT_JOIN_FORM["email"] = f"{self.__rand_string_gen()}@naver.com"
        return self.__DEFAULT_JOIN_FORM


class JoinSurveyFormFactory:
    __DEFAULT_JOIN_FORM = {
        "survey_type": "A",
    }

    def __init__(self,
                 content: str,
                 vaccine_type: str,
                 vaccine_round: str,
                 is_crossed: str,
                 is_pregnant: str,
                 is_underlying_disease: str,
                 date_from: str,
                 data: str,
                 ):
        if content is None:
            self.__content = ""
        else:
            self.__content = content

        if is_crossed == "FALSE":
            self.__is_crossed = False
        else:
            self.__is_crossed = True

        if is_pregnant == "FALSE":
            self.__is_pregnant = False
        else:
            self.__is_pregnant = True

        if is_underlying_disease == "FALSE":
            self.__is_underlying_disease = False
        else:
            self.__is_underlying_disease = True

        self.__review_detail = {
            "content": self.__content,
            "keywords": [],
            "images": {"image1_url": None, "image2_url": None, "image3_url": None}
        }
        self.__survey_details = {
            "vaccine_type": vaccine_type,
            "vaccine_round": vaccine_round,
            "is_crossed": self.__is_crossed,
            "is_pregnant": self.__is_pregnant,
            "is_underlying_disease": self.__is_underlying_disease,
            "date_from": date_from,
            "data": literal_eval(data)
        }

    def gen_dict(self) -> dict:
        self.__DEFAULT_JOIN_FORM["survey_details"] = self.__survey_details
        self.__DEFAULT_JOIN_FORM["review_detail"] = self.__review_detail
        return self.__DEFAULT_JOIN_FORM


if __name__ == "__main__":
    sheet = get_excel_sheet(file_path="sulmoon_google_ddakm.xlsx")
    index = 1
    for row in sheet:
        # 컬럼 정리
        content = row[0].value
        vaccine_round = row[1].value
        vaccine_type = row[2].value
        is_crossed = row[3].value
        is_pregnant = row[4].value
        is_underlying_disease = row[5].value
        date_from = row[6].value
        data = row[15].value
        gender = row[13].value
        age = row[14].value

        # 회원의 가입용 json body
        join_form = JoinFormFactory(gender=gender, age=age).gen_dict()
        # 회원가입 API 요청
        join(join_form, "prod")

        # 로그인 API 요청
        email = join_form.get("email")
        password = join_form.get("password")
        access_token = login(password=password, email=email, env="prod")

        # 가입설문용 json body
        joinsurvey_form = JoinSurveyFormFactory(
            content=content,
            vaccine_type=vaccine_type,
            vaccine_round=vaccine_round,
            is_crossed=is_crossed,
            is_pregnant=is_pregnant,
            is_underlying_disease=is_underlying_disease,
            date_from=date_from,
            data=data
        ).gen_dict()
        body = jsonable_encoder(joinsurvey_form)

        # 가입설문 API 요청
        status_code = join_survey(request_body=body, auth=access_token, env="prod")
        if status_code != 200:
            print(f"{index} 번째 에러 발생")
        index += 1
