from __future__ import annotations

from .pipeline import generate_studio_plan


def evaluate_pipeline() -> dict[str, float | int | str]:
    output = generate_studio_plan(
        animal="golden retriever",
        condition="mild dehydration warning signs",
        environment="a bright veterinary clinic",
        mood="Hopeful",
        duration=45,
        audience="first-time pet owners",
    )

    week14_baseline_alignment = 0.58
    week15_alignment = output.prompt_alignment
    week14_audio_only_score = 0.62
    week15_multimodal_score = round((output.prompt_alignment + output.realism_score + output.diversity_score) / 3, 2)

    return {
        "week14_prompt_alignment": week14_baseline_alignment,
        "week15_prompt_alignment": week15_alignment,
        "week14_audio_only_quality": week14_audio_only_score,
        "week15_multimodal_quality": week15_multimodal_score,
        "realism_score": output.realism_score,
        "diversity_score": output.diversity_score,
        "latency_seconds": round(output.latency_seconds, 4),
        "safety_flags_found": len(output.safety_review),
        "sfx_cues_found": len(output.sfx_cues),
        "image_prompt": output.image_prompt,
        "music_prompt": output.music_prompt,
        "narration_script": output.narration_script,
        "raw_output": str(output.__dict__),
    }
