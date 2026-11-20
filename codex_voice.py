"""Send a typed request to Codex and read its final reply aloud."""

import argparse
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


def main():
    # Read one request and validate the target project.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, help="pasta do projeto")
    args = parser.parse_args()
    project = args.project.expanduser().resolve()
    if not project.is_dir():
        parser.error(f"pasta do projeto inválida: {project}")

    try:
        request = input("Pedido para o Codex: ").strip()
    except EOFError:
        request = ""
    if not request:
        parser.error("digite um pedido antes de enviar")

    # Save the final reply separately from CLI progress and diagnostics.
    print("Aguardando o Codex...", file=sys.stderr)
    with TemporaryDirectory() as directory:
        reply_file = Path(directory) / "reply.txt"
        try:
            subprocess.run(
                [
                    "codex", "exec", "--sandbox", "workspace-write",
                    "--skip-git-repo-check", "--json",
                    "--output-last-message", str(reply_file),
                    "-",
                ],
                cwd=project,
                input=f"Responda em português do Brasil.\n\n{request}\n",
                text=True,
                stdout=subprocess.DEVNULL,
                check=True,
            )
            reply = reply_file.read_text(encoding="utf-8").strip()
        except (OSError, subprocess.CalledProcessError) as error:
            print(f"Falha ao obter a resposta do Codex: {error}", file=sys.stderr)
            return 1

    # Display the reply even if speech playback fails.
    if not reply:
        print("O Codex retornou uma resposta vazia.", file=sys.stderr)
        return 1
    print(f"\n{reply}", flush=True)
    try:
        subprocess.run(
            [sys.executable, str(Path(__file__).with_name("speak.py"))],
            input=reply,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"Falha ao ler a resposta em voz alta: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
