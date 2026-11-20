"""Read PT-BR text aloud with the locally installed Chatterbox model."""

import argparse
import os
from pathlib import Path
import subprocess
import sys


SAMPLE = (
    "Quem me dera no tempo em que escrevia… sem dar por isso… "
    "cartas de amor. Ridículas."
)


def main():
    # Read a sample or the response that the caller already generated.
    parser = argparse.ArgumentParser(description="Lê um texto com o Chatterbox PT-BR local.")
    parser.add_argument("--sample", action="store_true", help="lê o trecho de Fernando Pessoa")
    args = parser.parse_args()
    text = SAMPLE if args.sample else sys.stdin.read().strip()
    if not text:
        parser.error("envie um texto pela entrada padrão ou use --sample")

    # Run inference using the Python environment prepared by the installer.
    data_home = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share")
    voice_home = Path(os.environ.get("CODEX_VOICE_HOME") or data_home / "codex-voice")
    python = voice_home / "venv/bin/python"
    if not python.is_file():
        parser.error("Chatterbox local não instalado. Execute bash setup-local.sh.")

    worker = Path(__file__).with_name("chatterbox_local.py")
    environment = os.environ.copy()
    environment["HF_HUB_OFFLINE"] = "1"
    environment.setdefault("OMP_NUM_THREADS", "4")
    return subprocess.run(
        [str(python), "-B", str(worker), str(voice_home)],
        input=text,
        text=True,
        env=environment,
    ).returncode


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
