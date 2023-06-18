import base64
import os
import re
from io import BytesIO
from PIL import Image
import requests
from pyrogram import errors as pyrogram_errors
from pyrogram.types import InputMediaPhoto, InputMediaDocument
from scripts.consts import SD_URL
import scripts.utils as utils


class Outpaint:
    def __init__(self, queue, message):
        self.message = message
        self.queue = queue
        self.image_big = False

    @staticmethod
    def _img2b64(image):
        buff = BytesIO()
        image.save(buff, format="png")
        img_str = base64.b64encode(buff.getvalue())
        return str(img_str, "utf-8")

    @staticmethod
    def parse_message_text(text):
        # Define flag patterns
        command_pattern = r"/outpaint"
        dir_pattern = r"(--|—)direction\s+(\w+)"
        amount_pattern = r"(--|—)amount\s+(\d+)"
        guide_pattern = r"(--|—)guide((?:(?!--|—).)*)"
        all_patterns = (
            f"{command_pattern}|{dir_pattern}|{amount_pattern}|{guide_pattern}"
        )

        # Match and extract flags and arguments
        direction_match = re.search(dir_pattern, text)
        amount_match = re.search(amount_pattern, text)
        guide_match = re.search(guide_pattern, text)

        # Remove matched flags and arguments from text
        clean_text = re.sub(all_patterns, "", text)

        # Return False if any non-whitespace characters remain after removing valid flags and arguments
        if re.search(r"\S", clean_text):
            return False

        direction = direction_match.group(2) if direction_match else "horizontal"
        if direction not in ["vertical", "horizontal"]:
            return False

        amount = int(amount_match.group(2)) if amount_match else 20
        if not (1 <= amount <= 100):
            return False

        guide = guide_match.group(2).strip() if guide_match else ""

        return {"direction": direction, "amount": amount, "guide": guide}

    @staticmethod
    def nearest_divisible_by_8(resolution):
        width, height = resolution
        nearest_width = round(width / 8) * 8
        nearest_height = round(height / 8) * 8
        return (nearest_width, nearest_height)

    def _outpaint_payload_former(self):
        params = None
        if self.message.caption and self.message.photo:
            params = Outpaint.parse_message_text(self.message.caption)
        if not params:
            return False

        image_path = self.message.download()
        image = Image.open(image_path)
        w, h = self.nearest_divisible_by_8(image.size)

        if w * h > 896 * 896:
            w //= 2
            h //= 2
            self.image_big = True

        base64_img = self._img2b64(image)
        os.remove(image_path)

        parse_result = {"image": base64_img, **params}
        self.guide_prompt = parse_result["guide"]
        payload = {
            "prompt": utils.translate_prompt(parse_result["guide"])
            if parse_result["guide"]
            else "",
            "negative_prompt": "(deformed, distorted, disfigured:1.3), poorly drawn, bad anatomy, wrong anatomy, extra limb, missing limb, floating limbs, (mutated hands and fingers:1.4), disconnected limbs, mutation, mutated, ugly, disgusting, blurry",
            "batch_size": 1,
            "steps": 30,
            "cfg_scale": 3,
            "sampler_index": "DPM++ 2M SDE",
            "enable_hr": self.image_big,
            "hr_upscaler": "4x-UltraSharp",
            "denoising_strength": 0.25,
            "hr_scale": 2,
            "width": w + w * parse_result["amount"] / 100
            if parse_result["direction"] == "horizontal"
            else w,
            "height": h + h * parse_result["amount"] / 100
            if parse_result["direction"] == "vertical"
            else h,
            "override_settings": {
                "sd_model_checkpoint": "Misc\\dreamshaper_631Inpainting.safetensors [c5372b26da]",
                "sd_vae": "model-v1-5-vae-ft-mse-840000.vae.pt",
            },
            "alwayson_scripts": {
                "controlnet": {
                    "args": [
                        {
                            "input_image": parse_result["image"],
                            "module": "inpaint_only+lama",
                            "model": "control_v11p_sd15_inpaint [ebff9138]",
                            "weight": 0.15,
                            "resize_mode": 2,
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

    def _process_image(self, path, payload):
        r = requests.post(f"{SD_URL}/sdapi/v1/txt2img", json=payload).json()
        outpainted_image = Image.open(BytesIO(base64.b64decode(r["images"][0])))
        processed_filename = f"{self.message.from_user.username}-{self.job_id}.png"
        outpainted_image.save(os.path.join(path, processed_filename))

    def _present_results(self, path, reply):
        processed_filename = f"{self.message.from_user.username}-{self.job_id}.png"
        file_path = os.path.join(path, processed_filename)
        caption = (
            "Outpainted image\n"
            + (
                f"Guidance prompt: **{self.guide_prompt}**\n"
                if self.guide_prompt
                else ""
            )
            + f"\n**Outpainted by [@{self.message.from_user.username}](tg://user?id={self.message.from_user.id})**\n"
        )

        try:
            media = InputMediaPhoto(media=file_path, caption=caption)
            reply.edit_media(media=media)
        except pyrogram_errors.bad_request_400.PhotoInvalidDimensions:
            media = InputMediaDocument(media=file_path, caption=caption)
            reply.edit_media(media=media)

    def process(self):
        self.job_id = utils.generate_job_id(16)
        path = f"./output/outpaint/{self.message.from_user.username}/"
        payload = self._outpaint_payload_former()

        if not payload:
            self.message.reply(
                "Please send an image with this command. Also check arguments"
            )
            return

        reply_message = utils.reply_outpaint_template(
            self.queue, self.message, self.guide_prompt
        )
        reply = self.message.reply_animation(**reply_message)

        utils.add_to_queue_outpaint(
            reply, self.queue, self.job_id, self.message, self.guide_prompt
        )

        if not os.path.exists(path):
            os.makedirs(path)

        self._process_image(path, payload)
        self._present_results(path, reply)
        self.queue.pop(0)
