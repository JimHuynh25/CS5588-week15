from __future__ import annotations

import textwrap
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scenesound.pipeline import generate_studio_plan


OUT = ROOT / "outputs"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_wrapped(draw: ImageDraw.ImageDraw, text: str, xy: tuple[int, int], width: int, line_height: int, fill: str) -> int:
    x, y = xy
    for paragraph in text.split("\n"):
        for line in textwrap.wrap(paragraph, width=width):
            draw.text((x, y), line, fill=fill, font=font(17))
            y += line_height
        y += 6
    return y


def panel(draw: ImageDraw.ImageDraw, title: str, body: str, box: tuple[int, int, int, int], accent: str) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=14, fill="#ffffff", outline="#d7dee8", width=2)
    draw.rectangle((x1, y1, x2, y1 + 8), fill=accent)
    draw.text((x1 + 22, y1 + 22), title, fill=accent, font=font(24, True))
    draw_wrapped(draw, body, (x1 + 22, y1 + 62), 58, 26, "#25324a")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    result = generate_studio_plan(
        animal="golden retriever",
        condition="mild dehydration warning signs",
        environment="a bright veterinary clinic",
        mood="Hopeful",
        duration=45,
        audience="first-time pet owners",
    )

    app = Image.new("RGB", (1366, 900), "#f3f6fb")
    draw = ImageDraw.Draw(app)
    draw.rectangle((0, 0, 1366, 100), fill="#172033")
    draw.text((44, 26), "SceneSound Studio Pro", fill="#ffffff", font=font(36, True))
    draw.text((44, 68), "Multimodal animal-care image + soundtrack generator", fill="#b8c7dd", font=font(17))
    panel(draw, "Inputs", "Animal: golden retriever\nCare scenario: mild dehydration warning signs\nEnvironment: a bright veterinary clinic\nMood: Hopeful\nDuration: 45 seconds\nAudience: first-time pet owners", (54, 150, 650, 500), "#2b7de9")
    panel(draw, "Output Tabs", "Image Prompt\nMusic Prompt\nSFX Cue Sheet\nNarration\nResponsible AI\nEvaluation Metrics", (716, 150, 1312, 500), "#0f9f6e")
    panel(draw, "Final Upgrade", "Week 13 image prompt control + Week 14 soundtrack generation becomes a full Week 15 multimodal production workflow.", (54, 560, 1312, 800), "#7c3aed")
    app.save(OUT / "scenesound_app_screenshot.png")

    results = Image.new("RGB", (1366, 900), "#f3f6fb")
    draw = ImageDraw.Draw(results)
    draw.rectangle((0, 0, 1366, 100), fill="#172033")
    draw.text((44, 26), "SceneSound Studio Pro - generated plan", fill="#ffffff", font=font(34, True))
    draw.text((44, 68), "Result after clicking Generate Multimodal Plan", fill="#b8c7dd", font=font(17))
    panel(draw, "Image Prompt", result.image_prompt, (44, 130, 660, 370), "#2b7de9")
    panel(draw, "Music Prompt", result.music_prompt, (706, 130, 1322, 370), "#0f9f6e")
    panel(draw, "SFX Cue Sheet", "\n".join(f"- {cue}" for cue in result.sfx_cues), (44, 410, 660, 650), "#d97706")
    metrics = (
        f"Prompt alignment: {result.prompt_alignment:.2f}\n"
        f"Realism score: {result.realism_score:.2f}\n"
        f"Diversity score: {result.diversity_score:.2f}\n"
        f"Latency: {result.latency_seconds:.4f} seconds"
    )
    panel(draw, "Narration + Metrics", result.narration_script + "\n\n" + metrics, (706, 410, 1322, 650), "#7c3aed")
    panel(draw, "Responsible AI Review", "\n".join(f"- {item}" for item in result.safety_review), (44, 690, 1322, 858), "#d14368")
    results.save(OUT / "scenesound_results_screenshot.png")
    print("Saved outputs/scenesound_app_screenshot.png")
    print("Saved outputs/scenesound_results_screenshot.png")


if __name__ == "__main__":
    main()
