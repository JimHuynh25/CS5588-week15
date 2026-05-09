from __future__ import annotations

import hashlib
import math
import random
import re
import struct
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


OUTPUT_DIR = Path("outputs")
DEFAULT_PHOTO = Path("assets/realistic-animal-clinic-preview.png")
SOUND_DIR = Path("assets/sounds")
SAMPLE_RATE = 22050

MOOD_COLORS = {
    "Calm": ((232, 242, 238), (83, 128, 118), (34, 73, 70)),
    "Hopeful": ((255, 244, 218), (226, 146, 75), (51, 93, 129)),
    "Urgent": ((252, 235, 230), (196, 83, 73), (77, 65, 92)),
    "Educational": ((237, 242, 252), (75, 112, 174), (52, 75, 96)),
}

MOOD_AUDIO = {
    "Calm": ([261.63, 329.63, 392.00, 523.25], 0.30, 0.18),
    "Hopeful": ([293.66, 369.99, 440.00, 587.33], 0.22, 0.22),
    "Urgent": ([220.00, 261.63, 329.63, 392.00], 0.14, 0.24),
    "Educational": ([246.94, 329.63, 392.00, 493.88], 0.26, 0.19),
}

ANIMAL_AUDIO = {
    "cat": ("meow", [520.0, 610.0, 470.0], 0.42, 0.23),
    "kitten": ("meow", [590.0, 700.0, 540.0], 0.38, 0.22),
    "bird": ("chirp", [1500.0, 1900.0, 1650.0], 0.08, 0.20),
    "parrot": ("chirp", [1200.0, 1750.0, 1400.0], 0.10, 0.20),
    "horse": ("neigh", [420.0, 620.0, 360.0], 0.55, 0.24),
    "cow": ("moo", [165.0, 145.0, 130.0], 0.80, 0.25),
    "dog": ("bark", [220.0, 155.0], 0.18, 0.28),
    "puppy": ("bark", [360.0, 240.0], 0.16, 0.25),
}

REAL_SOUND_TERMS = {
    "dog": [
        "dog",
        "puppy",
        "canine",
        "retriever",
        "labrador",
        "lab",
        "shepherd",
        "bulldog",
        "poodle",
        "husky",
        "terrier",
        "beagle",
    ],
    "cat": ["cat", "kitten", "feline"],
    "bird": ["bird", "parrot", "budgie", "budgerigar"],
    "horse": ["horse", "pony"],
    "cow": ["cow", "calf", "cattle"],
}


def _safe_slug(*parts: str) -> str:
    text = "-".join(parts).lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]
    return f"{text[:44].strip('-')}-{digest}" if text else digest


def _font(size: int) -> ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            pass
    return ImageFont.load_default()


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        trial = " ".join([*current, word])
        if draw.textbbox((0, 0), trial, font=font)[2] <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def _lerp_color(a: tuple[int, int, int], b: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    return tuple(int(a[i] + (b[i] - a[i]) * amount) for i in range(3))


def _draw_clinic_scene(draw: ImageDraw.ImageDraw, bg: tuple[int, int, int], accent: tuple[int, int, int]) -> None:
    wall_top = _lerp_color(bg, (255, 255, 255), 0.62)
    wall_bottom = _lerp_color(bg, (188, 196, 202), 0.28)
    for y in range(90, 720):
        amount = (y - 90) / 630
        draw.line((0, y, 1280, y), fill=_lerp_color(wall_top, wall_bottom, amount))

    draw.rectangle((0, 540, 1280, 720), fill=(215, 220, 220))
    for x in range(-120, 1280, 150):
        draw.line((x, 720, x + 280, 540), fill=(197, 204, 205), width=2)
    for y in range(560, 720, 46):
        draw.line((0, y, 1280, y), fill=(197, 204, 205), width=2)

    draw.rounded_rectangle((92, 155, 615, 500), radius=18, fill=(246, 249, 250), outline=(210, 219, 222), width=3)
    draw.rectangle((96, 405, 611, 500), fill=(232, 237, 239))
    draw.rounded_rectangle((145, 448, 555, 560), radius=18, fill=(178, 190, 196))
    draw.rounded_rectangle((126, 414, 574, 476), radius=20, fill=(242, 244, 242), outline=accent, width=4)
    draw.ellipse((236, 532, 280, 576), fill=(120, 132, 138))
    draw.ellipse((442, 532, 486, 576), fill=(120, 132, 138))
    draw.rounded_rectangle((440, 172, 584, 282), radius=10, fill=(238, 242, 244), outline=(204, 214, 218), width=3)
    draw.line((460, 206, 564, 206), fill=accent, width=5)
    draw.line((512, 154, 512, 260), fill=accent, width=5)


def _draw_fur(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], base: tuple[int, int, int], seed: str) -> None:
    digest = hashlib.sha1(seed.encode("utf-8")).digest()
    x1, y1, x2, y2 = bounds
    for i in range(220):
        byte = digest[i % len(digest)]
        x = x1 + ((byte * 37 + i * 29) % max(1, x2 - x1))
        y = y1 + ((byte * 53 + i * 17) % max(1, y2 - y1))
        length = 8 + byte % 18
        shade = _lerp_color(base, (70, 48, 32), (byte % 45) / 100)
        draw.line((x, y, x + length, y + 3), fill=shade, width=2)


