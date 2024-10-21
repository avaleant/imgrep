from contextlib import contextmanager
import signal
import subprocess
import magic
import os
import time

from ollama_vision_client import OllamaVisionClient
from tess_reader import TessReader
from env import db
from colorlogger import logger

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


class TranscriptionHandler:
    def __init__(self, db):
        self.client = OllamaVisionClient(host="http://localhost:11434")
        self.reader = TessReader()
        self.db = db
        self.timeout = 120

    def transcribe(self, file_path):
         logger.info(f"Saw an image {file_path}")
         try:
             with time_limit(self.timeout):
                 self._transcribe_exec(file_path)
         except TimeoutException as e:
             logger.warning(f"Couldn't process {file_path}. Timed out after {self.timeout} seconds.")
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
                logger.info("LLM: " + response['response'])
                logger.info("OCR: " + ocr_transcription)
         except Exception as e:
                logger.error(f"Error: {e}")
                self.shell_restart_ollama()
                
    # temporary stopgap, restart shell in case of errors that break server
    # (e.g. extremely long processes failing to terminate server side)
    def shell_restart_ollama(self):
        logger.warning("Restarting Ollama...")
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


