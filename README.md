# Kokorofile

A command-line text-to-speech tool using Kokoro ONNX.

## Installation

### Prerequisites

On Linux, you need to install portaudio and espeak-ng development files:
```bash
sudo apt-get install portaudio19-dev espeak-ng
```

### Using uv (recommended)

```bash
uv tool install git+https://github.com/Notnaton/kokorofile
```

### Manual Installation

```bash
git clone https://github.com/Notnaton/kokorofile.git
cd kokorofile
uv venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
uv pip install -e .
```

### Binary Installation

You can download the pre-built binary from the releases page. The binary requires espeak-ng to be installed on your system:

```bash
# On Ubuntu/Debian
sudo apt-get install espeak-ng

# On Fedora
sudo dnf install espeak-ng

# On Arch Linux
sudo pacman -S espeak-ng
```

## Usage

### Command Line Usage

```bash
# Convert text to speech and play through default audio device
kokorofile "Hello, this is a test"

# Save to file
kokorofile "Hello" -o output.wav

# Read from file
kokorofile input.txt

# Pipe input
echo "Hello" | kokorofile
```

### Server Mode

Run as HTTP server:
```bash
kokorofile --server
```

The server provides a REST API with the following endpoints:

- `POST /synthesize`: Generate speech from text
  ```bash
  curl -X POST "http://localhost:8000/synthesize" \
       -H "Content-Type: application/json" \
       -d '{"text": "Hello", "voice": "af_sarah", "speed": 1.0, "lang": "en-us"}'
  ```

- `GET /voices`: List available voices
  ```bash
  curl http://localhost:8000/voices
  ```

- `GET /devices`: List available audio devices
  ```bash
  curl http://localhost:8000/devices
  ```

Interactive API documentation is available at `http://localhost:8000/docs`

### Options

- `-o, --output`: Output file path (if not provided, plays through audio device)
- `-d, --device`: Audio device ID to use for playback
- `-l, --list-devices`: List available audio devices
- `--cache-dir`: Override default cache directory
- `--data-dir`: Override default data directory
- `--voice`: Voice to use (default: af_sarah)
- `--speed`: Speech speed (default: 1.0)
- `--lang`: Language code (default: en-us)
- `--debug`: Enable debug logging
- `--server`: Run as HTTP server
- `--host`: Server host (default: 127.0.0.1)
- `--port`: Server port (default: 8000)

### Examples

```bash
# Use specific voice and speed
kokorofile "Hello" --voice af_sarah --speed 1.2

# Save to file with specific language
kokorofile "Hello" -o output.wav --lang en-us

# Use specific audio device
kokorofile "Hello" -d 1

# List available audio devices
kokorofile -l

# Run server on custom port
kokorofile --server --port 8080
```

## Notes

- GPU version is sufficient only for Linux and Windows. macOS works with GPU by default.
- You can see the used execution provider by enabling debug log with `--debug` option.
- Model files are automatically downloaded on first run and cached in platform-specific directories.
- The binary version requires espeak-ng to be installed on your system.
 
