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

### aren't there better open source models?

much better! for instance, llama3.2-vision consistently extracts text and responds with only text, even on screenshots of long paragraphs. But llama3.2-vision also takes up 4x as much space and significantly more compute and time.

this piece of software was assembled specifically to get a working and resilient pipeline without being able to rely on having the best currently available model which can accurately follow criteria - if you have the GPUs on hand to run llama3.2-vision on everything you want to index, you already have access to much better solutions.

this isn't a trivial fix either that can be improved by using a *slightly* larger  model - llava-7b, for instance, performs worse than moondream across a wide variety of images when asked to extract text only.
