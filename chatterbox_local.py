"""Synthesize and play speech in the Chatterbox Python environment."""

import errno
import json
from pathlib import Path
import random
import re
import socket
import subprocess
import sys
from tempfile import TemporaryDirectory
from textwrap import wrap
from time import perf_counter

from speak import reader_address, same_user


VOICE_EXAGGERATION = 0.35
SEGMENT_LIMIT = 200


def speech_segments(text):
    # Prefer sentence boundaries and cap long sentences for the synthesizer.
    for sentence in re.split(r"(?<=[.!?…])\s+", text):
        if len(sentence) <= SEGMENT_LIMIT:
            if sentence.strip():
                yield sentence
        else:
            yield from wrap(sentence, width=SEGMENT_LIMIT, break_on_hyphens=False)


class Voice:
    def __init__(self, voice_home):
        # Load the approved checkpoint and prepare the voice reference once.
        import torch

        if not torch.cuda.is_available():
            raise RuntimeError("O Chatterbox local precisa de uma GPU NVIDIA com CUDA disponível.")

        sys.path.insert(0, str(voice_home / "demo/chatterbox/src"))
        from chatterbox.tts import ChatterboxTTS

        print("Carregando o Chatterbox local...", file=sys.stderr, flush=True)
        started = perf_counter()
        self.model = ChatterboxTTS.from_local(voice_home / "weights", "cuda")
        with torch.inference_mode():
            self.model.prepare_conditionals(
                str(voice_home / "reference.wav"), exaggeration=VOICE_EXAGGERATION
            )
        print(f"Voz pronta em {perf_counter() - started:.1f} s.", file=sys.stderr, flush=True)

    def speak(self, text):
        import numpy as np
        import soundfile
        import torch

        # Seed once so the sequence of segments is reproducible.
        random.seed(31)
        np.random.seed(31)
        torch.manual_seed(31)
        player = Path(__file__).with_name("play_audio.py")
        with TemporaryDirectory() as directory, torch.inference_mode():
            playback = None
            try:
                for index, segment in enumerate(speech_segments(text)):
                    audio_path = Path(directory) / f"resposta-{index % 2}.wav"
                    started = perf_counter()
                    audio = self.model.generate(
                        segment,
                        language_id="pt",
                        exaggeration=VOICE_EXAGGERATION,
                        temperature=0.7,
                        cfg_weight=0.32,
                    )
                    soundfile.write(audio_path, audio.squeeze().cpu().numpy(), self.model.sr)
                    print(f"Áudio pronto em {perf_counter() - started:.1f} s.", file=sys.stderr, flush=True)
                    # Generate one segment ahead and keep playback in order.
                    if playback is not None and playback.wait():
                        raise subprocess.CalledProcessError(playback.returncode, playback.args)
                    playback = subprocess.Popen(["/usr/bin/python3", str(player), str(audio_path)])
                if playback is not None and playback.wait():
                    raise subprocess.CalledProcessError(playback.returncode, playback.args)
            finally:
                if playback is not None and playback.poll() is None:
                    playback.kill()
                    playback.wait()


def serve(voice_home):
    # Bind before loading to prevent duplicate readers while the model starts.
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as listener:
        try:
            listener.bind(reader_address(voice_home))
        except OSError as error:
            if error.errno == errno.EADDRINUSE:
                raise RuntimeError("Já existe um leitor local neste ambiente.") from error
            raise
        listener.listen()
        voice = Voice(voice_home)

        # Accept requests from this user only and play them in sequence.
        while True:
            connection, _ = listener.accept()
            with connection:
                if not same_user(connection):
                    continue
                connection.settimeout(5)
                stop = False
                try:
                    with connection.makefile("rb") as stream:
                        text = json.loads(stream.readline())
                    stop = text is None
                    if not stop:
                        if not isinstance(text, str) or not text.strip():
                            raise ValueError("Envie um texto para leitura.")
                        voice.speak(text)
                    reply = {"status": 0, "message": "Leitor local encerrado." if stop else ""}
                except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
                    reply = {"status": 1, "message": f"Falha ao ler: {error}"}
                try:
                    connection.sendall(json.dumps(reply).encode() + b"\n")
                except OSError:
                    pass
                if stop:
                    return


def main():
    voice_home = Path(sys.argv[1])
    if "--serve" in sys.argv[2:]:
        serve(voice_home)
    else:
        Voice(voice_home).speak(sys.stdin.read())


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        sys.exit(f"Falha ao falar com o Chatterbox local: {error}")
    except KeyboardInterrupt:
        sys.exit(130)
