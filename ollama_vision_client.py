import requests
import base64
from typing import List, Optional

class OllamaVisionClient:
    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host
        self.api_endpoint = f"{host}/api/generate"

    def encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def generate_response(self,
                          model: str,
                          prompt: str,
                          image_paths: List[str],
                          stream: bool = False) -> dict:
       encoded_images = [self.encode_image(img) for img in image_paths]

       payload = {
               "model": model,
               "prompt": prompt,
               "images": encoded_images,
               "stream": stream
               }

       response = requests.post(self.api_endpoint, json=payload)
       response.raise_for_status()

       if stream:
           return self._handle_stream(response)
       return response.json()

    def _handle_stream(self, response: requests.Response) -> dict:
        full_response = ""
        for line in response.iter_lines():
            if line:
                json_response = json.loads(line)
                if "response" in json_response:
                    full_response += json_response["response"]
                if json_response.get("done", False):
                    return {"response": full_response}

        return {"response": full_response}

