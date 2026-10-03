import filetype
import numpy as np
import cv2
import pymupdf

from .base import BaseProcessor

class ImageLoader(BaseProcessor):
    def __init__(self):
        self.image_ext = ["png","jpg","jpeg"]
        self.pdf_ext = ["pdf"]
    def process(self,path):
        ext = self.guess_file_type(path)
        if ext in self.pdf_ext:
            list_image_bytes = self.extract_images_from_pdf(path)
            images = self.process_bytes(list_image_bytes)
        elif ext in self.image_ext:
            images = [cv2.imread(path)]
        else:
            raise TypeError("File type not supported! Type should be pdf,png,jpg or jpeg")
        return images
    def guess_file_type(self,path):
        kind = filetype.guess(path)
        return kind.extension
    def extract_images_from_pdf(self,path:str)->list:
        image_frames = []
        try:
            doc = pymupdf.open(path)
            for page in doc:
                images = page.get_images(full=True)
                for img in images:
                    xref = img[0]
                    image = doc.extract_image(xref)
                    image_bytes =  image["image"]
                    image_frames.append(image_bytes)                
        except:
            pass
        return image_frames
    def process_bytes(self, list_image_bytes: bytes) -> list[np.ndarray]:
        images = []
        for image_bytes in list_image_bytes:
            image = np.frombuffer(image_bytes, dtype=np.uint8)
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)

            if image is None:
                raise ValueError("Invalid image bytes")
            images.append(image)
        return images

    