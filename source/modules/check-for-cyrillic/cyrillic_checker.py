import re


def contains_cyrillic(prompt):
    return bool(re.search('[а-яА-Я]', prompt))


if __name__ == "__main__":
    print(contains_cyrillic("привет"))
    print(contains_cyrillic("ПРИВЕТ"))
    print(contains_cyrillic("Hello World!"))
    print(contains_cyrillic("Hello World!п"))
