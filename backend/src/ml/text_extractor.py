import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from .prompt import EXTRACTOR_MODEL_PROMPT
from .base import BaseProcessor
from .extractors import (
    WestBengalEnglishRORV1,
    WestBengalBengaliRORV1,
)


FIELD_LABELS = {
    "district":            "District",
    "khata_number":        "Khatian No",       
    "survey_number":       "J.L.No",           
    "village":             "Mouza",
    "tehsil":              "Police Station",
    "prep_date":           "Khatian Prep.Date",
    "total_plots":         "Total Plots",
    "landowner_name":      "Name",
    "guardian_name":       "Father/Husband",
    "landowner_address":   "Address",
    "plotwise_section":    "Plot-wise Land Details",
    "total_khatian_count": "Total Khatian Count",
    "fees_received":       "Fees Received",
    "signed_by":           "Digitally signed by",
}



class LLMTextExtractor(BaseProcessor):
    def __init__(self,model_name):
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            dtype=torch.float16,
            device_map="cpu",
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
    def process(self,results):
        pages = self.preprocess(results)
        print(f"Pages : \n{pages}")
        prompt = EXTRACTOR_MODEL_PROMPT + f"""<<<\n{pages}\n>>>\nJSON:"""
        messages = [
            {"role": "system", "content": "You are a land-record information extraction model"},
            {"role": "user", "content": prompt}
        ]
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=1024,
            do_sample=True,
            temperature=0.2,
            top_p=0.8,
            top_k=20,
            repetition_penalty=1.1,
            eos_token_id=self.tokenizer.eos_token_id,
            pad_token_id=self.tokenizer.pad_token_id or self.tokenizer.eos_token_id,       
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return response
    def preprocess(self,result):
        pages = []
        for page in result:
            pages.extend(page.get("page",[]))
        return "\n".join("\t".join(row) if isinstance(row, list) else str(row) for row in pages)

class RegexRegistry:

    def __init__(self):
        self.registry = {
            ("bengali", "wb"): [
                WestBengalBengaliRORV1(),
            ],

            ("english", "wb"): [
                WestBengalEnglishRORV1(),
            ],
        }
        self.transliterate = None
        self.script_detector = None

    def _set_script_funcs(self,transliterate,detector):
        self.transliterate = transliterate
        self.script_detector = detector

    def extract(self,text,blocks,language,state):
        candidates = self.registry.get(
            (language, state),
            []
        )

        if not candidates:
            return None

        best = None
        best_score = 0.0

        for extractor in candidates:
            score = extractor.detect(text)
            if score > best_score:
                best_score = score
                best = extractor
        if best is None or best_score < 0.70:
            return None

        return {"extractor":best.document_id,"confidence":best_score,"data":best.process(text,blocks,self.transliterate,self.script_detector)}
    
