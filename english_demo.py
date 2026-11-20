"""Try Chatterbox Multilingual V3 with an English voice reference.

Run with the Python environment created by setup-local.sh. Use the
ResembleAI/Chatterbox-Multilingual-TTS-V3 Space at revision
b21d9d062b4eda102f21975333276919935d2060 for --source.

For --weights, use ve.pt, s3gen.pt, t3_mtl23ls_v3.safetensors and
grapheme_mtl_merged_expanded_v1.json from ResembleAI/chatterbox at revision
5bb1f6ee58e50c3b8d408bc82a6d3740c2db6e18. The English reference used in the
test is https://storage.googleapis.com/chatterbox-demo-samples/mtl_prompts/en_f1.flac.
"""

import argparse
from pathlib import Path
import subprocess
import sys
from time import perf_counter


SAMPLES = [
    "Your changes are ready.",
    "I checked the tests and found one thing worth reviewing.",
    "Take your time. We can look at the next step together.",
]


def main():
    # Use separate model assets and reuse the project's local player.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="Multilingual V3 Space checkout")
    parser.add_argument("--weights", type=Path, required=True, help="Multilingual V3 weights directory")
    parser.add_argument("--reference", type=Path, required=True, help="English speech reference")
    parser.add_argument("--output", type=Path, required=True, help="Path for the generated WAV")
    parser.add_argument("--text", action="append", help="English phrase, repeatable")
    args = parser.parse_args()

    import numpy as np
    import soundfile
    import torch

    if not torch.cuda.is_available():
        parser.error("CUDA is required for this experiment.")
    sys.path.insert(0, str(args.source / "chatterbox/src"))
    from chatterbox.tts import ChatterboxTTS

    # Load one model and prepare the English voice for all phrases.
    torch.manual_seed(31)
    started = perf_counter()
    with torch.inference_mode():
        voice = ChatterboxTTS.from_local(args.weights, "cuda")
        voice.prepare_conditionals(str(args.reference), exaggeration=0.35)
        print(f"Voice ready in {perf_counter() - started:.1f} s.", flush=True)

        clips = []
        for phrase in args.text or SAMPLES:
            started = perf_counter()
            audio = voice.generate(
                phrase, language_id="en", exaggeration=0.35, temperature=0.7, cfg_weight=0.32
            )
            clips.append(audio.squeeze().cpu().numpy())
            print(f"Generated in {perf_counter() - started:.1f} s. {phrase}", flush=True)

    # Save a single comparison sample and play it at the project's usual rate.
    silence = np.zeros(voice.sr // 3, dtype=clips[0].dtype)
    separated = [part for clip in clips for part in (clip, silence)]
    soundfile.write(args.output, np.concatenate(separated[:-1]), voice.sr)
    print(f"Peak VRAM allocated: {torch.cuda.max_memory_allocated() / 1024**3:.2f} GiB.", flush=True)
    player = Path(__file__).with_name("play_audio.py")
    subprocess.run(["/usr/bin/python3", str(player), str(args.output)], check=True)


if __name__ == "__main__":
    main()
