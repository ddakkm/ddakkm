import random
from itertools import product

nicknames = []

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


if __name__ == "__main__":
    lines = open_nickname_csv("../nickname_csv.csv")
    emt = []
    make_nickname_list(lines, emt)
    print(emt)
