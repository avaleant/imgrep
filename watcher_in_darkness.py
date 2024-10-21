import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests
import json
import base64
from tinydb import TinyDB, Query
from rapidfuzz import process, fuzz
import os
from dotenv import load_dotenv
import traceback
import magic

from ollama_vision_client import OllamaVisionClient
from tess_reader import TessReader
from transcription_handler import TranscriptionHandler

class MemeWatcher(FileSystemEventHandler):
    def __init__(self, db):
        self.queue = []
        self.transcriber = TranscriptionHandler(db)

    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            try:
                file_type = self.get_file_type(file_path)
                
                if file_path.endswith('.part'):
                    print(f"Partial download phantom {file_path}")
                    return

                if file_type.startswith('image') and not file_type == 'image/gif':
                    # print("FT:" + file_type)
                    self.queue.append(file_path)
                    print(f"{len(self.queue)} items currently in queue.")
                    # self.transcribe(file_path)
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

    def handle_queue(self):
        for path in self.queue:
            try:
                self.transcriber.transcribe(path)
            finally:
                self.queue.remove(path)
                print(f"Entry handled, queue now at {len(self.queue)}")

    def get_file_type(self, file_path):
         mime = magic.Magic(mime=True)
         return mime.from_file(file_path)
     
    def on_moved(self, event):         
        if not event.is_directory:
            file_path = event.src_path
            print(f"Saw movement from {file_path} to {event.dest_path}")
            if file_path.endswith('.part'):
                print(f"Completing a download.")
                if file_type.startswith('image') and not file_type == 'image/gif':
                    # print("FT:" + file_type)
                    self.queue.append(file_path)
                    print(f"{len(self.queue)} items currently in queue.")


if __name__ == "__main__":
    from env import db
    
    path_to_watch = os.getenv('WATCH_PATH')
    event_handler = MemeWatcher(db)
    observer = Observer()
    observer.schedule(event_handler, path_to_watch, recursive=True)
    observer.start()

    print("Watcher In Darkness is online. Please stand by...")

    try:
        while True:
            time.sleep(1)
            event_handler.handle_queue()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


