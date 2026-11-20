"""Read PT-BR text aloud with the locally installed Chatterbox model."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import struct
import subprocess
import sys


SAMPLE = (
    "Quem me dera no tempo em que escrevia… sem dar por isso… "
    "cartas de amor. Ridículas."
)


def reader_address(voice_home):
    # Use a Linux abstract socket so a stopped reader leaves no stale file.
    installation = hashlib.sha256(os.fsencode(voice_home)).hexdigest()[:24]
    return f"\0codex-voice-{os.getuid()}-{installation}"


def same_user(connection):
    credentials = connection.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12)
    _, uid, _ = struct.unpack("3i", credentials)
    return uid == os.getuid()


def request_reader(voice_home, text):
    # Return None only when there is no running reader.
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        try:
            connection.connect(reader_address(voice_home))
        except ConnectionRefusedError:
            return None
        if not same_user(connection):
            raise RuntimeError("O leitor local pertence a outro usuário.")
        connection.sendall(json.dumps(text).encode() + b"\n")
        with connection.makefile("rb") as stream:
            reply = stream.readline()
        if not reply:
            raise RuntimeError("O leitor local encerrou sem responder.")
        return json.loads(reply)


def main():
    # Read a sample, existing text, or a command for the persistent reader.
    parser = argparse.ArgumentParser(description="Lê um texto com o Chatterbox PT-BR local.")
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--text", help="lê a frase informada")
    actions.add_argument("--sample", action="store_true", help="lê o trecho de Fernando Pessoa")
    actions.add_argument("--serve", action="store_true", help="mantém o modelo carregado na GPU")
    actions.add_argument("--stop", action="store_true", help="encerra o leitor local")
    args = parser.parse_args()

    data_home = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share")
    voice_home = Path(os.environ.get("CODEX_VOICE_HOME") or data_home / "codex-voice").resolve()
    text = None
    if not args.serve and not args.stop:
        if args.sample:
            text = SAMPLE
        else:
            text = (args.text if args.text is not None else sys.stdin.read()).strip()
        if not text:
            parser.error("envie um texto pela entrada padrão ou use --text ou --sample")

    # Reuse the resident model when available. Keep one-shot playback available.
    if not args.serve:
        reply = request_reader(voice_home, text)
        if reply is not None:
            if reply["message"]:
                print(reply["message"], file=sys.stderr)
            return reply["status"]
        if args.stop:
            print("O leitor local já está parado.")
            return 0

    python = voice_home / "venv/bin/python"
    if not python.is_file():
        parser.error("Chatterbox local não instalado. Execute bash setup-local.sh.")

    worker = Path(__file__).with_name("chatterbox_local.py")
    environment = os.environ.copy()
    environment["HF_HUB_OFFLINE"] = "1"
    environment.setdefault("OMP_NUM_THREADS", "4")
    command = [str(python), "-B", str(worker), str(voice_home)]
    if args.serve:
        # Replace the launcher so Ctrl+C and service tools target the GPU process.
        os.execve(python, command + ["--serve"], environment)
    return subprocess.run(command, input=text, text=True, env=environment).returncode


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError) as error:
        sys.exit(f"Falha ao acessar o leitor local: {error}")
    except KeyboardInterrupt:
        sys.exit(130)
