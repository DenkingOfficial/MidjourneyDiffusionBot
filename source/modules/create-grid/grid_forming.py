from PIL import Image
from math import sqrt, floor, ceil


def create_image_grid(imgs):
    imgs_count = len(imgs)
    cols = floor(sqrt(imgs_count))
    rows = ceil(imgs_count / cols)
    w, h = imgs[0].size
    grid = Image.new("RGB", size=(cols * w, rows * h))
    for i, img in enumerate(imgs):
        grid.paste(img, box=(i % cols * w, i // cols * h))
    return grid
