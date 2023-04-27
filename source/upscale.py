import os
import requests
from io import BytesIO
from PIL import Image
import base64
import utils as utils
from pyrogram import errors as pyrogram_errors
from pyrogram.types import InputMediaPhoto, InputMediaDocument

import json

from consts import SD_URL


def img2b64(image):
    buff = BytesIO()
    image.save(buff, format="png")
    img_str = base64.b64encode(buff.getvalue())
    return str(img_str).removeprefix("b'").removesuffix("'")


def upscale_fast(client, call, queue):
    job_id = utils.generate_job_id(16)
    job_name = "Upscaling"
    filename = ""
    args = call.data.split("/")
    args.pop(0)
    username, image_job_id, index, user_id = args
    main_folder = f"./output/txt2img/{username}/"
    for folder in os.listdir(main_folder):
        if image_job_id in folder:
            main_folder += f"{folder}/"
            break
    file_path = main_folder
    for file in os.listdir(file_path):
        if file[0] == index:
            file_path += file
            filename = file.replace(".png", "").replace(image_job_id, job_id)
            break
    with open(f"{main_folder}/gen_info.json") as json_file:
        payload = json.load(json_file)
    with open(f"{main_folder}/user_info.json") as json_file:
        user_info = json.load(json_file)
    reply = call.message.reply_animation(
        animation="./static/noise.gif",
        caption=f"{job_name} image using prompt:\n**{user_info['orig_prompt']}**\n"
        f"\n"
        f"Position in queue: {str(len(queue))} "
        f"{'(Pending)' if len(queue) > 0 else ''}\n"
        f"\n"
        f"by [@{call.from_user.username}]"
        f"(tg://user?id={call.from_user.id})\n",
    )
    utils.add_to_queue(
        client,
        reply,
        queue,
        job_id,
        job_name,
        user_info["orig_prompt"],
        call.from_user.username,
        call.from_user.id,
    )

    image = Image.open(file_path)
    image = img2b64(image)

    payload = {
        "resize_mode": 0,
        "upscaling_resize": 4,
        "upscaler_1": "4x_foolhardy_Remacri",
        "image": image,
    }
    upscaled_image_path = f"{main_folder}/{filename}.jpg"
    if not os.path.isfile(upscaled_image_path):
        r = requests.post(
            url=f"{SD_URL}/sdapi/v1/extra-single-image", json=payload
        ).json()
        filename += "--upscaled"
        upscaled_image = Image.open(BytesIO(base64.b64decode(r["image"])))
        upscaled_image.save(upscaled_image_path)
    try:
        reply.edit_media(
            media=InputMediaPhoto(
                media=f"{upscaled_image_path}",
                caption="Upscaled image\n"
                + "\n"
                + f"Prompt: **{user_info['orig_prompt']}**\n"
                + (
                    f"Negative Prompt: **{user_info['negative_prompt']}**\n"
                    if user_info["negative_prompt"]
                    else ""
                )
                + "\n"
                + f"**Upscaled by [@{call.from_user.username}]"
                + f"(tg://user?id={call.from_user.id})**\n"
                + f"**Original Image by [@{username}]"
                + f"(tg://user?id={user_id})**",
            )
        )
    except pyrogram_errors.bad_request_400.PhotoInvalidDimensions:
        reply.edit_media(
            media=InputMediaDocument(
                media=f"{upscaled_image_path}",
                caption="Upscaled image\n"
                + "\n"
                + f"Prompt: **{user_info['orig_prompt']}**\n"
                + (
                    f"Negative Prompt: **{user_info['negative_prompt']}**\n"
                    if user_info["negative_prompt"]
                    else ""
                )
                + "\n"
                + f"**Upscaled by [@{call.from_user.username}]"
                + f"(tg://user?id={call.from_user.id})**\n"
                + f"**Original Image by [@{username}]"
                + f"(tg://user?id={user_id})**",
            )
        )
    queue.pop(0)