def _draw_realistic_animal(
    image: Image.Image,
    animal: str,
    condition: str,
    accent: tuple[int, int, int],
    ink: tuple[int, int, int],
) -> None:
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    animal_lc = animal.lower()
    is_cat = "cat" in animal_lc or "kitten" in animal_lc
    is_dark = any(term in animal_lc for term in ["black", "lab", "rottweiler"])
    base = (82, 72, 64) if is_dark else ((194, 156, 103) if not is_cat else (170, 158, 140))
    light = _lerp_color(base, (255, 236, 198), 0.45)
    shadow = _lerp_color(base, (55, 39, 29), 0.45)

    draw.ellipse((172, 296, 520, 500), fill=(*base, 255), outline=(*shadow, 255), width=5)
    draw.ellipse((276, 190, 472, 374), fill=(*base, 255), outline=(*shadow, 255), width=5)
    draw.ellipse((222, 340, 560, 534), fill=(*light, 255), outline=(*shadow, 255), width=4)
    draw.ellipse((246, 472, 314, 586), fill=(*base, 255), outline=(*shadow, 255), width=4)
    draw.ellipse((420, 462, 492, 586), fill=(*base, 255), outline=(*shadow, 255), width=4)

    if is_cat:
        draw.polygon([(292, 234), (250, 144), (340, 206)], fill=(*base, 255), outline=(*shadow, 255))
        draw.polygon([(452, 234), (492, 144), (404, 206)], fill=(*base, 255), outline=(*shadow, 255))
    else:
        draw.pieslice((222, 202, 320, 386), start=96, end=278, fill=(*shadow, 255), outline=(*shadow, 255))
        draw.pieslice((428, 202, 526, 386), start=262, end=84, fill=(*shadow, 255), outline=(*shadow, 255))

    draw.ellipse((316, 246, 340, 272), fill=(33, 30, 27, 255))
    draw.ellipse((404, 246, 428, 272), fill=(33, 30, 27, 255))
    draw.ellipse((324, 252, 331, 259), fill=(255, 255, 255, 230))
    draw.ellipse((412, 252, 419, 259), fill=(255, 255, 255, 230))
    draw.ellipse((354, 276, 394, 304), fill=(39, 31, 29, 255))
    draw.arc((338, 292, 376, 332), start=10, end=105, fill=(*ink, 255), width=4)
    draw.arc((374, 292, 414, 332), start=75, end=170, fill=(*ink, 255), width=4)
    draw.arc((154, 306, 272, 468), start=110, end=238, fill=(*shadow, 255), width=12)

    _draw_fur(draw, (188, 214, 532, 530), base, f"{animal}-{condition}")
    draw.rounded_rectangle((214, 520, 548, 570), radius=16, fill=(*accent, 235))
    draw.text((240, 532), "realistic animal-care preview", fill=(255, 255, 255, 255), font=_font(22))

    blurred_shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(blurred_shadow)
    shadow_draw.ellipse((160, 508, 560, 604), fill=(0, 0, 0, 58))
    blurred_shadow = blurred_shadow.filter(ImageFilter.GaussianBlur(18))
    image.alpha_composite(blurred_shadow)
    image.alpha_composite(overlay)


