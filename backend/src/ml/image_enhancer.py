import cv2
import numpy as np

from .base import BaseProcessor

class CVProcessor(BaseProcessor):
    def process(self,images:list[np.ndarray])->list[np.ndarray]:
        image_list = []
        for image in images:
            image = self.preprocess(image)
            image = self.enhance(image)
            image_list.append(image)
        return image_list
    

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray,(1948,2752))
        denoised = cv2.fastNlMeansDenoising(
            gray,
            None,
            h=10,
            templateWindowSize=7,
            searchWindowSize=21
        )

        return cv2.cvtColor(denoised,cv2.COLOR_GRAY2RGB)

    def enhance(self, image: np.ndarray) -> np.ndarray:
        return image