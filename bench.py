#!/usr/bin/env python3
import argparse
import base64
import json
import requests
from pathlib import Path

from ollama_vision_client import OllamaVisionClient

def main():
    parser = argparse.ArgumentParser(description="Send images to Ollama vision models")
    parser.add_argument("--model", default="moondream", help="Model to use (default: moondream)")
    parser.add_argument("--prompt", default="Describe this image:", help="Prompt to send to model")
    parser.add_argument("--host", default="http://localhost:11434", help="Ollama host")
    parser.add_argument("--images", nargs="+", required=True, help="Paths to image files")
    parser.add_argument("--stream", action="store_true", help="Stream the response")
    
    args = parser.parse_args()
    
    client = OllamaVisionClient(host=args.host)
    
    try:
        response = client.generate_response(
            model=args.model,
            prompt=args.prompt,
            image_paths=args.images,
            stream=args.stream
        )
        print(response['response'])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
