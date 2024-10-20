from tinydb import TinyDB, Query
from rapidfuzz import process, fuzz
import sys
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

db = TinyDB('memes.json')

# Extremely primitive way to fuzz based on two keys in a value set
# taking their average.
def ratio_hk(e1, e2, processor=None, score_cutoff=None):
    to_llm = fuzz.token_set_ratio(e1.lower(), e2['llm_transcription'].lower(), 
                      processor=processor, score_cutoff=score_cutoff)
    # print(f"Score for {e2['llm_transcription']} is {to_llm}")
    to_ocr = fuzz.token_set_ratio(e1.lower(), e2['ocr_transcription'].lower(), 
                      processor=processor, score_cutoff=score_cutoff)
    # print(f"Score for {e2['ocr_transcription']} is {to_ocr}")
    return (to_llm + to_ocr) / 2

def search(query, limit=5):
    return process.extract(query, db.all(), limit=limit, scorer=ratio_hk)

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

        search_button = ttk.Button(search_frame, text="Search", command=self.perform_search)
        search_button.pack(side=tk.LEFT)

        self.results_frame = ttk.Frame(self)
        self.results_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    def perform_search(self):
        query = self.search_entry.get()
        results = search(query, limit=5)

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
            ttk.Label(info_frame, text=f"LLM: {item['llm_transcription'][:50]}...").pack(anchor=tk.W)
            ttk.Label(info_frame, text=f"OCR: {item['ocr_transcription'][:50]}...").pack(anchor=tk.W)

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
