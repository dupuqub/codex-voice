#!/usr/bin/env bash
set -euo pipefail

voice_home="${CODEX_VOICE_HOME:-${XDG_DATA_HOME:-$HOME/.local/share}/codex-voice}"
demo_revision=9e515821e826e207cd617a0fdd0223899ed108ea
demo_url=https://huggingface.co/spaces/ResembleAI/Chatterbox-Multilingual-TTS-pt-br
model_url=https://huggingface.co/ResembleAI/Chatterbox-Multilingual-pt-br/resolve/b3952f18bc2eaa72b9bd7c17d2c4653bcad4770d
base_url=https://huggingface.co/ResembleAI/chatterbox/resolve/5bb1f6ee58e50c3b8d408bc82a6d3740c2db6e18
reference_url=https://storage.googleapis.com/chatterbox-demo-samples/mtl-v3-single-language-prompts/pt-br/pt_br_f2.wav

# Set up the pinned inference code and Linux CUDA environment.
mkdir -p "$voice_home/weights"
export UV_CACHE_DIR="${UV_CACHE_DIR:-$voice_home/uv-cache}"
export UV_PYTHON_INSTALL_DIR="$voice_home/python"
if [[ ! -d "$voice_home/demo/.git" ]]; then
    git init --quiet "$voice_home/demo"
fi
if [[ "$(git -C "$voice_home/demo" rev-parse --verify HEAD 2>/dev/null || true)" != "$demo_revision" ]]; then
    git -C "$voice_home/demo" fetch --depth 1 "$demo_url" "$demo_revision"
    git -C "$voice_home/demo" checkout --detach FETCH_HEAD
fi
if [[ ! -x "$voice_home/venv/bin/python" ]]; then
    uv venv --python 3.11.18 "$voice_home/venv"
fi
uv pip install --python "$voice_home/venv/bin/python" \
    --index https://download.pytorch.org/whl/cu128 torch==2.8.0 torchaudio==2.8.0
uv pip install --python "$voice_home/venv/bin/python" \
    numpy==1.26.0 resampy==0.4.3 librosa==0.10.0 s3tokenizer==0.3.0 \
    transformers==4.46.3 diffusers==0.29.0 omegaconf==2.3.0 \
    resemble-perth==1.0.1 silero-vad==5.1.2 conformer==0.3.2 \
    safetensors==0.8.0 soundfile==0.14.0 huggingface-hub==0.36.2

# Verify the exact assets used for the approved voice before making them available.
fetch_asset() {
    local url="$1" target="$2" hash="$3"
    if [[ -f "$target" ]] && printf '%s  %s\n' "$hash" "$target" | sha256sum --check --status; then
        return
    fi
    local partial
    partial="$(mktemp "${target}.XXXXXX")"
    if curl --fail --location --retry 2 --silent --show-error "$url" -o "$partial" &&
        printf '%s  %s\n' "$hash" "$partial" | sha256sum --check --status; then
        mv "$partial" "$target"
    else
        rm -f "$partial"
        printf 'Falha ao baixar ou verificar %s\n' "$target" >&2
        return 1
    fi
}

fetch_asset "$model_url/t3_pt_br.safetensors" "$voice_home/weights/t3_pt_br.safetensors" \
    074aaf65255eb9cb960288f7cc72e09d3b5008f6e0b14868c0d4e5b0bd7cbb6c
fetch_asset "$model_url/s3gen_v3.pt" "$voice_home/weights/s3gen_v3.pt" \
    f7abce4b196dae2d08d9296cbebc6521b046079577643b42a19a03499d08721e
fetch_asset "$base_url/ve.pt" "$voice_home/weights/ve.pt" \
    4b16d836bc598509860f6fa068165a8bb5e9ac84f05582dfcf278a5a372879f1
fetch_asset "$base_url/grapheme_mtl_merged_expanded_v1.json" \
    "$voice_home/weights/grapheme_mtl_merged_expanded_v1.json" \
    69632f47220a788a52ce2661d096453c5655e9bf25289d89a8d832c46ee07dbf
fetch_asset "$reference_url" "$voice_home/reference.wav" \
    b74124fa87356241316d2d55b8f9dfea1da57f08325f63e9198e33f755659482
printf 'Chatterbox instalado em %s\n' "$voice_home"
