import io
from PIL import Image


def open_image(file):
    image = Image.open(io.BytesIO(file))
    return image
