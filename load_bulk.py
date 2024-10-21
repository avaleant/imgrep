from env import db
from os import listdir
from os.path import isfile, join
import sys

from transcription_handler import TranscriptionHandler

if __name__ == "__main__":
    transcriber = TranscriptionHandler(db)

    path = sys.argv[1]
    files = [f for f in listdir(path) if isfile(join(path, f))]

    for file in files:
        # TODO: check image type
        transcriber.transcribe(join(path, file))


