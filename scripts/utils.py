import re
from PIL import Image
from math import sqrt, floor, ceil
from pyrogram import errors as pyrogram_errors
from yandexfreetranslate import YandexFreeTranslate
from langdetect import detect
import json
import random
import string
from scripts.consts import (
    DEFAULT_VALUES,
    AVAILABLE_STYLES_DICT,
    AVAILABLE_MODELS_DICT,
    AVAILABLE_ASPECT_RATIO_DICT,
    MAX_SEED_VALUE,
)

translator = YandexFreeTranslate(api="ios")


def get_generation_args(command):
    args = re.split(" --|--| —|—", command.text)
    args[0] = args[0].split(" ", 1)
    if len(args[0]) == 1:
        return False
    args[0][0] = "prompt"
    try:
        args[1:] = map(lambda param: re.split(" ", param, 1), args[1:])
        args = dict(args)  # type: ignore
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
    if detect(prompt) != "en":
        return translator.translate(text=prompt, target="en")
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
    first_string = f"{job_name} изображения:\n**{prompt}**\n"
    last_string = f"От [@{username}]"
    job_index = queue.index(job_id)
    while queue[0] != job_id:
        prev_index = job_index
        job_index = queue.index(job_id)
        if prev_index != job_index:
            try:
                reply.edit_text(
                    text=f"{first_string}"
                    f"\n"
                    f"Позиция в очереди: {job_index} (Ожидает)\n"
                    f"\n"
                    f"{last_string}"
                    f"(tg://user?id={user_id})"
                )
            except pyrogram_errors.bad_request_400.MessageNotModified:
                pass
    reply.edit_text(
        text=f"{first_string}"
        f"\n"
        f"Позиция в очереди: 0 (В процессе)\n"
        f"\n"
        f"{last_string}"
        f"(tg://user?id={user_id})"
    )


def add_to_queue_outpaint(reply, queue, job_id, message, guide_prompt):
    queue.append(job_id)
    first_string = "Дорисовка изображения\n"
    last_string = f"От [@{message.from_user.username}]"
    job_index = queue.index(job_id)
    while queue[0] != job_id:
        prev_index = job_index
        job_index = queue.index(job_id)
        if prev_index != job_index:
            try:
                reply.edit_text(
                    text=f"{first_string}"
                    + (
                        f"Описание дорисовки: **{guide_prompt}**\n\n"
                        if guide_prompt
                        else "\n"
                    )
                    + f"Позиция в очереди: {job_index} (Ожидает)\n"
                    + "\n"
                    + f"{last_string}"
                    + f"(tg://user?id={message.from_user.id})"
                )
            except pyrogram_errors.bad_request_400.MessageNotModified:
                pass
    reply.edit_text(
        text=f"{first_string}"
        + (f"Описание дорисовки: **{guide_prompt}**\n\n" if guide_prompt else "\n")
        + "Позиция в очереди: 0 (В процессе)\n"
        + "\n"
        + f"{last_string}"
        + f"(tg://user?id={message.from_user.id})"
    )


def add_to_queue_redraw(reply, queue, job_id, message, prompt):
    queue.append(job_id)
    first_string = "Перерисовка изображения\n"
    last_string = f"От [@{message.from_user.username}]"
    job_index = queue.index(job_id)
    while queue[0] != job_id:
        prev_index = job_index
        job_index = queue.index(job_id)
        if prev_index != job_index:
            try:
                reply.edit_text(
                    text=f"{first_string}"
                    + f"Описание: **{prompt}**\n\n"
                    + f"Позиция в очереди: {job_index} (Ожидает)\n"
                    + "\n"
                    + f"{last_string}"
                    + f"(tg://user?id={message.from_user.id})"
                )
            except pyrogram_errors.bad_request_400.MessageNotModified:
                pass
    reply.edit_text(
        text=f"{first_string}"
        + f"Описание: **{prompt}**\n\n"
        + "Позиция в очереди: 0 (Processing)\n"
        + "\n"
        + f"{last_string}"
        + f"(tg://user?id={message.from_user.id})"
    )


def reply_template(
    job_name, queue, user_info, variations=False, regenerate=False, upscale=False
):
    position = str(len(queue))
    status = "(Ожидает)" if len(queue) > 0 else ""
    caption = (
        f"{job_name} изображения по описанию:\n**{user_info['orig_prompt']}**\n\n"
        f"Позиция в очереди: {position} {status}\n\n"
        f"От [@{user_info['username']}](tg://user?id={user_info['user_id']})"
    )
    reply = {
        "animation": "./static/noise.gif",
        "caption": caption,
    }
    if not (regenerate and variations and upscale):
        reply["quote"] = True  # type: ignore
    return reply


def reply_outpaint_template(queue, message, guide_prompt):
    position = str(len(queue))
    status = "(Ожидает)" if len(queue) > 0 else ""
    caption = (
        "Дорисовка изображения\n"
        + (f"Описание дорисовки: **{guide_prompt}**\n\n" if guide_prompt else "\n")
        + f"Позиция в очереди: {position} {status}\n"
        + f"От [@{message.from_user.username}](tg://user?id={message.from_user.id})"
    )
    reply = {"animation": "./static/noise.gif", "caption": caption, "quote": True}
    return reply


def reply_redraw_template(queue, message, prompt):
    position = str(len(queue))
    status = "(Ожидает)" if len(queue) > 0 else ""
    caption = (
        "Перерисовка изображения\n"
        + f"Описание: **{prompt}**\n\n"
        + f"Позиция в очереди: {position} {status}\n"
        + f"От [@{message.from_user.username}](tg://user?id={message.from_user.id})"
    )
    reply = {"animation": "./static/noise.gif", "caption": caption, "quote": True}
    return reply
