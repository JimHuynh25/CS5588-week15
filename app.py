from __future__ import annotations

import gradio as gr

from scenesound.media import create_animal_sound, create_preview_audio, create_preview_image
from scenesound.pipeline import generate_studio_plan


def create_plan(
    animal: str,
    condition: str,
    environment: str,
    mood: str,
    duration: int,
    audience: str,
    uploaded_photo: str | None,
    uploaded_sound: str | None,
) -> tuple[str, str, str, str, str, str, str, str, str]:
    output = generate_studio_plan(animal, condition, environment, mood, duration, audience)
    image_path = create_preview_image(animal, condition, environment, mood, audience, uploaded_photo)
    audio_path = create_preview_audio(mood, duration, animal, environment)
    animal_sound_path = create_animal_sound(animal, condition, uploaded_sound)
    sfx = "\n".join(f"- {cue}" for cue in output.sfx_cues)
    safety = "\n".join(f"- {item}" for item in output.safety_review)
    metrics = (
        f"Prompt alignment: {output.prompt_alignment:.2f}\n"
        f"Realism score: {output.realism_score:.2f}\n"
        f"Diversity score: {output.diversity_score:.2f}\n"
        f"Latency: {output.latency_seconds:.4f} seconds"
    )
    return image_path, audio_path, animal_sound_path, output.image_prompt, output.music_prompt, sfx, output.narration_script, safety, metrics


with gr.Blocks(title="SceneSound Studio Pro") as demo:
    gr.Markdown("# SceneSound Studio Pro")
    gr.Markdown(
        "Week 15 final multimodal studio: structured animal-care image prompts, soundtracks, SFX cues, narration, safety review, and evaluation."
    )

    with gr.Row():
        with gr.Column():
            animal = gr.Textbox(label="Animal / subject", value="golden retriever")
            condition = gr.Textbox(label="Care scenario", value="mild dehydration warning signs")
            environment = gr.Textbox(label="Environment", value="a bright veterinary clinic")
        with gr.Column():
            mood = gr.Dropdown(label="Soundtrack mood", choices=["Calm", "Hopeful", "Urgent", "Educational"], value="Hopeful")
            duration = gr.Slider(label="Audio duration in seconds", minimum=10, maximum=90, step=5, value=45)
            audience = gr.Textbox(label="Target audience", value="first-time pet owners")
            uploaded_photo = gr.Image(label="Photo upload optional", type="filepath")
            uploaded_sound = gr.Audio(label="Animal sound upload optional", type="filepath")

    run = gr.Button("Generate Multimodal Plan", variant="primary")

    with gr.Tab("Preview Image"):
        preview_image = gr.Image(label="Generated educational image preview", type="filepath")
    with gr.Tab("Preview Audio"):
        preview_audio = gr.Audio(label="Generated soundtrack preview", type="filepath")
    with gr.Tab("Animal Sound"):
        animal_sound = gr.Audio(label="Generated animal sound effect", type="filepath")
    with gr.Tab("Image Prompt"):
        image_prompt = gr.Textbox(label="Week 13 image-generation prompt", lines=6)
    with gr.Tab("Music Prompt"):
        music_prompt = gr.Textbox(label="Week 14/15 soundtrack prompt", lines=6)
    with gr.Tab("SFX Cue Sheet"):
        sfx_cues = gr.Markdown()
    with gr.Tab("Narration"):
        narration = gr.Textbox(label="Voice-ready narration script", lines=5)
    with gr.Tab("Responsible AI"):
        safety = gr.Markdown()
    with gr.Tab("Evaluation Metrics"):
        metrics = gr.Textbox(label="Final evaluation snapshot", lines=5)

    run.click(
        create_plan,
        inputs=[animal, condition, environment, mood, duration, audience, uploaded_photo, uploaded_sound],
        outputs=[preview_image, preview_audio, animal_sound, image_prompt, music_prompt, sfx_cues, narration, safety, metrics],
    )


if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)
