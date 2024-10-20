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
import signal
from contextlib import contextmanager
import subprocess

from ollama_vision_client import OllamaVisionClient
from tess_reader import TessReader

class TimeoutException(Exception): pass

@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException(f"Process {signum} timed out")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

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

class TranscriptionHandler:
    def __init__(self, db):
        self.client = OllamaVisionClient(host="http://localhost:11434")
        self.reader = TessReader()
        self.db = db
        self.timeout = 120

    def transcribe(self, file_path):
         print(f"Saw an image {file_path}")
         try:
             with time_limit(self.timeout):
                 self._transcribe_exec(file_path)
         except TimeoutException as e:
             print(f"Couldn't process {file_path}. Timed out after {self.timeout} seconds.")
             self.shell_restart_ollama()


    def _transcribe_exec(self, file_path):
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
                self.shell_restart_ollama()
                
    # temporary stopgap, restart shell in case of errors that break server
    # (e.g. extremely long processes failing to terminate server side)
    def shell_restart_ollama(self):
        print("Restarting Ollama...")
        subprocess.run(["ollama", "stop", "moondream"])
        process = subprocess.Popen(["ollama run moondream"],
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True,
                                   shell=True)
        time.sleep(1)
        process.communicate(input="\x04")
        process.wait()
        return process.returncode
    
    def on_moved(self, event):         
        if not event.is_directory:
            file_path = event.src_path
            print(f"Saw movement from {file_path} to {event.dest_path}")
            if file_path.endswith('.part'):
                print(f"Completing a download.")
                self.transcribe(event.dest_path)


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
            event_handler.handle_queue()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


