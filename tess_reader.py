import cv2
import pytesseract
from PIL import Image
import numpy as np

class TessReader():
    def read_img(self, path):
        return cv2.imread(path)

    def read(self, img):
        return pytesseract.image_to_string(img)

    def strip(self, text):
        return ' '.join(text.split())

    def ocr(self, path):
        img = self.read_img(path)
        raw_text = self.read(img)
        clean_text = self.strip(raw_text)

        return clean_text

