from __future__ import annotations

import gradio as gr

from scenesound.pipeline import generate_studio_plan


def create_plan(
    animal: str,
    condition: str,
    environment: str,
    mood: str,
    duration: int,
    audience: str,
) -> tuple[str, str, str, str, str, str]:
    output = generate_studio_plan(animal, condition, environment, mood, duration, audience)
    sfx = "\n".join(f"- {cue}" for cue in output.sfx_cues)
    safety = "\n".join(f"- {item}" for item in output.safety_review)
    metrics = (
        f"Prompt alignment: {output.prompt_alignment:.2f}\n"
        f"Realism score: {output.realism_score:.2f}\n"
        f"Diversity score: {output.diversity_score:.2f}\n"
        f"Latency: {output.latency_seconds:.4f} seconds"
    )
    return output.image_prompt, output.music_prompt, sfx, output.narration_script, safety, metrics


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

    run = gr.Button("Generate Multimodal Plan", variant="primary")

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
        inputs=[animal, condition, environment, mood, duration, audience],
        outputs=[image_prompt, music_prompt, sfx_cues, narration, safety, metrics],
    )


if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)
