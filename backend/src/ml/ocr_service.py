import os
import regex as re
import sys
from PIL import Image
from huggingface_hub import snapshot_download


MODEL_DIR = snapshot_download(repo_id="bodhan-ai/indic-ocr")
if MODEL_DIR not in sys.path:
    sys.path.insert(0, MODEL_DIR)
from indic_ocr import IndicDocLayout, IndicBlockOCR
from idp_recognizer import build_requests
from idp_types import CropConfig
LAYOUT_WEIGHTS = os.path.join(MODEL_DIR,"weights","layout")
OCR_WEIGHTS = os.path.join(MODEL_DIR,"weights","ocr")

class IndicOCRProcessor:
    def __init__(self):
        self.layout_engine = IndicDocLayout(LAYOUT_WEIGHTS)
        self.ocr_engine = IndicBlockOCR(OCR_WEIGHTS)
        self.EXCLUDE_TYPES = {"image", "chart", "diagram", "website-link", "advertisement", "flag"}

    def process(self,images)->list[dict]:
        output = []
        for image in images:
            output.append(self.process_one(image))
        return output
    def process_one(self, rgb_array)->dict:
        pil_image = Image.fromarray(rgb_array)
        layout_blocks = self.layout_engine.backend.detect(pil_image)
        crop_cfg = CropConfig()
        requests,orders = build_requests(layout_blocks,pil_image,crop_cfg,table_format="html")
        texts = self.ocr_engine.backend.transcribe(requests)
        order_to_text = dict(zip(orders, texts))
        final_markdown_output = []
        structured_json_blocks = []

        for block in layout_blocks:
            record = block.as_record()
            record["text"] = order_to_text.get(record["order"], "")
            if record["type"].lower() not in self.EXCLUDE_TYPES:
                record["text"] = order_to_text.get(record["order"], "")
                structured_json_blocks.append(record)
                final_markdown_output.append(record["text"])
            elif record["type"] == "image":
                final_markdown_output.append("![Image Block](...)")
        complete_markdown = "\n\n".join(final_markdown_output)
        
        return {
            "markdown": complete_markdown,
            "json_layout": structured_json_blocks
        }