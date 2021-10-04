import random


def symtom_randomizer(symptom: dict) -> dict:
    candidate_list = ["q1", "q2", "q3", "q4", "q5"]
    random.shuffle(candidate_list)
    return {candidate_list[0]: symptom.get(candidate_list[0]), candidate_list[1]: symptom.get(candidate_list[1])}


if __name__ == "__main__":
    symptom = {
        "q1": "asd",
        "q2": "asdassadfasfd",
        "q3": "asdadgfasd",
        "q4": "asdsgd",
        "q5": "asdasd"
    }
    print(symtom_randomizer(symptom))
