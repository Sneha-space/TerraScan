import os
import numpy as np

from .base import BaseProcessor
from .image_loader import ImageLoader
from .image_enhancer import CVProcessor
from .ocr_service import IndicOCRProcessor
from .text_processor import TextProcessor
from .script_detector import ScriptDetector
from .text_extractor import LLMTextExtractor,RegexRegistry
from .transliterate import Transliterator
from .validator_model import LandRecordExtraction
from ..core.config import UPLOAD_DIR
from ..services.ingest import save_document_results
from ..core.session_maker import get_session,delete_session,stop_session


class MlPipeline(BaseProcessor):
    def __init__(self):
        self.image_loader = ImageLoader()
        self.cvprocessor = CVProcessor()
        self.ocr_processor = IndicOCRProcessor()
        self.script_detector = ScriptDetector()
        self.text_processor = TextProcessor()
        self.re_registry = RegexRegistry()
        self.llm_extractor = LLMTextExtractor("Qwen/Qwen3.5-4B")
        self.transliterate = Transliterator()

        self.re_registry._set_script_funcs(self.transliterate,self.script_detector)

    def process(self,path:str,state:str="wb"):
        # path = os.path.join(UPLOAD_DIR,key)
        images:np.ndarray = self.image_loader.process(path) #list[np.ndarray]
        images:np.ndarray = self.cvprocessor.process(images) #list[np.ndarray]
        result:list[dict] = self.ocr_processor.process(images) #[{markdown,json_layout},...]
        text,blocks = self.text_processor.process(result)  # str,list[dict]->[{'conf','text'}]
        script = self.script_detector.process(text)
        records = self.re_registry.extract(text,blocks,script["primary_script"],state)
        if records is None:
            records = self.llm_extractor.process(text)
        records = LandRecordExtraction.model_validate(records)
        return records.dict()
        