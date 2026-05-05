from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scenesound.evaluation import evaluate_pipeline


def main() -> None:
    results = evaluate_pipeline()

    output_dir = ROOT / "outputs"
    output_dir.mkdir(exist_ok=True)
    pd.DataFrame([results]).to_csv(output_dir / "evaluation_results.csv", index=False)
    print("Saved outputs/evaluation_results.csv")
    for key, value in results.items():
        if key != "raw_output":
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()
