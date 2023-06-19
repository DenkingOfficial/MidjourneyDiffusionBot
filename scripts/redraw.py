import base64
import os
from io import BytesIO
from PIL import Image
import requests
from pyrogram import errors as pyrogram_errors
from pyrogram.types import InputMediaPhoto, InputMediaDocument
from scripts.consts import SD_URL, REDRAW_HELP_TEXT
import scripts.utils as utils


class Redraw:
    def __init__(self, queue, message):
        self.message = message
        self.queue = queue

    @staticmethod
    def _img2b64(image):
        buff = BytesIO()
        image.save(buff, format="png")
        img_str = base64.b64encode(buff.getvalue())
        return str(img_str, "utf-8")

    @staticmethod
    def parse_message_text(text):
        prompt = text.replace("/redraw", "").split(" ", 1)[-1]
        if not prompt:
            return False
        return prompt

    @staticmethod
    def nearest_divisible_by_8(resolution):
        width, height = resolution
        nearest_width = round(width / 8) * 8
        nearest_height = round(height / 8) * 8
        return (nearest_width, nearest_height)

    def _redraw_payload_former(self):
        prompt = None
        if self.message.caption and self.message.photo:
            prompt = self.parse_message_text(self.message.caption)
        if not prompt:
            return False

        image_path = self.message.download()
        image = Image.open(image_path)
        w, h = self.nearest_divisible_by_8(image.size)

        base64_img = self._img2b64(image)
        os.remove(image_path)
        self.prompt = prompt
        payload = {
            "prompt": utils.translate_prompt(prompt),
            "negative_prompt": "BadDream, (UnrealisticDream:1.2), (deformed, distorted, disfigured:1.3), poorly drawn, bad anatomy, wrong anatomy, extra limb, missing limb, floating limbs, (mutated hands and fingers:1.4), disconnected limbs, mutation, mutated, ugly, disgusting, blurry",
            "batch_size": 1,
            "steps": 10,
            "cfg_scale": 7,
            "sampler_index": "DPM++ 2M SDE",
            "width": w,
            "height": h,
            "override_settings": {
                "sd_model_checkpoint": "Misc\\dreamshaper_631BakedVae.safetensors [2336dbf342]",
                "sd_vae": "None",
            },
            "alwayson_scripts": {
                "controlnet": {
                    "args": [
                        {
                            "input_image": base64_img,
                            "module": "softedge_hed",
                            "model": "control_v11p_sd15_softedge [a8575a2a]",
                            "weight": 1,
                            "resize_mode": 1,
                            "lowvram": True,
                            "pixel_perfect": True,
                        }
                    ],
                },
                "Tiled VAE": {
                    "args": ["True", 1024, 96, "False", "False", "False", "False"],
                },
            },
        }
        return payload

    def _change_cn_config(self, version):
        endpoint = f"{SD_URL}/sdapi/v1/options"
        payload = {
            "control_net_model_config": f"models\\cldm_v{version}.yaml",
        }
        requests.post(endpoint, json=payload)

    def _process_image(self, path, payload):
        r = requests.post(f"{SD_URL}/sdapi/v1/txt2img", json=payload).json()
        redrawn_image = Image.open(BytesIO(base64.b64decode(r["images"][0])))
        processed_filename = f"{self.message.from_user.username}-{self.job_id}.png"
        redrawn_image.save(os.path.join(path, processed_filename))

    def _present_results(self, path, reply):
        processed_filename = f"{self.message.from_user.username}-{self.job_id}.png"
        file_path = os.path.join(path, processed_filename)
        caption = (
            "Redrawn image\n"
            + f"Prompt: **{self.prompt}**\n"
            + f"\n**Redrawn by [@{self.message.from_user.username}](tg://user?id={self.message.from_user.id})**\n"
        )

        try:
            media = InputMediaPhoto(media=file_path, caption=caption)
            reply.edit_media(media=media)
        except pyrogram_errors.bad_request_400.PhotoInvalidDimensions:
            media = InputMediaDocument(media=file_path, caption=caption)
            reply.edit_media(media=media)

    def process(self):
        self.job_id = utils.generate_job_id(16)
        path = f"./output/redraw/{self.message.from_user.username}/"
        payload = self._redraw_payload_former()

        if not payload:
            self.message.reply(REDRAW_HELP_TEXT)
            return

        reply_message = utils.reply_redraw_template(
            self.queue, self.message, self.prompt
        )
        reply = self.message.reply_animation(**reply_message)

        utils.add_to_queue_redraw(
            reply, self.queue, self.job_id, self.message, self.prompt
        )

        if not os.path.exists(path):
            os.makedirs(path)
        self._change_cn_config("21")
        self._process_image(path, payload)
        self._present_results(path, reply)
        self._change_cn_config("15")
        self.queue.pop(0)
