"""Synthesize and play speech in the Chatterbox Python environment."""

from pathlib import Path
import random
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
from textwrap import wrap
from time import perf_counter

import numpy as np
import soundfile
import torch


def main():
    # Validate local playback and load the approved checkpoint on the GPU.
    voice_home = Path(sys.argv[1])
    text = sys.stdin.read()
    player = shutil.which("gst-play-1.0")
    if not player:
        raise RuntimeError("Instale o gst-play-1.0 para reproduzir o áudio.")
    if not torch.cuda.is_available():
        raise RuntimeError("O Chatterbox local precisa de uma GPU NVIDIA com CUDA disponível.")

    sys.path.insert(0, str(voice_home / "demo/chatterbox/src"))
    from chatterbox.tts import ChatterboxTTS

    print("Carregando o Chatterbox local...", file=sys.stderr, flush=True)
    started = perf_counter()
    model = ChatterboxTTS.from_local(voice_home / "weights", "cuda")
    print(f"Modelo carregado em {perf_counter() - started:.1f} s.", file=sys.stderr)

    # Reuse the model for each short segment and play audio as segments finish.
    random.seed(31)
    np.random.seed(31)
    torch.manual_seed(31)
    with TemporaryDirectory() as directory, torch.inference_mode():
        audio_path = Path(directory) / "resposta.wav"
        # Keep short inputs verbatim to preserve their pacing and punctuation.
        segments = [text] if len(text) <= 200 else wrap(text, width=200)
        for segment in segments:
            started = perf_counter()
            audio = model.generate(
                segment,
                language_id="pt",
                audio_prompt_path=str(voice_home / "reference.wav"),
                exaggeration=0.35,
                temperature=0.7,
                cfg_weight=0.32,
            )
            soundfile.write(audio_path, audio.squeeze().cpu().numpy(), model.sr)
            print(f"Síntese em {perf_counter() - started:.1f} s.", file=sys.stderr)
            subprocess.run([player, "--quiet", str(audio_path)], check=True)


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        sys.exit(f"Falha ao falar com o Chatterbox local: {error}")
    except KeyboardInterrupt:
        sys.exit(130)
