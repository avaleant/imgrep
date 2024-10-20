import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import magic
import requests
import json
import base64
from tinydb import TinyDB, Query
from rapidfuzz import process, fuzz
import os
from dotenv import load_dotenv
import traceback

from ollama_vision_client import OllamaVisionClient
from tess_reader import TessReader

class MemeWatcher(FileSystemEventHandler):
    def __init__(self, db):
        self.client = OllamaVisionClient(host="http://localhost:11434")
        self.reader = TessReader()
        self.db = db

    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            try:
                file_type = self.get_file_type(file_path)
                
                if file_path.endswith('.part'):
                    print(f"Partial download phantom {file_path}")
                    return

                if file_type.startswith('image'):
                    self.transcribe(file_path)
            except FileNotFoundError:
                  print(f"File at {file_path} was created and immediately destroyed.")

    def on_modified(self, event):
        if not event.is_directory:
            file_path = event.src_path

            print(f"Saw modification at {file_path}")
            try:
                stats = os.stat(file_path)
                print(f"current size is {stats.st_size} bytes")
            except FileNotFoundError:
                print(f"{file_path} destroyed immediately after modification.")

    def transcribe(self, file_path):
         print(f"Saw an image {file_path}")
         try:
                response = self.client.generate_response(
                    model="moondream",
                    prompt="What text is in this image?",
                    image_paths=[file_path]
                    )
                ocr_transcription = self.reader.ocr(file_path)

                db.insert({'file': file_path, 'llm_transcription': response["response"], 'ocr_transcription': ocr_transcription})
                print("LLM: " + response['response'])
                print("OCR: " + ocr_transcription)
         except Exception as e:
                print(f"Error: {e}")
                print(traceback.format_exc())
    
    def on_moved(self, event):         
        if not event.is_directory:
            file_path = event.src_path
            print(f"Saw movement from {file_path} to {event.dest_path}")
            if file_path.endswith('.part'):
                print(f"Completing a download.")
                self.transcribe(event.dest_path)

    def get_file_type(self, file_path):
         mime = magic.Magic(mime=True)
         return mime.from_file(file_path)

if __name__ == "__main__":
    load_dotenv()

    db = TinyDB(os.getenv('DB_PATH'))
    
    path_to_watch = os.getenv('WATCH_PATH')
    event_handler = MemeWatcher(db)
    observer = Observer()
    observer.schedule(event_handler, path_to_watch, recursive=True)
    observer.start()

    print("Watcher In Darkness is online. Please stand by...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


