"""Read a short PT-BR text with the public Chatterbox demo."""

import argparse
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from urllib.request import Request, urlopen


DEMO = "https://resembleai-chatterbox-multilingual-tts-pt-br.hf.space"
ENDPOINT = DEMO + "/gradio_api/call/generate_tts_audio"
SAMPLE = (
    "Quem me dera no tempo em que escrevia… sem dar por isso… "
    "cartas de amor. Ridículas."
)


def generate_audio(text, audio_path):
    # Get the demo's current default voice reference and submit the approved preset.
    with urlopen(DEMO + "/gradio_api/info", timeout=20) as response:
        parameters = json.load(response)["named_endpoints"]["/generate_tts_audio"]["parameters"]
    voice = parameters[1]["parameter_default"]
    preset = [text, voice, 0.35, 0.7, 31, 0.32]
    request = Request(
        ENDPOINT,
        data=json.dumps({"data": preset}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urlopen(request, timeout=30) as response:
        event_id = json.load(response)["event_id"]

    # Wait for the completed audio and download it from the demo.
    event = ""
    with urlopen(f"{ENDPOINT}/{event_id}", timeout=90) as response:
        for raw_line in response:
            line = raw_line.decode().strip()
            if line.startswith("event:"):
                event = line.removeprefix("event:").strip()
            if event == "error":
                raise RuntimeError("A demo não conseguiu gerar o áudio.")
            if event == "complete" and line.startswith("data:"):
                url = json.loads(line.removeprefix("data:"))[0]["url"]
                if not url.startswith(DEMO + "/"):
                    raise RuntimeError("A demo retornou um endereço de áudio inesperado.")
                with urlopen(url, timeout=25) as audio:
                    audio_path.write_bytes(audio.read())
                return
    raise RuntimeError("A demo terminou sem retornar áudio.")


def main():
    # Accept the built-in sample or a short text explicitly sent via stdin.
    parser = argparse.ArgumentParser(
        description="Envia um trecho à demo pública do Chatterbox e toca o áudio."
    )
    parser.add_argument("--sample", action="store_true", help="lê o trecho de Fernando Pessoa")
    args = parser.parse_args()
    text = SAMPLE if args.sample else sys.stdin.read().strip()
    if not 1 <= len(text) <= 300:
        parser.error("envie de 1 a 300 caracteres pela entrada padrão ou use --sample")

    # Play the result and remove the temporary audio file afterward.
    try:
        with TemporaryDirectory() as directory:
            audio_path = Path(directory) / "reply.wav"
            generate_audio(text, audio_path)
            subprocess.run(["gst-play-1.0", "--quiet", str(audio_path)], check=True)
    except (OSError, RuntimeError, subprocess.CalledProcessError, ValueError, KeyError, TypeError, IndexError) as error:
        print(f"Falha ao falar com o Chatterbox: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
