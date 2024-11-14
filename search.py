from tinydb import TinyDB, Query
from rapidfuzz import process, fuzz
from rapidfuzz.utils import default_process
import sys
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from functools import partial

db = TinyDB('memes.json')

# returns the hypothetical length of the set of "partial matches"
# where, for instance, a 50% score would count as "half"
def fuzzy_intersection_size(set1, set2):
    fuzzy_sect = 0.0 
    for s1 in set1:
        for s2 in set2:
            sim = fuzz.ratio(s1, s2)
            most_similar = 0.0
            if sim > 85:
                fuzzy_sect -= most_similar # don't count similarity twice
                most_similar = sim / 100
                fuzzy_sect += most_similar
                
    return fuzzy_sect 

# Extremely primitive way to fuzz based on two keys in a value set
# taking their average.
def token_ignoring_surrounding_ratio(query, text):
    # Tokenize query and text
    query_tokens = set(default_process(query).split())
    text_tokens = set(default_process(text).split())

    if not query_tokens:
        return 0

    # Calculate how many query tokens are found in the text
    # matches = query_tokens.intersection(text_tokens)
    matches = fuzzy_intersection_size(query_tokens, text_tokens)
    return 100 * len(matches) / len(query_tokens)

def ratio_hk(e1, e2, processor=None, score_cutoff=None):
    to_llm = token_ignoring_surrounding_ratio(e1.lower(), e2['llm_transcription'].lower())
    #fuzz.token_sort_ratio(e1.lower(), e2['llm_transcription'].lower(), 
                      #processor=processor, score_cutoff=score_cutoff)
    # print(f"Score for {e2['llm_transcription']} is {to_llm}")
    to_ocr = token_ignoring_surrounding_ratio(e1.lower(), e2['ocr_transcription'].lower())
    # to_ocr = fuzz.token_sort_ratio(e1.lower(), e2['ocr_transcription'].lower(), 
                     # processor=processor, score_cutoff=score_cutoff)
    # print(f"Score for {e2['ocr_transcription']} is {to_ocr}")

    # weight high single scores
    if to_llm > 80:
        to_llm *= 2
    if to_ocr > 80:
        to_ocr *= 2
    return (to_llm + to_ocr) / 2

def search(query, limit=10, score_cutoff=None):
    return process.extract(query, db.all(), limit=limit, scorer=ratio_hk, score_cutoff=score_cutoff)

class ImageSearcher(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("imgrep")
        self.geometry("800x600")
        self.create_widgets()

    def create_widgets(self):
        search_frame = ttk.Frame(self)
        search_frame.pack(pady=10, padx=10, fill=tk.X)

        self.search_entry = ttk.Entry(search_frame, width=50)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))

        self.search_entry.bind('<Return>', lambda e: self.perform_search())

        search_button = ttk.Button(search_frame, text="Search", command=self.perform_search)
        search_button.pack(side=tk.LEFT)

        self.results_label = ttk.Label(self, text="Enter your query above")
        self.results_label.pack(pady=0, padx=10, anchor=tk.W)

        self.results_frame = ttk.Frame(self)
        self.results_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    def perform_search(self):
        query = self.search_entry.get()
        if not query.strip():
            self.results_label.config(text="Please enter a search query.")
            return

        prev = search(query, limit=None, score_cutoff=49)

        result_count = len(prev)
        append = ""
        # only 10 results will be shown at max
        # this triggers if less than 10 results matched score_cutoff
        if result_count < 11:
            append = ", showing less likely results"
        self.results_label.config(text=f"{result_count} likely match(es) found for {query}{append}")

        results = search(query)

        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        # Display new results
        # print(results[0])
        for i, (item, score, _) in enumerate(results):
            result_frame = ttk.Frame(self.results_frame)
            result_frame.pack(pady=10, fill=tk.X)

            # Load and display image
            try:
                img = Image.open(item['file'])
                img.thumbnail((200, 200))
                photo = ImageTk.PhotoImage(img)
                img_label = ttk.Label(result_frame, image=photo)
                img_label.image = photo 
                img_label.pack(side=tk.LEFT, padx=(0, 10))
            except Exception as e:
                print(f"Error loading image {item['file']}: {e}")
                img_label = ttk.Label(result_frame, text="Image not found")
                img_label.pack(side=tk.LEFT, padx=(0, 10))

            # Display information
            info_frame = ttk.Frame(result_frame)
            info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

            ttk.Label(info_frame, text=f"File: {os.path.basename(item['file'])}").pack(anchor=tk.W)
            ttk.Label(info_frame, text=f"Score: {score:.2f}").pack(anchor=tk.W)
            ttk.Label(info_frame, text=f"LLM: {item['llm_transcription']}").pack(anchor=tk.W)
            ttk.Label(info_frame, text=f"OCR: {item['ocr_transcription']}").pack(anchor=tk.W)

if __name__ == "__main__":
    app = ImageSearcher()
    app.mainloop()



if False and __name__ == "__main__":
    query = ' '.join(sys.argv[1:len(sys.argv)])
    result = search(query, limit=1)
    for possible in result:
        print(f"{possible[0]['file']}:")
        print(f"{possible[0]['llm_transcription']}")
        print(f"{possible[0]['ocr_transcription']}")