def _cover_resize(source: Image.Image, size: tuple[int, int]) -> Image.Image:
    target_w, target_h = size
    source = source.convert("RGB")
    ratio = max(target_w / source.width, target_h / source.height)
    resized = source.resize((int(source.width * ratio), int(source.height * ratio)), Image.Resampling.LANCZOS)
    left = max(0, (resized.width - target_w) // 2)
    top = max(0, (resized.height - target_h) // 2)
    return resized.crop((left, top, left + target_w, top + target_h))


def _draw_uploaded_photo_scene(
    image: Image.Image,
    uploaded_photo: str,
    condition: str,
    accent: tuple[int, int, int],
    ink: tuple[int, int, int],
) -> bool:
    try:
        photo = Image.open(uploaded_photo)
    except (OSError, TypeError, ValueError):
        return False

    photo = _cover_resize(photo, (610, 466)).filter(ImageFilter.UnsharpMask(radius=1.4, percent=120))
    image.paste(photo, (54, 132))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((54, 132, 664, 598), radius=20, outline=accent, width=6)
    draw.rectangle((54, 534, 664, 598), fill=(0, 0, 0, 104))
    for i, line in enumerate(_wrap_text(draw, condition, _font(22), 540)[:2]):
        draw.text((82, 548 + i * 26), line, fill=(255, 255, 255), font=_font(22))
    return True


def create_preview_image(
    animal: str,
    condition: str,
    environment: str,
    mood: str,
    audience: str,
    uploaded_photo: str | None = None,
) -> str:
    OUTPUT_DIR.mkdir(exist_ok=True)
    slug = _safe_slug(animal, condition, environment, mood, audience)
    path = OUTPUT_DIR / f"{slug}-preview.png"

    bg, accent, ink = MOOD_COLORS.get(mood, MOOD_COLORS["Educational"])
    image = Image.new("RGBA", (1280, 720), (*bg, 255))
    draw = ImageDraw.Draw(image)

    title_font = _font(50)
    label_font = _font(26)
    body_font = _font(34)
    small_font = _font(22)

    _draw_clinic_scene(draw, bg, accent)

    draw.rectangle((0, 0, 1280, 90), fill=ink)
    draw.text((54, 22), "SceneSound Studio Pro", fill=(255, 255, 255), font=title_font)
    draw.rounded_rectangle((940, 24, 1208, 66), radius=12, fill=accent)
    draw.text((972, 31), f"{mood} preview", fill=(255, 255, 255), font=small_font)

    used_photo = False
    if uploaded_photo:
        used_photo = _draw_uploaded_photo_scene(image, uploaded_photo, condition, accent, ink)
    if not used_photo and DEFAULT_PHOTO.exists():
        used_photo = _draw_uploaded_photo_scene(image, str(DEFAULT_PHOTO), condition, accent, ink)
    if not used_photo:
        _draw_realistic_animal(image, animal, condition, accent, ink)

    x = 710
    draw.rounded_rectangle((680, 126, 1218, 632), radius=18, fill=(255, 255, 255), outline=(220, 226, 229), width=3)
    draw.text((x, 144), "Subject", fill=accent, font=label_font)
    for i, line in enumerate(_wrap_text(draw, animal.title(), body_font, 470)[:2]):
        draw.text((x, 182 + i * 42), line, fill=ink, font=body_font)

    draw.text((x, 292), "Care Scenario", fill=accent, font=label_font)
    for i, line in enumerate(_wrap_text(draw, condition, body_font, 470)[:3]):
        draw.text((x, 330 + i * 42), line, fill=ink, font=body_font)

    draw.text((x, 486), "Environment", fill=accent, font=label_font)
    for i, line in enumerate(_wrap_text(draw, environment, body_font, 470)[:2]):
        draw.text((x, 524 + i * 42), line, fill=ink, font=body_font)

    footer = f"For {audience}. AI-generated classroom/demo preview, not veterinary diagnosis."
    draw.text((58, 672), footer[:118], fill=ink, font=small_font)

    image = image.convert("RGB")
    image.save(path)
    return str(path)


def create_preview_audio(mood: str, duration: int, animal: str, environment: str) -> str:
    OUTPUT_DIR.mkdir(exist_ok=True)
    duration = max(10, min(int(duration or 30), 90))
    slug = _safe_slug(mood, str(duration), animal, environment)
    path = OUTPUT_DIR / f"{slug}-audio.wav"

    notes, note_length, volume = MOOD_AUDIO.get(mood, MOOD_AUDIO["Educational"])
    attack = 0.025
    release = 0.08
    total_samples = duration * SAMPLE_RATE

    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)

        frames = bytearray()
        for sample_index in range(total_samples):
            t = sample_index / SAMPLE_RATE
            note_index = int(t / note_length) % len(notes)
            freq = notes[note_index]
            phase = (t % note_length) / note_length
            env = min(1.0, phase / attack) * min(1.0, (1.0 - phase) / release)
            pad = math.sin(2 * math.pi * (freq / 2) * t) * 0.45
            melody = math.sin(2 * math.pi * freq * t) * 0.55
            pulse = 0.12 * math.sin(2 * math.pi * 2.0 * t) if mood == "Urgent" else 0.0
            fade_out = min(1.0, (duration - t) / 2.0)
            value = (pad + melody + pulse) * env * volume * fade_out
            frames.extend(struct.pack("<h", int(max(-1.0, min(1.0, value)) * 32767)))

        wav.writeframes(frames)

    return str(path)


def _animal_audio_profile(animal: str) -> tuple[str, list[float], float, float]:
    animal_lc = (animal or "").lower()
    for key, profile in ANIMAL_AUDIO.items():
        if key in animal_lc:
            return profile
    return ANIMAL_AUDIO["dog"]


def _real_animal_sound_path(animal: str) -> str | None:
    animal_lc = (animal or "").lower()
    for sound_name, terms in REAL_SOUND_TERMS.items():
        if any(term in animal_lc for term in terms):
            path = SOUND_DIR / f"{sound_name}.ogg"
            if path.exists():
                return str(path)
    return None


def _tone_sample(freq: float, t: float, harmonics: float = 0.35) -> float:
    return math.sin(2 * math.pi * freq * t) + harmonics * math.sin(2 * math.pi * freq * 2.0 * t)


def create_animal_sound(animal: str, condition: str, uploaded_sound: str | None = None) -> str:
    if uploaded_sound and Path(uploaded_sound).exists():
        return uploaded_sound

    real_sound = _real_animal_sound_path(animal)
    if real_sound:
        return real_sound

    OUTPUT_DIR.mkdir(exist_ok=True)
    sound_type, notes, note_length, volume = _animal_audio_profile(animal)
    slug = _safe_slug(animal, condition, sound_type)
    path = OUTPUT_DIR / f"{slug}-animal-sound.wav"
    duration = 4
    total_samples = duration * SAMPLE_RATE
    rng = random.Random(slug)

    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)

        frames = bytearray()
        for sample_index in range(total_samples):
            t = sample_index / SAMPLE_RATE
            event_time = t % 1.25
            note_index = int((t // note_length) % len(notes))
            freq = notes[note_index]

            if sound_type == "bark":
                active = event_time < 0.24 or 0.42 < event_time < 0.58
                env = max(0.0, 1.0 - event_time / 0.22) if event_time < 0.24 else max(0.0, 1.0 - (event_time - 0.42) / 0.16)
                noise = (rng.random() * 2 - 1) * 0.25
                value = (_tone_sample(freq, t, 0.5) * 0.75 + noise) * env * volume if active else 0.0
            elif sound_type == "meow":
                phrase = min(1.0, event_time / 0.75)
                glide = freq + math.sin(phrase * math.pi) * 180 - phrase * 90
                env = math.sin(min(1.0, event_time / 0.95) * math.pi)
                value = _tone_sample(glide, t, 0.18) * env * volume if event_time < 0.95 else 0.0
            elif sound_type == "chirp":
                chirp_time = t % 0.42
                env = max(0.0, 1.0 - chirp_time / 0.09)
                glide = freq + 500 * math.sin(chirp_time * 80)
                value = _tone_sample(glide, t, 0.12) * env * volume if chirp_time < 0.09 else 0.0
            elif sound_type == "moo":
                env = math.sin(min(1.0, event_time / 1.05) * math.pi)
                value = _tone_sample(freq + 18 * math.sin(t * 7), t, 0.42) * env * volume if event_time < 1.05 else 0.0
            else:
                env = math.sin(min(1.0, event_time / 0.85) * math.pi)
                glide = freq + 120 * math.sin(t * 9)
                value = _tone_sample(glide, t, 0.32) * env * volume if event_time < 0.85 else 0.0

            frames.extend(struct.pack("<h", int(max(-1.0, min(1.0, value)) * 32767)))

        wav.writeframes(frames)

    return str(path)
