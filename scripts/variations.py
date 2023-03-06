import os
import requests
from io import BytesIO
from PIL import Image, PngImagePlugin
import base64
import scripts.utils as utils
from pyrogram.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
import json

SD_URL = "http://192.168.0.66:7860"


def variations(client, call, queue):
    job_id = utils.generate_job_id(16)
    job_name = "Generating variations for"
    args = call.data.split("/")
    args.pop(0)
    username, image_job_id, seed = args
    main_folder = f"./output/txt2img/{username}/"
    for folder in os.listdir(main_folder):
        if image_job_id in folder:
            main_folder += f"{folder}/"
            break
    with open(f"{main_folder}/gen_info.json") as json_file:
        payload = json.load(json_file)
    with open(f"{main_folder}/user_info.json") as json_file:
        user_info = json.load(json_file)
    payload["seed"] = int(seed)
    payload["subseed_strength"] = 0.1
    payload["batch_size"] = 4
    reply = call.message.reply_animation(
        animation="./static/noise.gif",
        caption=f"{job_name} image using prompt:\n**{user_info['orig_prompt']}**\n"
        f"\n"
        f"Position in queue: {str(len(queue))} "
        f"{'(Pending)' if len(queue) > 0 else ''}\n"
        f"\n"
        f"by [@{call.from_user.username}]"
        f"(tg://user?id={call.from_user.id})",
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
        False,
    )
    r = requests.post(url=f"{SD_URL}/sdapi/v1/txt2img", json=payload).json()
    list_of_subseeds = utils.get_json_from_info(r)["all_subseeds"]
    filename = utils.clean_prompt(user_info["orig_prompt"])
    filename += f"--{job_id}"
    path = f"./output/txt2img/{call.from_user.username}/{filename}"
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)
    images_list = []
    for index, img in enumerate(r["images"]):
        image = Image.open(BytesIO(base64.b64decode(img.split(",", 1)[0])))
        images_list.append(image)
        word = f"{index}-{filename}-{list_of_subseeds[index]}"
        png_payload = {"image": "data:image/png;base64," + img}
        response2 = requests.post(url=f"{SD_URL}/sdapi/v1/png-info", json=png_payload)
        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))
        image.save(f"{path}/{word}.png", pnginfo=pnginfo)
    grid = utils.create_image_grid(images_list)
    grid.save(f"{path}/{filename}-grid.jpg")
    subseeds_str = [f"`{str(seed)}`" for seed in list_of_subseeds]
    queue.pop(0)
    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Upscale an image:", callback_data="_")],
            [
                InlineKeyboardButton(
                    text=str(i + 1),
                    callback_data=f"UF/{call.from_user.username}/{job_id}/{i}/{call.from_user.id}",
                )
                for i in range(len(images_list))
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Regenerate variations",
                    callback_data=f"V/{call.from_user.username}/{image_job_id}/{seed}",
                )
            ],
        ]
    )
    reply.edit_media(
        media=InputMediaPhoto(
            media=f"{path}/{filename}-grid.jpg",
            caption=f"Prompt: **{user_info['orig_prompt']}**\n"
            f"Seed: `{payload['seed']}`\n"
            f"Subseeds: {', '.join(subseeds_str)}\n"
            f"**Generated by [@{call.from_user.username}]"
            f"(tg://user?id={call.from_user.id})**",
        ),
        reply_markup=inline_keyboard,
    )
