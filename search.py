from tinydb import TinyDB, Query
from rapidfuzz import process, fuzz
import sys

db = TinyDB('memes.json')

# fuzz.ratio based on a key in a value set
def ratio_hk(e1, e2, processor=None, score_cutoff=None):
    return fuzz.ratio(e1, e2['transcription'], 
                      processor=processor, score_cutoff=score_cutoff)

def search(query, limit=5):
    return process.extract(query, db.all(), limit=limit, scorer=ratio_hk)

if __name__ == "__main__":
    query = ' '.join(sys.argv[1:len(sys.argv)])
    result = search(query, limit=1)
    for possible in result:
        print(f"{possible[0]['file']}: {possible[0]['transcription']}")
