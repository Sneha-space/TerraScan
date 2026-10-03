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

    def process(self,key:str,state:str="wb"):
        path = os.path.join(UPLOAD_DIR,key)
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
        # self.ingest_to_db(key,result,text_result["confidence"])
        # stop_session(key)
    def ingest_to_db(self,key,result,confidence):
        session = get_session(key)
        doc_id = session["doc_id"]
        pages = format_output(result,confidence)
        save_document_results(doc_id,pages)
        


def format_output(result,confidence)->list[list[dict]]:
    output = []
    for i,plot in enumerate(result["plot_area"]["per_plot"]):
        info = {
            "owner_name":{"value":result["landowner_details"]["name"],"confidence":confidence},
            "guardian":{"value":result["landowner_details"]["guardian"],"confidence":confidence},
            "survey_number":{"value":result["survey_number"],"confidence":confidence},
            "khasra_number":{"value":plot["plot_no"],"confidence":confidence},
            "khata_number":{"value":result["khata_number"],"confidence":confidence},
            "area":{"value":plot["total_plot_area"],"confidence":confidence},
            "ocupier_share":{"value":plot["occupier_share"],"confidence":confidence},
            "share_area":{"value":plot["share_area"],"confidence":confidence},
            "village":{"value":result["village"],"confidence":confidence},
            "tehsil":{"value":result["tehsil"],"confidence":confidence},
            "district":{"value":result["district"],"confidence":confidence},
            "state":{"value":None,"confidence":confidence},
            "land_classification":{"value":result["land_classification"][i],"confidence":confidence},
            "mutation_number":{"value":result["mutation_records"],"confidence":confidence},
            "mutation_date":{"value":result["registration_information"]["certification_date"],"confidence":confidence},
            "registration_number":{"value":result["registration_information"]["copy_no"],"confidence":confidence},
        }
        output.append(info)
    return [output]

