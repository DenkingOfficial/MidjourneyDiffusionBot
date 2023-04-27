from googletrans import Translator
import re

translator = Translator()


def translate_prompt(prompt):
    if bool(re.search("[а-яА-Я]", prompt)):
        return translator.translate(prompt, dest="en", src="ru").text
    else:
        return prompt


if __name__ == "__main__":
    print(translate_prompt("привет"))
    print(translate_prompt("ПРИВЕТ"))
    print(translate_prompt("Hello World!"))
    print(translate_prompt("Hello World!п"))
