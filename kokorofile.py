#!/usr/bin/env python3
import argparse
import sys
import sounddevice as sd
import soundfile as sf
from kokoro_onnx import Kokoro
import tempfile
import os
from platformdirs import user_cache_dir, user_data_dir
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
from typing import Optional

def setup_logging(debug=False):
    """Setup logging configuration."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def get_cache_dirs():
    """Get platform-specific cache and data directories."""
    cache_dir = user_cache_dir("kokorofile", "kokorofile")
    data_dir = user_data_dir("kokorofile", "kokorofile")
    
    # Create directories if they don't exist
    os.makedirs(cache_dir, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)
    
    return cache_dir, data_dir

def download_model_files(cache_dir):
    """Download model files if they don't exist."""
    import urllib.request
    import hashlib
    
    model_url = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
    voices_url = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"
    
    model_path = os.path.join(cache_dir, "kokoro-v1.0.onnx")
    voices_path = os.path.join(cache_dir, "voices-v1.0.bin")
    
    def download_file(url, path):
        if not os.path.exists(path):
            logging.info(f"Downloading {os.path.basename(path)}...")
            urllib.request.urlretrieve(url, path)
        return path
    
    return (
        download_file(model_url, model_path),
        download_file(voices_url, voices_path)
    )

def text_to_speech(text, output_file=None, device=None, voice="af_sarah", speed=1.0, lang="en-us", debug=False):
    """Convert text to speech and either save to file or play through device."""
    # Get platform-specific directories
    cache_dir, data_dir = get_cache_dirs()
    
    # Download model files if needed
    model_path, voices_path = download_model_files(cache_dir)
    
    # Initialize Kokoro with model files
    kokoro = Kokoro(
        model_path,
        voices_path
    )
    
    # Generate audio with specified parameters
    logging.info(f"Generating speech with voice '{voice}', speed {speed}, language '{lang}'")
    audio, sample_rate = kokoro.create(
        text,
        voice=voice,
        speed=speed,
        lang=lang
    )
    
    if output_file:
        # Save to file
        sf.write(output_file, audio, sample_rate)
        print(f"Audio saved to {output_file}")
    elif device is not None:
        # Play through specified device
        sd.play(audio, sample_rate, device=device)
        sd.wait()
    else:
        # Play through default device
        sd.play(audio, sample_rate)
        sd.wait()

class TTSRequest(BaseModel):
    text: str
    voice: str = "af_sarah"
    speed: float = 1.0
    lang: str = "en-us"

def run_server(host: str = "127.0.0.1", port: int = 8000):
    """Run FastAPI server for text-to-speech requests."""
    app = FastAPI(
        title="Kokorofile TTS Server",
        description="Text-to-speech server using Kokoro ONNX",
        version="0.1.0"
    )
    
    @app.post("/synthesize")
    async def synthesize(request: TTSRequest):
        """Synthesize speech from text and return audio file."""
        try:
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                output_path = temp_file.name
            
            # Generate speech
            text_to_speech(
                request.text,
                output_path,
                voice=request.voice,
                speed=request.speed,
                lang=request.lang
            )
            
            # Return the audio file
            return FileResponse(
                output_path,
                media_type="audio/wav",
                filename="output.wav"
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/voices")
    async def list_voices():
        """List available voices."""
        # This is a placeholder - you might want to implement actual voice listing
        return {"voices": ["af_sarah"]}
    
    @app.get("/devices")
    async def list_devices():
        """List available audio devices."""
        return {"devices": sd.query_devices()}
    
    print(f"Server running at http://{host}:{port}")
    print(f"API documentation available at http://{host}:{port}/docs")
    uvicorn.run(app, host=host, port=port)

def main():
    parser = argparse.ArgumentParser(description='Convert text to speech using Kokoro')
    parser.add_argument('input', nargs='?', help='Input text or file path (if not provided, reads from stdin)')
    parser.add_argument('-o', '--output', help='Output file path (if not provided, plays through audio device)')
    parser.add_argument('-d', '--device', type=int, help='Audio device ID to use for playback')
    parser.add_argument('-l', '--list-devices', action='store_true', help='List available audio devices')
    parser.add_argument('--cache-dir', help='Override default cache directory')
    parser.add_argument('--data-dir', help='Override default data directory')
    parser.add_argument('--voice', default='af_sarah', help='Voice to use (default: af_sarah)')
    parser.add_argument('--speed', type=float, default=1.0, help='Speech speed (default: 1.0)')
    parser.add_argument('--lang', default='en-us', help='Language code (default: en-us)')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--server', action='store_true', help='Run as HTTP server')
    parser.add_argument('--host', default='127.0.0.1', help='Server host (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8000, help='Server port (default: 8000)')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.debug)
    
    if args.server:
        run_server(args.host, args.port)
        return
    
    if args.list_devices:
        print("\nAvailable audio devices:")
        print(sd.query_devices())
        return
    
    # Get input text
    if args.input:
        if os.path.isfile(args.input):
            with open(args.input, 'r') as f:
                text = f.read().strip()
        else:
            text = args.input
    else:
        # Read from stdin without prompting
        text = sys.stdin.read().strip()
    
    if not text:
        print("Error: No input text provided", file=sys.stderr)
        sys.exit(1)
    
    try:
        text_to_speech(
            text,
            args.output,
            args.device,
            voice=args.voice,
            speed=args.speed,
            lang=args.lang,
            debug=args.debug
        )
    except Exception as e:
        logging.error(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 