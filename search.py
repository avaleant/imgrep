from tinydb import TinyDB, Query
from rapidfuzz import process, fuzz
import sys

db = TinyDB('memes.json')

# Extremely primitive way to fuzz.partial_ratio based on two keys in a value set
# taking their average.
def ratio_hk(e1, e2, processor=None, score_cutoff=None):
    to_llm = fuzz.partial_ratio(e1, e2['llm_transcription'], 
                      processor=processor, score_cutoff=score_cutoff)
    # print(f"Score for {e2['llm_transcription']} is {to_llm}")
    to_ocr = fuzz.partial_ratio(e1, e2['ocr_transcription'], 
                      processor=processor, score_cutoff=score_cutoff)
    # print(f"Score for {e2['ocr_transcription']} is {to_ocr}")
    return (to_llm + to_ocr) / 2

def search(query, limit=5):
    return process.extract(query, db.all(), limit=limit, scorer=ratio_hk)

if __name__ == "__main__":
    query = ' '.join(sys.argv[1:len(sys.argv)])
    result = search(query, limit=1)
    for possible in result:
        print(f"{possible[0]['file']}:")
        print(f"{possible[0]['llm_transcription']}")
        print(f"{possible[0]['ocr_transcription']}")
