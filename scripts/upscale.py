import os
import requests
from io import BytesIO
from PIL import Image
import base64
import scripts.utils as utils
from pyrogram.types import InputMediaPhoto

SD_URL = "http://192.168.0.66:7860"


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
    reply = call.message.reply_animation(
        animation="./static/noise.gif",
        caption=f"{job_name} image\n"
        f"\n"
        f"Position in queue: {str(len(queue))} "
        f"{'(Pending)' if len(queue) > 0 else ''}\n"
        f"\n"
        f"Original Image by [@{username}]"
        f"(tg://user?id={user_id})",
    )
    utils.add_to_queue(
        client, reply, queue, job_id, job_name, "", username, user_id, True
    )

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
    image = Image.open(file_path)
    image = img2b64(image)

    payload = {
        "resize_mode": 0,
        "upscaling_resize": 4,
        "upscaler_1": "4x_foolhardy_Remacri (1)",
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

    reply.edit_media(
        media=InputMediaPhoto(
            media=f"{upscaled_image_path}",
            caption=f"Upscaled image\n"
            f"**Original Image by [@{username}]"
            f"(tg://user?id={user_id})**",
        )
    )
    queue.pop(0)
