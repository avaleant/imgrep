# imgrep

### what does it do?

Transcribes a folder of images containing non-standard text - your folder of memes, screenshots, etc., and makes them searchable.

### how does it work?

Grabs one transcription with a small multimodal model (Moondream, 2B parameters) and one transcription with conventional OCR (pytesseract), and uses the average of similarity to both to search.

The model can reconstruct deep-fried lines of text or text made difficult to OCR by being superimposed over images; the OCR handles the majority of cases. Most images containing text can be transcribed decently enough to appear in search by at least one of them. Not a pretty solution, but has a pretty high success rate.

### how well does it work?

In active development. Basic functionality proven to work. Bugs abound.

### how fast does it work?

benchmarks coming Soon(TM)

### how do I install it?

```
curl -fsSL https://ollama.com/install.sh | sh
pip install -r requirements.txt
```

### how do I run it?

```
ollama run moondream
python watcher_in_darkness.py
```

and then move or save your images into WATCH_PATH.

```
python search.py Text to query for
```

yes, you can run both simultaneously.

### how much compute do I need?

Less than you think. I've run Moondream inference CPU-only on a $80 laptop and taken ~30 seconds per image. Not optimal, wouldn't recommend, but it works.
