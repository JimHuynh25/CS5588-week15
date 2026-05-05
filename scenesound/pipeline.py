from __future__ import annotations

import re
import time
from dataclasses import dataclass


MOOD_SETTINGS = {
    "Calm": {
        "tempo": "72 BPM",
        "instruments": "soft piano, warm pads, light acoustic textures",
        "mix": "gentle dynamics with low-frequency rumble removed",
    },
    "Hopeful": {
        "tempo": "92 BPM",
        "instruments": "bright marimba, clean guitar, soft strings",
        "mix": "clear midrange with a light uplifting build",
    },
    "Urgent": {
        "tempo": "118 BPM",
        "instruments": "subtle pulse, short strings, restrained percussion",
        "mix": "focused energy without alarming or sensational sound design",
    },
    "Educational": {
        "tempo": "84 BPM",
        "instruments": "light piano, neutral synth bed, simple bell accents",
        "mix": "speech-friendly arrangement with minimal masking",
    },
}

SAFETY_TERMS = {
    "injury": "Avoid graphic injury depiction; present the condition as educational and non-sensational.",
    "surgery": "Avoid surgical gore; use clinical, respectful educational framing.",
    "abuse": "Avoid exploitative imagery; focus on care, recovery, and responsible reporting.",
    "blood": "Avoid graphic blood; use symbolic or non-graphic visual explanation.",
    "copyright": "Use original generated music and avoid copying existing artists or tracks.",
    "voice clone": "Do not clone a real person's voice without explicit permission.",
}


@dataclass
class StudioOutput:
    image_prompt: str
    music_prompt: str
    sfx_cues: list[str]
    narration_script: str
    safety_review: list[str]
    prompt_alignment: float
    realism_score: float
    diversity_score: float
    latency_seconds: float


def normalize_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text.strip())
    return text.rstrip(".")


def build_image_prompt(animal: str, condition: str, environment: str, audience: str) -> str:
    return (
        f"Educational veterinary care scene of a {animal} showing {condition} in {environment}. "
        f"Designed for {audience}, realistic but gentle, clean lighting, clear subject focus, "
        "non-graphic medical education, high detail, professional animal welfare visual."
    )


def build_music_prompt(mood: str, duration: int, environment: str) -> str:
    setting = MOOD_SETTINGS[mood]
    return (
        f"{duration}-second {mood.lower()} background music bed for an animal care explainer in {environment}. "
        f"Use {setting['instruments']}, around {setting['tempo']}. The mix should be {setting['mix']}."
    )


def build_sfx_cues(animal: str, environment: str, mood: str) -> list[str]:
    base = [
        f"0-4s: soft room tone from {environment}",
        f"4-12s: gentle {animal} movement or breathing layer",
        "12-22s: subtle transition cue when the care recommendation appears",
        "22-end: clean fade under narration with no harsh alarms",
    ]
    if mood == "Urgent":
        base[2] = "12-22s: restrained pulse cue to show urgency without fear-based sound design"
    return base


def build_narration(animal: str, condition: str, environment: str, audience: str) -> str:
    return (
        f"This scene explains how to recognize {condition} in a {animal} within {environment}. "
        f"For {audience}, the key message is to observe symptoms calmly, document changes, "
        "and contact a qualified veterinarian when warning signs appear."
    )


def review_safety(*parts: str) -> list[str]:
    text = " ".join(parts).lower()
    risks = [message for term, message in SAFETY_TERMS.items() if term in text]
    risks.append("Label outputs as AI-generated educational media, not veterinary diagnosis.")
    return risks


def score_prompt_alignment(image_prompt: str, music_prompt: str, animal: str, condition: str, mood: str) -> float:
    combined = f"{image_prompt} {music_prompt}".lower()
    required = [animal.lower(), condition.lower(), mood.lower(), "educational", "care"]
    hits = sum(1 for term in required if term in combined)
    return round(hits / len(required), 2)


def score_realism(condition: str, environment: str, audience: str) -> float:
    score = 0.65
    if condition:
        score += 0.1
    if environment:
        score += 0.1
    if audience:
        score += 0.1
    return round(min(score, 0.95), 2)


def score_diversity(mood: str, duration: int, environment: str) -> float:
    setting_terms = len(set(MOOD_SETTINGS[mood]["instruments"].split(", ")))
    duration_bonus = 0.08 if duration >= 30 else 0.03
    environment_bonus = 0.08 if environment else 0
    return round(min(0.55 + setting_terms * 0.05 + duration_bonus + environment_bonus, 0.92), 2)


def generate_studio_plan(
    animal: str,
    condition: str,
    environment: str,
    mood: str,
    duration: int,
    audience: str,
) -> StudioOutput:
    start = time.perf_counter()
    animal = normalize_text(animal or "dog")
    condition = normalize_text(condition or "mild dehydration warning signs")
    environment = normalize_text(environment or "a modern veterinary clinic")
    audience = normalize_text(audience or "pet owners")
    mood = mood if mood in MOOD_SETTINGS else "Educational"
    duration = max(10, min(int(duration or 30), 90))

    image_prompt = build_image_prompt(animal, condition, environment, audience)
    music_prompt = build_music_prompt(mood, duration, environment)
    sfx_cues = build_sfx_cues(animal, environment, mood)
    narration_script = build_narration(animal, condition, environment, audience)
    safety_review = review_safety(condition, image_prompt, music_prompt, narration_script)
    latency = time.perf_counter() - start

    return StudioOutput(
        image_prompt=image_prompt,
        music_prompt=music_prompt,
        sfx_cues=sfx_cues,
        narration_script=narration_script,
        safety_review=safety_review,
        prompt_alignment=score_prompt_alignment(image_prompt, music_prompt, animal, condition, mood),
        realism_score=score_realism(condition, environment, audience),
        diversity_score=score_diversity(mood, duration, environment),
        latency_seconds=latency,
    )
