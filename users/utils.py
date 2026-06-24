import io
import random
from enum import StrEnum

from PIL import Image, ImageDraw, ImageFont

from .constants import AVATAR_TEXT_COLOR

AVATAR_SIZE = 100
AVATAR_FONT_SIZE = 52
FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
]


class AvatarColor(StrEnum):
    BLUE = "#4A90D9"
    SLATE_BLUE = "#7B68EE"
    TEAL = "#20B2AA"
    GREEN = "#3CB371"
    BROWN = "#CD853F"
    GRAY = "#708090"
    PURPLE = "#9370DB"
    ORANGE = "#E07B54"


def generate_avatar_image(first_letter: str):
    try:
        color = random.choice(list(AvatarColor))
        img = Image.new("RGB", (AVATAR_SIZE, AVATAR_SIZE), color)
        draw = ImageDraw.Draw(img)
        letter = first_letter.upper()

        font = None
        for path in FONT_PATHS:
            try:
                font = ImageFont.truetype(path, AVATAR_FONT_SIZE)
                break
            except OSError:
                pass
        if font is None:
            font = ImageFont.load_default(size=AVATAR_FONT_SIZE)

        bbox = draw.textbbox((0, 0), letter, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(
            ((AVATAR_SIZE - w) // 2 - bbox[0], (AVATAR_SIZE - h) // 2 - bbox[1]),
            letter,
            fill=AVATAR_TEXT_COLOR,
            font=font,
        )

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf.read()
    except Exception:
        return None
