import regex as re
from .extractor_master import RegexTextExtractor

class WestBengalEnglishRORV1(RegexTextExtractor):
    def __init__(self):
        super().__init__()
        self.document_id = "WB_EN_ROR_V1"
        self.language = "en"
        self.state = "west_bengal"
        self.FIELD_ALIASES = {

            "landowner_name": [
                "Name",
                "Occupier Name",
                "Landowner Name",
            ],

            "guardian_name": [
                "Father/Husband",
                "Father",
                "Husband",
            ],

            "landowner_address": [
                "Address",
            ],

            "district": [
                "District",
            ],

            "village": [
                "Village",
                "Mouza",
            ],

            "tehsil": [
                "Tehsil",
                "Thana",
            ],

            "khata_number": [
                "Khatian No",
                "Khatian Number",
                "Khata No",
                "Khata Number",
            ],

            "total_plots": [
                "Total Plots",
                "Total Khatian Count",
            ],

            "survey_number": [
                "Survey No",
                "Survey Number",
            ],

            "signed_by": [
                "Digitally signed by",
            ],
        }

        self.DOCUMENT_ANCHORS = [
            "Plot-wise Land Details",
            "Plot No.",
            "Land Class",
            "Occupier Share",
            "Share Area",
        ]

        

        self.total_area_pattern = re.compile(
            r"""
            Land\s*Area
            \s*
            (?:\(?(?:Dec|Decimal)\.?\)?)
            \s*[:\-]?\s*
            (?P<value>\d+(?:\.\d+)?)
            """,
            re.IGNORECASE | re.VERBOSE
        )

        self.ownership_pattern = re.compile(
            r"\b("
            r"Raiyat|"
            r"Bargadar|"
            r"Sikimi|"
            r"Under\s+Raiyat"
            r")\b",
            re.IGNORECASE
        )

        self.registration_pattern = re.compile(
            r"""
            Certified\s+to\s+be\s+true\s+copy
            .*?
            Act\s+1\s+of\s+1872
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

        self.mutation_pattern = re.compile(
            r"mutation",
            re.IGNORECASE
        )
        super().compile_patterns()
    def parse_plot_row(self, row):

        if len(row) < 6:
            return None

        plot_no = row[0]

        if not re.fullmatch(
            r"\d+(?:/\d+)?",
            plot_no
        ):
            return None

        return {
            "plot_no": plot_no,

            "land_class":
                row[1] or None,

            "remarks":
                row[2] or None,

            "total_plot_area":
                row[3] or None,

            "occupier_share":
                row[4] or None,

            "share_area":
                row[5] or None,
        }

    def extract_specialized(self, text, rows):

        out = super().extract_specialized(
            text,
            rows
        )

        m = self.total_area_pattern.search(text)

        out["total_land_area_dec"] = (
            m.group("value")
            if m else None
        )

        m = self.ownership_pattern.search(text)

        out["ownership_type"] = (
            m.group(1)
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

        out["mutation_records"] = (
            "found"
            if self.mutation_pattern.search(text)
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