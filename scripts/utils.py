import re
from PIL import Image
from math import sqrt, floor, ceil
from googletrans import Translator
from pyrogram import errors as pyrogram_errors
import json
import random
import string

translator = Translator()

MAX_SEED_VALUE = 9999999999999999999

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
    "hr",
)

DEFAULT_VALUES = {
    "ar": "1:1",
    "count": 4,
    "model": "illuminati_v1.1",
    "seed": -1,
    "cfg": 5.0,
    "facefix": "0",
    "style": "default",
    "negative": "",
    "hr": "0",
}

AVAILABLE_ASPECT_RATIO_DICT = ("16:9", "4:3", "1:1", "9:16", "3:4")

AVAILABLE_STYLES_DICT = ("default", "realistic", "art", "pixel-art")

AVAILABLE_MODELS_DICT = ("illuminati_v1.1", "original_sd_1.5", "original_sd_2.1")

HELP_TEXT = (
    "Format: `/imagine (Your prompt) [--argument value]`\n"
    "\n"
    "Available args:\n"
    "`--ar` — aspect ratio of an image (default: `1:1`)\n"
    "` ` Available values:\n"
    "`  ` — `1:1`\n"
    "`  ` — `16:9` or `9:16`\n"
    "`  ` — `4:3` or `3:4`\n"
    "\n"
    "`--count` — number of images to generate (default: `4`)\n"
    "` ` Available values:\n"
    "`  ` — A number in range `1-4`\n"
    "\n"
    "`--model` — which model to use (default: `illuminati_v1.1`)\n"
    "` ` Available values:\n"
    "`  ` — `illuminati_v1.1` - High quality model trained using "
    "noise offset, based on SD 2.1\n"
    "`  ` — `original_sd_2.1` - Original Stable Diffusion 2.1 model\n"
    "`  ` — `original_sd_1.5` - Original Stable Diffusion 1.5 model\n"
    "\n"
    "`--seed` — seed to use (default: `random`)\n"
    "` ` Available values:\n"
    "`  ` — A number in range `0-9999999999999999999`\n"
    "\n"
    "`--cfg` — how close prompt follows the image (default: `5`)\n"
    "` ` Available values:\n"
    "`  ` — A number in range `1-15`\n"
    "\n"
    "`--facefix` — fix faces (default: `0`)\n"
    "` ` Available values:\n"
    "`  ` — `0` - Turn off\n"
    "`  ` — `1` - Turn on\n"
    "\n"
    "`--style` — style to use\n"
    "` ` Available values:\n"
    "`  ` — `realistic` - photorealistic images\n"
    "`  ` — `art` - digital art\n"
    "`  ` — `pixel-art` - pixel art images (NOT IMPLEMENTED)"
)


def get_generation_args(command):
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
    return DEFAULT_VALUES | args


def check_args(args, available_args):
    try:
        assert not sorted(set(args).difference(available_args))
        assert args["prompt"]
        assert int(args["hr"]) == 0 or int(args["hr"]) == 1
        assert args["ar"] in AVAILABLE_ASPECT_RATIO_DICT
        assert int(args["count"]) >= 1 and int(args["count"]) <= 4
        assert int(args["seed"]) == -1 or (
            int(args["seed"]) >= 1 and int(args["seed"]) <= MAX_SEED_VALUE
        )
        assert float(args["cfg"]) >= 1.0 and float(args["cfg"]) <= 15.0
        assert int(args["facefix"]) == 0 or int(args["facefix"]) == 1
        assert args["style"] in AVAILABLE_STYLES_DICT
        assert args["model"] in AVAILABLE_MODELS_DICT
    except AssertionError:
        return False
    except KeyError:
        pass
    return True


def create_image_grid(imgs):
    imgs_count = len(imgs)
    cols = floor(sqrt(imgs_count))
    rows = ceil(imgs_count / cols)
    w, h = imgs[0].size
    grid = Image.new("RGB", size=(cols * w, rows * h))
    for i, img in enumerate(imgs):
        grid.paste(img, box=(i % cols * w, i // cols * h))
    return grid


def translate_prompt(prompt):
    if contains_cyrillic(prompt):
        return translator.translate(prompt, dest="en", src="ru").text
    else:
        return prompt


def contains_cyrillic(prompt, alphabet=set("абвгдеёжзийклмнопрстуфхцчшщъыьэюя")):
    return not alphabet.isdisjoint(prompt.lower())


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
    first_string = f"{job_name} image using prompt:\n**{prompt}**\n"
    last_string = f"by [@{username}]"
    job_index = queue.index(job_id)
    while queue[0] != job_id:
        prev_index = job_index
        job_index = queue.index(job_id)
        if prev_index != job_index:
            try:
                reply.edit_text(
                    text=f"{first_string}"
                    f"\n"
                    f"Position in queue: {job_index} (Pending)\n"
                    f"\n"
                    f"{last_string}"
                    f"(tg://user?id={user_id})"
                )
            except pyrogram_errors.bad_request_400.MessageNotModified:
                pass
    reply.edit_text(
        text=f"{first_string}"
        f"\n"
        f"Position in queue: 0 (Processing)\n"
        f"\n"
        f"{last_string}"
        f"(tg://user?id={user_id})"
    )


def reply_template(
    job_name, queue, user_info, variations=False, regenerate=False, upscale=False
):
    position = str(len(queue))
    status = "(Pending)" if len(queue) > 0 else ""
    caption = (
        f"{job_name} image using prompt:\n**{user_info['orig_prompt']}**\n\n"
        f"Position in queue: {position} {status}\n\n"
        f"by [@{user_info['username']}](tg://user?id={user_info['user_id']})"
    )
    reply = {
        "animation": "./static/noise.gif",
        "caption": caption,
    }
    if not (regenerate and variations and upscale):
        reply["quote"] = True
    return reply
