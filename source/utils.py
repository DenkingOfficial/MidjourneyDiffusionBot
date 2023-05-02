import re
from PIL import Image
from math import sqrt, floor, ceil
from googletrans import Translator
import json
import random
import string

translator = Translator()


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


def add_to_queue(client, reply, queue, job_id, job_name, prompt, username, user_id):
    queue.append(job_id)
    first_string = f"{job_name} image using prompt:\n**{prompt}**\n"
    last_string = f"by [@{username}]"
    job_index = queue.index(job_id)
    while queue[0] != job_id:
        prev_index = job_index
        job_index = queue.index(job_id)
        if prev_index != job_index:
            reply.edit_text(
                text=f"{first_string}"
                f"\n"
                f"Position in queue: {job_index} (Pending)\n"
                f"\n"
                f"{last_string}"
                f"(tg://user?id={user_id})"
            )
    reply.edit_text(
        text=f"{first_string}"
        f"\n"
        f"Position in queue: 0 (Processing)\n"
        f"\n"
        f"{last_string}"
        f"(tg://user?id={user_id})"
    )
