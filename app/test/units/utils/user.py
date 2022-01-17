import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.utils.user import calculate_birth_year_from_age, get_age_group


class TestUserUtils:
    def test_calculate_birth_year_from_age(self):
        birth_year = 1993
        exp_age = 30
        result = calculate_birth_year_from_age(birth_year)
        assert exp_age == result

    def test_get_age_group_from_age(self):
        age = 30
        exp_age_group = "3039"
        result = get_age_group(age)
        assert exp_age_group == result
