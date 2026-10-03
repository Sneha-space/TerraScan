import regex as re
import unicodedata
from abc import ABC
from typing import Optional
from rapidfuzz import process, fuzz
from ..transliterate import Transliterator 
from ..script_detector import ScriptDetector
class RegexTextExtractor(ABC):
    def __init__(self):
        self.document_id = "base"
        self.language = "unknown"
        self.state = "unknown"
        self.DENORM_DIGITS = None
        self.LAND_CLASSES = {}
        self.FIELD_ALIASES = {}
        self.TABLE_HEADER_ALIASES = {}
        self.DOCUMENT_ANCHORS = []
        self._blocks = []
        self._field_confidences = {}
        self._special_confidences = {}
    
    def get_exact_cls(self,predicted:str,choices:str="land_class"):
        if not isinstance(predicted,str):
            return (None,None,0.0)
        if choices=="land_class":
            group = self.LAND_CLASSES.keys()
        closest_cls, _,_ = process.extractOne(predicted,group,scorer=fuzz.partial_ratio)
        alignment = fuzz.partial_ratio_alignment(predicted, closest_cls)
        matched_len = alignment.dest_end - alignment.dest_start
        score = (matched_len / len(closest_cls)) * 100
        if score>0.75:
            return closest_cls,score
        return (None,None,0.0)
    def verify_plot_area(self,total_plot_area,occupier_share,share_area):
        try:
            total_plot_area = float(total_plot_area)
        except:
            try:
                total_plot_area = float(occupier_share) * float(share_area)
            except:
                total_plot_area = None
        return None if total_plot_area is None else str(total_plot_area)
            
    def compile_patterns(self):
        self.field_patterns = {}
        for field, aliases in self.FIELD_ALIASES.items():
            self.field_patterns[field] = [
                self.compile_label_pattern(alias)
                for alias in aliases
            ]
        self.anchor_patterns = [
            self.compile_flexible_pattern(anchor)
            for anchor in self.DOCUMENT_ANCHORS
        ]
    def compile_flexible_pattern(self, text):
        text = unicodedata.normalize("NFC", text)
        pattern = re.escape(text)
        pattern = pattern.replace(r"\ ", r"\s*")
        return re.compile(pattern,re.IGNORECASE)
    
    def compile_label_pattern(self, label):
        label = unicodedata.normalize("NFC", label)
        pattern = re.escape(label)
        pattern = pattern.replace(r"\ ",r"\s*")
        return re.compile(rf"""(?im)^\s*(?:\(?\d{{1,2}}\)?\s*)?{pattern}\s*(?:[:\-–—]\s*)?(?P<value>.*?)\s*$""",re.VERBOSE)

    @staticmethod
    def normalize_digits(text: str) -> str:
        if not text:
            return text
        bengali = str.maketrans(
            "০১২৩৪৫৬৭৮৯",
            "0123456789"
        )
        devanagari = str.maketrans(
            "०१२३४५६७८९",
            "0123456789"
        )
        text = text.translate(bengali)
        text = text.translate(devanagari)
        return text

    def denormalize_digits(self, text: str) -> str:
        if not text:
            return text
        if self.DENORM_DIGITS:
            return text.translate(self.DENORM_DIGITS)
        return text
        
    @staticmethod
    def normalize_text(text: str) -> str:
        if text is None:
            return ""
        text = unicodedata.normalize("NFC", text)
        text = text.replace("\r", "")
        text = (
            text
            .replace("–", "-")
            .replace("—", "-")
            .replace("−", "-")
        )
        text = text.replace("\xa0", " ")
        return text

    @staticmethod
    def clean_value(value: Optional[str]):
        if value is None:
            return None
        value = value.strip()
        value = re.sub(r"[ ]{2,}", " ", value)
        return value or None

    def confidence_for_value(self, value):
        if not value:
            return 0
        value = self.normalize_digits(
            self.normalize_text(str(value)).strip()
        )
        for block in self._blocks:
            block_text = self.normalize_digits(
                self.normalize_text(block.get("text", ""))
            )
            if value.isdigit():
                found = re.search(
                    rf"(?<!\d){re.escape(value)}(?!\d)",
                    block_text
                )
            else:
                found = value in block_text
            if found:
                return block.get("conf")
        return 0

    def confidence_for_cells(self, cells):
        for cell in cells:
            confidence = self.confidence_for_value(cell)
            if confidence is not None:
                return confidence
        return None
    
    def load_rows(self, text: str):

        text = self.normalize_text(text)

        rows = []

        for line in text.split("\n"):
            cells = [
                cell.strip()
                for cell in line.split("\t")
            ]
            if any(cell for cell in cells):
                rows.append(cells)

        return rows
    def extract_field(self, rows, field):
        patterns = self.field_patterns.get(field, [])
        for row in rows:
            for i, cell in enumerate(row):
                if not cell:
                    continue
                for pattern in patterns:
                    match = pattern.match(cell)
                    if not match:
                        continue
                    value = self.clean_value(match.group("value"))
                    if not value and i + 1 < len(row):
                        value = self.clean_value(row[i + 1])
                    if value:
                        return value
        return None

    def extract_fields(self, rows):
        result = {}
        self._field_confidences = {}
        for field in self.FIELD_ALIASES:
            result[field] = self.extract_field(
                rows,
                field
            )
            self._field_confidences[field] = self.confidence_for_value(
                result[field]
            )
        return result
    def detect(self, text: str):
        normalized = self.normalize_text(text)
        matched = 0
        for pattern in self.anchor_patterns:
            if pattern.search(normalized):
                matched += 1
        if not self.anchor_patterns:
            return 0.0
        return matched / len(self.anchor_patterns)
    def extract_plot_rows(self, rows):
        plots = []
        for row in rows:
            if len(row) < 2:
                continue
            plot_no = row[0]

            if not re.fullmatch(
                r"\d+(?:/\d+)?",
                plot_no or ""
            ):
                continue

            plot = self.parse_plot_row(row)

            if plot:
                plot["confidence"] = self.confidence_for_cells(row)
                plots.append(plot)

        return plots
    def parse_plot_row(self, row):

        raise NotImplementedError
    def extract_specialized(self, text, rows):

        return {
            "plot_wise_details":
                self.extract_plot_rows(rows)
        }
    def build_schema(self, header, special):

        plots = special.get(
            "plot_wise_details",
            []
        )
        return {

            "landowner_details": {
                "name": self.field_pair(header, "landowner_name"),
                "guardian": self.field_pair(header, "guardian_name"),
                "address": self.field_pair(header, "landowner_address"),
            },

            "khasra_number":
                [
                    self.plot_pair(p, "plot_no")
                    for p in plots
                    if p.get("plot_no")
                ],

            "khata_number":self.field_pair(header, "khata_number"),

            "plot_area": {

                "total_holding_area_dec":self.special_pair(
                    special, "total_land_area_dec"
                ),
                "per_plot": [
                    {
                        "plot_no":self.plot_pair(p, "plot_no"),
                        "total_plot_area":
                        self.plot_area_pair(p),
                        "occupier_share":self.plot_pair(p, "occupier_share"),
                        "share_area":self.plot_pair(p, "share_area"),
                        "previous_khata_numbers": [
                            (
                                value,
                                self.confidence_for_value(value)
                            )
                            for value in (p.get("previous_khata_numbers") or [])
                        ],
                        "land_classification":self.get_exact_cls(predicted=p.get("land_class")),
                    }

                    for p in plots
                ],
            },

            "village":
                self.field_pair(header, "village"),

            "tehsil":
                self.field_pair(header, "tehsil"),

            "district":
                self.field_pair(header, "district"),
            "ownership_details": {

                "tenure_type":
                    self.special_pair(special, "ownership_type"),

                "total_plots":self.field_pair(header, "total_plots", normalize_digits=True)
            },

            "mutation_records":
                special.get("mutation_records"),

            "registration_information": {

                "statement":self.special_pair(
                    special, "registration_statement"
                ),

                "copy_no":
                    self.special_pair(special, "copy_no"),

                "certification_date":
                    self.special_pair(special, "certification_date"),

                "signed_by":self.field_pair(header, "signed_by"),

                "fees_received":self.special_pair(special, "fees_received"),
            },
        }

    def field_pair(self, header, field, normalize_digits=False):
        value = self.clean_value(header.get(field))
        if normalize_digits:
            value = self.normalize_digits(value)
        return value, self._field_confidences.get(field, 0)

    def special_pair(self, special, field):
        return special.get(field), self._special_confidences.get(field, 0)

    def plot_pair(self, plot, field):
        value = plot.get(field)
        if field == "plot_no":
            value = self.normalize_digits(value)
        return value, plot.get("confidence", 0)

    def plot_area_pair(self, plot):
        value = self.verify_plot_area(
            plot.get("total_plot_area"),
            plot.get("occupier_share"),
            plot.get("share_area")
        )
        return value, plot.get("confidence", 0)
    def transliterator(self,schema,transliterature:Transliterator,script_detector:ScriptDetector):
        def transliterate_pair(pair, digit=False):
            value, confidence = pair
            if value is None:
                confidence=0
            elif isinstance(confidence,(float,int)) and confidence>=0:
                if confidence<=1:
                    confidence = int(confidence*100)
                elif confidence<=100:
                    confidence = int(confidence)
            if digit:
                return (
                    self.denormalize_digits(value),
                    value,
                    confidence
                )
            src_lang = script_detector.detect(value)
            if (src_lang!="en") and (src_lang is not None):
                translated = transliterature.transliterate(
                    value,
                    src_lang=src_lang
                )
            else:
                translated=value
            return value, translated, confidence

        for key in ["name","guardian","address"]:
            val = schema["landowner_details"][key]
            schema["landowner_details"][key] = transliterate_pair(val)
        val = schema["khata_number"]
        schema["khata_number"] = transliterate_pair(val, digit=True)

        val = schema["plot_area"]["total_holding_area_dec"]
        schema["plot_area"]["total_holding_area_dec"] = transliterate_pair(val, digit=True)

        for i in range(len(schema["plot_area"]["per_plot"])):
            val = schema["plot_area"]["per_plot"][i]["plot_no"]
            schema["plot_area"]["per_plot"][i]["plot_no"] = transliterate_pair(val, digit=True)

            val = schema["plot_area"]["per_plot"][i]["total_plot_area"]
            schema["plot_area"]["per_plot"][i]["total_plot_area"] = transliterate_pair(val, digit=True)

            for key in ["occupier_share", "share_area"]:
                val = schema["plot_area"]["per_plot"][i][key]
                schema["plot_area"]["per_plot"][i][key] = transliterate_pair(
                    val,
                    digit=True
                )

            val = schema["plot_area"]["per_plot"][i]["previous_khata_numbers"]
            schema["plot_area"]["per_plot"][i]["previous_khata_numbers"] = [
                transliterate_pair(item, digit=True) for item in val
            ]

            val = schema["plot_area"]["per_plot"][i]["land_classification"]
            schema["plot_area"]["per_plot"][i]["land_classification"] = (val[0],transliterature.transliterate_land_class(val[0],self.LAND_CLASSES),val[1])
        schema["khasra_number"] = [
            transliterate_pair(value, digit=True)
            for value in schema["khasra_number"]
        ]
        for key in ["village","tehsil","district"]:
            val = schema[key]
            schema[key] = transliterate_pair(val)
        val = schema["ownership_details"]["tenure_type"]
        schema["ownership_details"]["tenure_type"] = transliterate_pair(val)
        val = schema["ownership_details"]["total_plots"]
        schema["ownership_details"]["total_plots"] = transliterate_pair(val, digit=True)
        for key in ["copy_no","certification_date"]:
            val = schema["registration_information"][key]
            schema["registration_information"][key] = transliterate_pair(val, digit=True)
        for key in ["statement", "signed_by", "fees_received"]:
            val = schema["registration_information"][key]
            schema["registration_information"][key] = transliterate_pair(val)
        return schema

    def process(self, text : str,blocks: list[dict],transliterate:Transliterator,script_detector:ScriptDetector):
        self._blocks = blocks
        text = self.normalize_text(text)
        rows = self.load_rows(text)
        header = self.extract_fields(rows)
        special = self.extract_specialized(text,rows)
        self._special_confidences = {
            key: self.confidence_for_value(value)
            for key, value in special.items()
        }
        schema = self.build_schema(header,special)
        return self.transliterator(schema,transliterate,script_detector)