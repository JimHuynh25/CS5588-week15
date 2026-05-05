# CS 5588 Week 15 Final Hands-On Challenge

## Project: SceneSound Studio Pro

SceneSound Studio Pro is a polished Week 15 multimodal AI system that continues the real Week 13 and Week 14 project direction.

- **Week 13:** AI Animal Care & Pet Health Visualization System using structured Stable Diffusion-style image prompts.
- **Week 14:** SceneSound Studio, a working prototype for text-to-music and sound-effects generation.
- **Week 15:** SceneSound Studio Pro, a final multimodal production workflow that combines animal-care image prompts, soundtrack prompts, sound-effect cue sheets, narration scripts, responsible-AI review, evaluation metrics, and a Gradio product demo.

## Why This Is Better Than Week 14

Week 14 focused on audio prompt generation. Week 15 adds:

1. Better prompt engineering for image, music, SFX, and narration outputs.
2. An advanced multimodal pipeline: scenario -> image prompt -> soundtrack prompt -> SFX cues -> narration -> safety review.
3. A Gradio product demo with clear controls for animal, condition, environment, mood, duration, and audience.
4. Real evaluation metrics: prompt alignment, multimodal quality, realism, diversity, latency, safety flags, and cue coverage.
5. Stronger business framing for veterinary educators, shelters, pet-care creators, instructors, and small marketing teams.
6. Responsible-AI safeguards for graphic medical content, copyright, misleading health claims, and voice-cloning misuse.
7. Cleaner engineering with a reusable pipeline, evaluation script, generated screenshots, final report, and presentation deck.

## Repository Structure

```text
.
├── app.py                          # Gradio demo app
├── scenesound/
│   ├── pipeline.py                 # Core multimodal planning pipeline
│   └── evaluation.py               # Final evaluation metrics
├── outputs/
│   ├── evaluation_results.csv
│   ├── scenesound_app_screenshot.png
│   ├── scenesound_results_screenshot.png
│   ├── week15_final_report.pdf
│   └── week15_scenesound_studio_pro.pptx
├── scripts/
│   ├── run_evaluation.py
│   ├── make_result_screenshot.py
│   └── generate_artifacts.py
├── VIDEO_SCRIPT.md
├── requirements.txt
└── README.md
```

## Setup

```powershell
python -m pip install -r requirements.txt
python scripts/run_evaluation.py
python scripts/make_result_screenshot.py
python scripts/generate_artifacts.py
python app.py
```

Then open the local Gradio URL printed in the terminal.

## Model Upgrade Path

The current repo runs offline for reliable presentation. A production version would connect:

- image prompts to Stable Diffusion XL or ControlNet
- music prompts to MusicGen or AudioLDM
- narration scripts to a text-to-speech model
- evaluation to human ratings plus model-based prompt alignment checks

## Final Deliverables

- PowerPoint: `outputs/week15_scenesound_studio_pro.pptx`
- Final report PDF: `outputs/week15_final_report.pdf`
- Demo video script: `VIDEO_SCRIPT.md`
- Evaluation results: `outputs/evaluation_results.csv`
- Screenshots: `outputs/scenesound_app_screenshot.png` and `outputs/scenesound_results_screenshot.png`

## Final Presentation Answer

SceneSound Studio Pro is significantly better than Week 14 because it turns an audio prompt prototype into a full multimodal AI production workflow. It directly connects Week 13 image generation and Week 14 sound generation, then adds stronger engineering, deeper evaluation, better outputs, improved UX, business value, and responsible-AI safeguards.
