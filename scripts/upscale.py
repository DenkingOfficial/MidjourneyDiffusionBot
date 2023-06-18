import os
import requests
from io import BytesIO
from PIL import Image
import base64
import scripts.utils as utils
from pyrogram import errors as pyrogram_errors
from pyrogram.types import InputMediaPhoto, InputMediaDocument

import json

from scripts.consts import SD_URL


class Upscale:
    def __init__(self, queue):
        self.queue = queue
        self.job_name = "Upscaling"
        self.job_id = None
        self.user_info = {}
        self.file_path = ""
        self.upscaled_file_path = ""

    def _img2b64(self, image):
        buff = BytesIO()
        image.save(buff, format="png")
        img_str = base64.b64encode(buff.getvalue())
        return str(img_str).removeprefix("b'").removesuffix("'")

    def _get_data_for_upscale(self, call):
        username, image_job_id, index = call.data.split("/")[1:]
        main_folder = f"./output/txt2img/{username}/"

        main_folder = next(
            os.path.join(main_folder, folder)
            for folder in os.listdir(main_folder)
            if image_job_id in folder
        )

        file_name, upscaled_file_name = self._find_target_file(
            main_folder, index, image_job_id, self.job_id
        )
        self.file_path = os.path.join(main_folder, file_name)
        self.upscaled_file_path = os.path.join(main_folder, upscaled_file_name)

        with open(os.path.join(main_folder, "user_info.json")) as json_file:
            self.user_info = json.load(json_file)

    def _find_target_file(self, main_folder, index, image_job_id, job_id):
        for file in os.listdir(main_folder):
            if file.startswith(index):
                new_filename = file.replace(".png", "-upscaled.jpg").replace(
                    image_job_id, job_id
                )
                return file, new_filename
        return "", ""

    def _prepare_data(self):
        image = Image.open(self.file_path)
        image = self._img2b64(image)
        payload = {
            "resize_mode": 0,
            "upscaling_resize": 4,
            "upscaler_1": "4x_foolhardy_Remacri",
            "image": image,
        }
        return payload

    def _process_image(self):
        payload = self._prepare_data()
        if not os.path.isfile(self.upscaled_file_path):
            r = requests.post(
                url=f"{SD_URL}/sdapi/v1/extra-single-image", json=payload
            ).json()
            upscaled_image = Image.open(BytesIO(base64.b64decode(r["image"])))
            upscaled_image.save(self.upscaled_file_path)

    def _present_results(self, reply, call=None):
        try:
            reply.edit_media(
                media=InputMediaPhoto(
                    media=f"{self.upscaled_file_path}",
                    caption="Upscaled image\n"
                    + "\n"
                    + f"Prompt: **{self.user_info['orig_prompt']}**\n"
                    + (
                        f"Negative Prompt: **{self.user_info['negative_prompt']}**\n"
                        if self.user_info["negative_prompt"]
                        else ""
                    )
                    + "\n"
                    + f"**Upscaled by [@{call.from_user.username}]"
                    + f"(tg://user?id={call.from_user.id})**\n"
                    + f"**Original Image by [@{self.user_info['username']}]"
                    + f"(tg://user?id={self.user_info['user_id']})**",
                )
            )
        except pyrogram_errors.bad_request_400.PhotoInvalidDimensions:
            reply.edit_media(
                media=InputMediaDocument(
                    media=f"{self.upscaled_file_path}",
                    caption="Upscaled image\n"
                    + "\n"
                    + f"Prompt: **{self.user_info['orig_prompt']}**\n"
                    + (
                        f"Negative Prompt: **{self.user_info['negative_prompt']}**\n"
                        if self.user_info["negative_prompt"]
                        else ""
                    )
                    + "\n"
                    + f"**Upscaled by [@{call.from_user.username}]"
                    + f"(tg://user?id={call.from_user.id})**\n"
                    + f"**Original Image by [@{self.user_info['username']}]"
                    + f"(tg://user?id={self.user_info['user_id']})**",
                )
            )

    def process(self, call):
        self.job_id = utils.generate_job_id(16)
        self._get_data_for_upscale(call)
        reply_message = utils.reply_template(
            self.job_name, self.queue, self.user_info, upscale=True
        )
        reply = call.message.reply_animation(**reply_message)
        utils.add_to_queue(
            reply,
            self.queue,
            self.job_id,
            self.job_name,
            self.user_info["orig_prompt"],
            call.from_user.username,
            call.from_user.id,
        )
        self._process_image()
        self._present_results(reply, call)
        self.queue.pop(0)
