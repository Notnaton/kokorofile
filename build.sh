rm -rf build/ dist/ kokorofile.spec

uv run pyinstaller --onefile \
  --name kokorofile \
  --add-data "models:models" \
  --add-data "models/voices:voices" \
  --collect-all kokoro \
  --upx-dir=upx \
  server.py
