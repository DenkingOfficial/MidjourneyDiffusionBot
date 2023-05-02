import os
import requests
import json
import io
from PIL import Image, PngImagePlugin
import base64
import utils

from types import SimpleNamespace
from pyrogram.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
from get_settings import get_settings
from dependencies import DependencyContainer

from app_reply import HELP
from consts import SD_URL

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

ASPECT_RATIO_DICT = {
    "16:9": {"width": 1024, "height": 576},
    "4:3": {"width": 768, "height": 576},
    "1:1": {"width": 768, "height": 768},
    "9:16": {"width": 576, "height": 1024},
    "3:4": {"width": 576, "height": 768},
}


def txt2img(client, message, deps: DependencyContainer):
    queue = deps.queue
    args = utils.get_generation_args(message)
    try:
        assert args
        assert utils.check_args(args, TXT2IMG_AVAILABLE_ARGS)
    except AssertionError:
        message.reply_text(HELP)
        return

    args = SimpleNamespace(**args)
    job_id = utils.generate_job_id(16)
    job_name = "Generating"
    reply = message.reply_animation(
        animation="./static/noise.gif",
        caption=f"{job_name} image using prompt:\n**{args.prompt}**\n"
        f"\n"
        f"Position in queue: {str(len(queue))} "
        f"{'(Pending)' if len(queue) > 0 else ''}\n"
        f"\n"
        f"by [@{message.from_user.username}]"
        f"(tg://user?id={message.from_user.id})",
        quote=True,
    )
    utils.add_to_queue(
        client,
        reply,
        queue,
        job_id,
        job_name,
        args.prompt,
        message.from_user.username,
        message.from_user.id,
    )
    args.gen_prompt = utils.translate_prompt(args.prompt)
    if args.negative:
        args.gen_negative = utils.translate_prompt(args.negative)
    model_path = get_settings(args.model)["model_path"]
    styles = get_settings(args.model)["styles"]
    override_settings = {}
    override_settings["sd_model_checkpoint"] = model_path
    override_payload = {"override_settings": override_settings}
    alwayson_scripts = {}
    if args.hr == "1":
        alwayson_scripts["Tiled VAE"] = {
            "args": ["True", "False", "False", "False", "False", 1024, 96]
        }
    alwayson_payload = {"alwayson_scripts": alwayson_scripts}

    payload = (
        {
            "prompt": args.gen_prompt + styles[args.style]["prompt_addition"],
            "negative_prompt": styles[args.style]["negative_prompt"]
            + (f", {args.gen_negative}" if args.negative else ""),
            "cfg_scale": float(args.cfg),
            "sampler_index": "Euler",
            "steps": 10,
            "batch_size": int(args.count) if args.hr != "1" else 1,
            "n_iter": int(args.count) if args.hr == "1" else 1,
            "seed": int(args.seed),
            "restore_faces": args.facefix == "1",
            "enable_hr": args.hr == "1",
            "hr_upscaler": "4x-UltraSharp",
            "denoising_strength": 0.25,
        }
        | ASPECT_RATIO_DICT[args.ar]
        | override_payload
        | alwayson_payload
    )
    print(f"Payload: {payload}")
    r = requests.post(url=f"{SD_URL}/sdapi/v1/txt2img", json=payload).json()
    print(f"Username: {message.from_user.username}")
    print(f'Prompt: {payload["prompt"]}')
    list_of_seeds = utils.get_json_from_info(r)["all_seeds"]
    filename = utils.clean_prompt(args.prompt)
    filename += f"--{job_id}"
    path = f"./output/txt2img/{message.from_user.username}/{filename}"
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)

    images_list = []
    for index, img in enumerate(r["images"]):
        image = Image.open(io.BytesIO(base64.b64decode(img.split(",", 1)[0])))
        images_list.append(image)
        word = f"{index}-{filename}-{list_of_seeds[index]}"
        png_payload = {"image": "data:image/png;base64," + img}
        response2 = requests.post(url=f"{SD_URL}/sdapi/v1/png-info", json=png_payload)
        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))
        image.save(f"{path}/{word}.png", pnginfo=pnginfo)
    grid = utils.create_image_grid(images_list)
    grid.save(f"{path}/{filename}-grid.jpg")
    seeds_str = [f"`{str(seed)}`" for seed in list_of_seeds]
    queue.pop(0)
    user_info = {
        "username": message.from_user.username,
        "user_id": message.from_user.id,
        "job_id": job_id,
        "orig_prompt": args.prompt,
        "negative_prompt": args.negative,
    }
    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Upscale an image:", callback_data="_")],
            [
                InlineKeyboardButton(
                    text=str(i + 1),
                    callback_data=f"UF/{message.from_user.username}/{job_id}/{i}/{message.from_user.id}",
                )
                for i in range(len(images_list))
            ],
            [InlineKeyboardButton(text="Generate variations:", callback_data="_")],
            [
                InlineKeyboardButton(
                    text=str(i + 1),
                    callback_data=f"V/{message.from_user.username}/{job_id}/{list_of_seeds[i]}",
                )
                for i in range(len(images_list))
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Regenerate (Count)",
                    callback_data="_",
                )
            ],
            [
                InlineKeyboardButton(
                    text=str(i + 1),
                    callback_data=f"RG/{message.from_user.username}/{job_id}/{str(i + 1)}",
                )
                for i in range(4)
            ],
        ]
    )

    reply.edit_media(
        media=InputMediaPhoto(
            media=f"{path}/{filename}-grid.jpg",
            caption=f"Prompt: **{args.prompt}**\n"
            + (f"Negative Prompt: **{args.negative}**\n" if args.negative else "")
            + f"Seed: {', '.join(seeds_str)}\n"
            + "\n"
            + f"**Generated by [@{message.from_user.username}]"
            + f"(tg://user?id={message.from_user.id})**",
        ),
        reply_markup=inline_keyboard,
    )
    with open(f"{path}/gen_info.json", "w") as fp:
        json.dump(payload, fp)
    with open(f"{path}/user_info.json", "w") as fp:
        json.dump(user_info, fp)
