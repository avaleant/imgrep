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
from colorlogger import logger

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
                    logger.info(f"Partial download phantom {file_path}")
                    return

                if file_type.startswith('image') and not file_type == 'image/gif':
                    logger.debug("file type:" + file_type)
                    self.queue.append(file_path)
                    logger.info(f"{len(self.queue)} items currently in queue.")
            except FileNotFoundError:
                  logger.warning(f"File at {file_path} was created and immediately destroyed.")

    def on_modified(self, event):
        if not event.is_directory:
            file_path = event.src_path

            logger.debug(f"Saw modification at {file_path}")
            try:
                stats = os.stat(file_path)
                logger.debug(f"current size is {stats.st_size} bytes")
            except FileNotFoundError:
                logger.warning(f"{file_path} destroyed immediately after modification.")

    def handle_queue(self):
        for path in self.queue:
            try:
                self.transcriber.transcribe(path)
            finally:
                self.queue.remove(path)
                logger.info(f"Entry handled, queue now at {len(self.queue)}")

    def get_file_type(self, file_path):
         mime = magic.Magic(mime=True)
         return mime.from_file(file_path)
     
    def on_moved(self, event):         
        if not event.is_directory:
            file_path = event.src_path
            logger.debug(f"Saw movement from {file_path} to {event.dest_path}")
            if file_path.endswith('.part'):
                logger.debug(f"Completing a download.")
                if file_type.startswith('image') and not file_type == 'image/gif':
                    logger.debug("file type: " + file_type)
                    self.queue.append(file_path)
                    logger.info(f"{len(self.queue)} items currently in queue.")


if __name__ == "__main__":
    from env import db
    
    path_to_watch = os.getenv('WATCH_PATH')
    event_handler = MemeWatcher(db)
    observer = Observer()
    observer.schedule(event_handler, path_to_watch, recursive=True)
    observer.start()

    logger.info("Watcher In Darkness is online. Please stand by...")

    try:
        while True:
            time.sleep(1)
            event_handler.handle_queue()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


