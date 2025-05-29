#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX"
DEST="${DEST:-assets}"
TMP="$(mktemp -d)"

echo "➡️  Cloning Kokoro repo (metadata only)…"
git lfs install
GIT_LFS_SKIP_SMUDGE=1 \
  git clone --depth 1 --filter=tree:0 "$REPO_URL" "$TMP"

echo "➡️  Pulling q8f16 model + voices (≈92 MB)…"
pushd "$TMP" >/dev/null
git lfs pull --include="onnx/model_q8f16.onnx,voices/*.bin"
popd >/dev/null

echo "➡️  Assembling asset folder $DEST/"
rm -rf "$DEST"
# <-- this will create ./assets and ./assets/voices
mkdir -p "$DEST/voices"

cp "$TMP/onnx/model_q8f16.onnx"    "$DEST/kokoro_q8f16.onnx"
cp "$TMP/voices/"*.bin             "$DEST/voices/"
cp "$TMP"/tokenizer*.json "$TMP"/config.json  "$DEST/"

rm -rf "$TMP"

echo "✅  Assets ready:"
du -h "$DEST"/*
