import re
from PIL import Image
from math import sqrt, floor, ceil
from googletrans import Translator
import os
import json
import random
import string

MAX_SEED_VALUE = 9999999999999999999

TXT2IMG_DEFAULT_VALUES = {
    "ar": "1:1",
    "count": 4,
    "model": "illuminati_v1.1",
    "seed": -1,
    "cfg": 5.0,
    "facefix": "0",
    "style": "default",
    "negative": "",
}

TXT2IMG_AVAILABLE_ARGS = (
    "prompt",
    "ar",
    "count",
    "model",
    "seed",
    "cfg",
    "facefix",
    "style",
    "negative",
)

AVAILABLE_STYLES = ("default", "realistic", "art", "pixel-art")

AVAILABLE_MODELS = ("illuminati_v1.1", "original_sd_1.5", "original_sd_2.1")

ASPECT_RATIO_DICT = {
    "16:9": {"width": 1024, "height": 576},
    "4:3": {"width": 768, "height": 576},
    "1:1": {"width": 768, "height": 768},
    "9:16": {"width": 576, "height": 1024},
    "3:4": {"width": 576, "height": 768},
}

CYRILLIC_ALPHABET = set("абвгдеёжзийклмнопрстуфхцчшщъыьэюя")

translator = Translator()


def json_to_dict(path, model="") -> dict:
    filename = os.path.join(path)
    try:
        with open(filename, mode="r", encoding="UTF-8") as f:
            return (json.loads(f.read())[model] if model
                    else json.loads(f.read()))
    except FileNotFoundError:
        return {}


def get_generation_args(command, defaults):
    args = re.split(" --|--| —|—", command.text)
    args[0] = args[0].split(" ", 1)
    if len(args[0]) == 1:
        return False
    args[0][0] = "prompt"
    try:
        args[1:] = map(lambda param: re.split(" ", param, 1), args[1:])
        args = dict(args)
    except ValueError:
        return False
    return defaults | args


def check_args(args, available_args):
    try:
        assert not sorted(set(args).difference(available_args))
        assert args["prompt"]
        assert args["ar"] in ASPECT_RATIO_DICT
        assert int(args["count"]) >= 1 and int(args["count"]) <= 4
        assert int(args["seed"]) == -1 or (
            int(args["seed"]) >= 1 and int(args["seed"]) <= MAX_SEED_VALUE
        )
        assert float(args["cfg"]) >= 1.0 and float(args["cfg"]) <= 15.0
        assert int(args["facefix"]) == 0 or int(args["facefix"]) == 1
        assert args["style"] in AVAILABLE_STYLES
        assert args["model"] in AVAILABLE_MODELS
    except AssertionError:
        return False
    except KeyError:
        pass
    return True


def create_image_grid(imgs):
    imgs_count = len(imgs)
    rows = floor(sqrt(imgs_count))
    cols = ceil(imgs_count / rows)
    w, h = imgs[0].size
    grid = Image.new("RGB", size=(cols * w, rows * h))
    for i, img in enumerate(imgs):
        grid.paste(img, box=(i % cols * w, i // cols * h))
    return grid


def contains_cyrillic(prompt, alphabet=CYRILLIC_ALPHABET):
    return not alphabet.isdisjoint(prompt.lower())


def translate_prompt(prompt):
    if contains_cyrillic(prompt):
        return translator.translate(prompt, dest="en", src="ru").text
    else:
        return prompt


def clean_prompt(prompt):
    return re.sub(r'[/\\:*?"<>\|]', "", prompt)[:40]


def get_json_from_info(response):
    info = response["info"].replace("\\", "")
    data = json.loads(info)
    return data


def generate_job_id(length):
    characters = string.ascii_letters + string.digits
    job_id = "".join(random.choice(characters) for i in range(length))
    return job_id


def add_to_queue(reply, queue, job_id, job_name, prompt, username, user_id):
    queue.append(job_id)
    job_index = queue.index(job_id)
    while queue[0] != job_id:
        prev_index = job_index
        job_index = queue.index(job_id)
        if prev_index != job_index:
            reply.edit_text(
                text=f"{job_name} image using prompt:\n**{prompt}**\n"
                f"\n"
                f"Position in queue: {job_index} (Pending)\n"
                f"\n"
                f"by [@{username}]"
                f"(tg://user?id={user_id})"
            )
    reply.edit_text(
        text=f"{job_name} image using prompt:\n**{prompt}**\n"
        f"\n"
        f"Position in queue: 0 (Processing)\n"
        f"\n"
        f"by [@{username}]"
        f"(tg://user?id={user_id})"
    )
