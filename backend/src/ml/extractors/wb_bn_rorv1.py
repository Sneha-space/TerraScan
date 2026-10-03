import regex as re
from .extractor_master import RegexTextExtractor
import unicodedata

def _nfc(pattern_text: str) -> str:
    return unicodedata.normalize("NFC", pattern_text)

class WestBengalBengaliRORV1(RegexTextExtractor):

    def __init__(self):
        super().__init__()
        self.document_id = "WB_BN_ROR_V1"
        self.language = "bn"
        self.state = "west_bengal"
        self.DENORM_DIGITS = str.maketrans("0123456789","০১২৩৪৫৬৭৮৯")
        self.LAND_CLASSES = {
            "ডাঙ্গা":"danga",
            "শালি":"shali ",
            "বাস্তু":"vastu",
            "সোনা":"sona",
            "পুকুর":"water body",
            "ডোবা":"doba",
            "প পতিত":"patit",
            "পতিত":"patit",
            "ভিটি":"viti",
            "কারখানা":"karkhana",
        }
        self.FIELD_ALIASES = {

            "landowner_name": [
                "নাম",
                "নাম-",
            ],

            "guardian_name": [
                "পিতা",
                "পিতা-",
                "পিতা/স্বামী",
                "পিতা/স্বামীর নাম",
            ],

            "landowner_address": [
                "ঠিকানা",
                "ঠিকানা-",
            ],

            "district": [
                "জেলা",
                "জেলা-",
            ],

            "village": [
                "মৌজা",
                "মৌজা-",
            ],

            "tehsil": [
                "থানা",
                "থানা-",
                "তহশিল",
                "তহশীল",
            ],

            "khata_number": [
                "খতিয়ান নং",
                "খতিয়ান নং",
                "খতিয়ান নং-",
                "খতিয়ান নং-",
            ],

            "total_plots": [
                "মোট দাগের সংখ্যা",
                "মোট দাগের সংখ্যা-",
                "মোট দাগের সংখ্যা -",
            ],

            "signed_by": [
                "Digitally signed by",
            ],
        }

        self.DOCUMENT_ANCHORS = [

            "অত্রস্বত্বের দখলকারের বিবরণ",

            "অত্রস্বত্বের নিজ দখলীয় জমি",

            "অত্রস্বত্বের নিজ দখলীয় জমি",

            "দাগ নং",

            "জমির শ্রেণী",

            "মোট দাগের সংখ্যা",
        ]

        

        self.total_area_pattern = re.compile(
            _nfc(r"""
            জমির\s*পরিমান
            \s*
            (?:\(?\s*এ\s*\)?)
            \s*[-:]?\s*
            (?P<value>
                [০-৯\d]+(?:\.[০-৯\d]+)?
            )
            """),
            re.IGNORECASE |
            re.VERBOSE
        )

        self.ownership_pattern = re.compile(
            _nfc(r"""
            \b
            (?P<value>
                রায়ত|
                পত্তন|
                বর্গাদার|
                সিকিমি|
                অধীন\s*রায়ত
            )
            \b
            """),
            re.IGNORECASE |
            re.VERBOSE
        )

        self.registration_pattern = re.compile(
            r"""
            Certified\s+to\s+be\s+true\s+copy
            .*?
            Act\s*1\s*of\s*1872
            """,
            re.IGNORECASE |
            re.DOTALL |
            re.VERBOSE
        )

        self.copy_pattern = re.compile(
            r"""
            Copy\s*No\.?
            \s*[:\-]?\s*
            (?P<value>\d+)
            """,
            re.IGNORECASE |
            re.VERBOSE
        )

        self.date_pattern = re.compile(
            r"""
            Date\s*[:\-]?\s*
            (?P<value>
                \d{4}[./-]\d{2}[./-]\d{2}
            )
            """,
            re.IGNORECASE |
            re.VERBOSE
        )

        self.khata_number_pattern = re.compile(
            _nfc(r"""
            খতিয়ান\s*নং\.?
            \s*[:\-]?\s*
            (?P<value>[০-৯\d]+)
            """),
            re.IGNORECASE |
            re.VERBOSE
        )

        self.previous_khata_pattern = re.compile(
            _nfc(r"""
            আগত\s*খ[ংঙ]?\s*নং
            \s*[:\-]?\s*
            (?P<numbers>
                [০-৯\d]+
                (?:\s*,\s*[০-৯\d]+)*
            )
            """),
            re.IGNORECASE |
            re.VERBOSE
        )

        super().compile_patterns()
    # @staticmethod
    # def rev_normalize_digits(text: str) -> str:
    #     if not text:
    #         return text
    #     bengali = str.maketrans(
    #         "0123456789",
    #         "০১২৩৪৫৬৭৮৯"
    #     )
    #     text = text.translate(bengali)
    #     return text

    def extract_fields(self, rows):
        result = super().extract_fields(rows)

        district_value = result.get("district")
        if district_value:
            district_value = re.split(
                _nfc(r"খতিয়ান\s*নং"),
                district_value,
                maxsplit=1,
            )[0]
            result["district"] = self.clean_value(district_value)

        return result

    def parse_plot_row(self, row):

        if len(row) < 2:
            return None

        plot_no = row[0]

        if not re.fullmatch(
            r"\d+(?:/\d+)?",
            plot_no
        ):
            return None
        result = {
            "plot_no": plot_no,
            "land_class": None,
            "remarks": None,
            "total_plot_area": None,
            "occupier_share": None,
            "share_area": None,
            "previous_khata_numbers": None,
        }

        if len(row) > 1:
            result["land_class"] = (
                row[1] or None
            )

        if len(row) > 2:
            result["remarks"] = (
                row[2] or None
            )

        if len(row) > 3:
            result["total_plot_area"] = (
                self.normalize_digits(row[3])
                or None
            )

        if len(row) > 4:
            result["occupier_share"] = (
                self.normalize_digits(row[4])
                or None
            )

        if len(row) > 5:
            result["share_area"] = (
                self.normalize_digits(row[5])
                or None
            )

        result["previous_khata_numbers"] = (
            self.extract_previous_khata_numbers(row)
        )

        return result

    def extract_previous_khata_numbers(self, row_or_text):
        if row_or_text is None:
            return []

        if isinstance(row_or_text, str):
            cells = [row_or_text]
        else:
            cells = row_or_text

        numbers = []
        for cell in cells:
            if not cell:
                continue
            for match in self.previous_khata_pattern.finditer(cell):
                for raw_number in match.group("numbers").split(","):
                    number = self.normalize_digits(raw_number.strip())
                    if number and number not in numbers:
                        numbers.append(number)

        return numbers or []

    def extract_specialized(self, text, rows):

        out = super().extract_specialized(
            text,
            rows
        )

        m = self.total_area_pattern.search(text)

        out["total_land_area_dec"] = (
            self.normalize_digits(
                m.group("value")
            )
            if m else None
        )

        m = self.ownership_pattern.search(text)

        out["ownership_type"] = (
            m.group("value")
            if m else None
        )

        m = self.registration_pattern.search(text)

        out["registration_statement"] = (
            re.sub(
                r"\s+",
                " ",
                m.group(0)
            ).strip()
            if m else None
        )

        m = self.copy_pattern.search(text)

        out["copy_no"] = (
            m.group("value")
            if m else None
        )

        m = self.date_pattern.search(text)

        out["certification_date"] = (
            m.group("value")
            if m else None
        )
        m = self.khata_number_pattern.search(text)

        out["khata_number_fallback"] = (
            self.normalize_digits(m.group("value"))
            if m else None
        )

        has_previous_khata_reference = bool(
            self.previous_khata_pattern.search(text)
        )

        out["mutation_records"] = (
            "found"
            if (
                re.search(
                    r"mutation|মিউটেশন|নামজারি",
                    text,
                    re.IGNORECASE
                )
                or has_previous_khata_reference
            )
            else None
        )

        fees_match = re.search(
            r"""
            Fees\s+Received
            \s*[:\-]?\s*
            (?P<value>.*?)
            (?=
                Copy\s*No
                |
                Digitally\s+signed
                |
                $
            )
            """,
            text,
            re.IGNORECASE |
            re.DOTALL |
            re.VERBOSE
        )

        out["fees_received"] = (
            re.sub(
                r"\s+",
                " ",
                fees_match.group("value")
            ).strip(" ,")
            if fees_match else None
        )

        out["plot_wise_details"] = (
            self.extract_plot_rows(rows)
        )

        return out

    def build_schema(self, header, special):
        schema = super().build_schema(header, special)

        if not schema["khata_number"][0]:
            schema["khata_number"] = (
                special.get("khata_number_fallback"),
                self._special_confidences.get("khata_number_fallback"),
            )

        return schema