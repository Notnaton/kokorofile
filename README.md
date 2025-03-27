# Kokorofile

A command-line text-to-speech tool using Kokoro ONNX.

## Installation

### Prerequisites

On Linux, you need to install portaudio development files:
```bash
sudo apt-get install portaudio19-dev
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

## Usage

### Basic Usage

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

### Options

- `-o, --output`: Output file path (if not provided, plays through audio device)
- `-d, --device`: Audio device ID to use for playback
- `-l, --list-devices`: List available audio devices
- `--voice`: Voice to use (default: af_sarah)
- `--speed`: Speech speed (default: 1.0)
- `--lang`: Language code (default: en-us)
- `--debug`: Enable debug logging

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
```

## Notes

- GPU version is sufficient only for Linux and Windows. macOS works with GPU by default.
- You can see the used execution provider by enabling debug log with `--debug` option.
- Model files are automatically downloaded on first run and cached in platform-specific directories.
 
