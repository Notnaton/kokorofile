# Kokoro TTS Inference Server

A Rust-based text-to-speech inference server using the quantized Kokoro TTS model with embedded assets.

## Features

- 🚀 Fast inference with quantized ONNX model (q8f16)
- 📦 Self-contained executable with embedded model and voices
- 🌐 RESTful web API
- 🎵 Multiple voice support
- ⚡ Configurable speech speed
- 🔊 WAV audio output

## Setup

### 1. Prepare Assets

First, run the asset preparation script to download the model and voices:

```bash
chmod +x prepare_assets.sh
./prepare_assets.sh
```

This will create an `assets/` directory with:
- `kokoro_q8f16.onnx` - The quantized TTS model
- `voices/*.bin` - Voice embedding files
- `config.json` - Model configuration
- `tokenizer.json` - Tokenizer configuration

### 2. Build the Server

```bash
cargo build --release
```

### 3. Run the Server

```bash
cargo run --release
```

The server will start on `http://0.0.0.0:8080`

## API Endpoints

### Health Check
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Kokoro TTS"
}
```

### List Available Voices
```
GET /voices
```

**Response:**
```json
{
  "voices": ["voice1", "voice2", "voice3"]
}
```

### Synthesize Speech (JSON Response)
```
POST /synthesize
Content-Type: application/json
```

**Request Body:**
```json
{
  "text": "Hello, world! This is a test of the Kokoro TTS system.",
  "voice": "voice1",
  "speed": 1.0
}
```

**Response:**
```json
{
  "success": true,
  "message": "Speech synthesized successfully",
  "audio_data": [/* base64 encoded WAV data */],
  "sample_rate": 22050
}
```

### Synthesize Speech (Direct WAV)
```
POST /synthesize/wav
Content-Type: application/json
```

**Request Body:**
```json
{
  "text": "Hello, world!",
  "voice": "voice1",
  "speed": 1.2
}
```

**Response:**
- Content-Type: `audio/wav`
- Body: Raw WAV audio data

## API Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `text` | string | Yes | - | Text to synthesize |
| `voice` | string | No | "default" | Voice to use (from `/voices` endpoint) |
| `speed` | float | No | 1.0 | Speech speed multiplier (0.5-2.0) |

## Example Usage

### Using curl

```bash
# Get available voices
curl http://localhost:8080/voices

# Synthesize speech and save as WAV
curl -X POST http://localhost:8080/synthesize/wav \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from Kokoro TTS!", "voice": "voice1", "speed": 1.0}' \
  --output output.wav

# Get JSON response with embedded audio data
curl -X POST http://localhost:8080/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Testing the API", "voice": "voice1"}' | jq .
```

### Using Python

```python
import requests
import json

# Synthesize speech
response = requests.post('http://localhost:8080/synthesize/wav', 
    json={
        'text': 'Hello from Python!',
        'voice': 'voice1',
        'speed': 1.1
    })

if response.status_code == 200:
    with open('output.wav', 'wb') as f:
        f.write(response.content)
    print("Audio saved to output.wav")
else:
    print(f"Error: {response.status_code}")
```

### Using JavaScript

```javascript
async function synthesizeSpeech(text, voice = 'voice1', speed = 1.0) {
    const response = await fetch('http://localhost:8080/synthesize/wav', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text, voice, speed })
    });
    
    if (response.ok) {
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        audio.play();
    } else {
        console.error('Synthesis failed:', response.status);
    }
}

// Usage
synthesizeSpeech("Hello from JavaScript!", "voice1", 1.0);
```

## Performance Notes

- First request may take longer due to model initialization
- Subsequent requests are much faster
- Memory usage depends on model size (~92MB for assets)
- CPU inference speed varies by hardware

## Troubleshooting

### Model Loading Issues
- Ensure all assets are properly downloaded with `prepare_assets.sh`
- Check that the `assets/` directory contains all required files
- Verify ONNX Runtime can find the model file

### Audio Output Issues
- Check that the sample rate matches your audio system
- Verify WAV encoding compatibility
- Try different voice names if synthesis fails

### API Errors
- Ensure JSON request format is correct
- Check that the specified voice exists
- Verify speed parameter is within reasonable range (0.1-3.0)

## License

This project uses the Kokoro TTS model from Hugging Face. Please check the model's license for usage terms.