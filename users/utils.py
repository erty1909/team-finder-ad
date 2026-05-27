import io
import random

from PIL import Image, ImageDraw, ImageFont

AVATAR_COLORS = [
    "#4A90D9",
    "#7B68EE",
    "#20B2AA",
    "#3CB371",
    "#CD853F",
    "#708090",
    "#9370DB",
    "#E07B54",
]

AVATAR_SIZE = 100
AVATAR_FONT_SIZE = 52
FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
]


def generate_avatar_image(first_letter: str):
    """Generate a PNG avatar with a letter on a solid background.

    Returns raw PNG bytes, or None if generation fails.
    """
    try:
        color = random.choice(AVATAR_COLORS)
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
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), letter, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(
            ((AVATAR_SIZE - w) // 2 - bbox[0], (AVATAR_SIZE - h) // 2 - bbox[1]),
            letter,
            fill="white",
            font=font,
        )

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf.read()
    except Exception:
        return None
