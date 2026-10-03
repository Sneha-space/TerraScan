from collections import defaultdict
import unicodedata


class ScriptDetector:
    LANGUAGE_MAP = {
        "english":"en",
        "bengali": "bn",
        "assamese": "as",
        "devanagari": "hi",
        "tamil": "ta",
        "telugu": "te",
        "kannada": "kn",
        "malayalam": "ml",
        "oriya": "or",
        "gujarati": "gu",
        "gurmukhi": "pa",
        "sinhala": "si",
    }

    SCRIPT_RANGES = {
        "english": [
            (0x0041, 0x005A),   # A-Z
            (0x0061, 0x007A),   # a-z
        ],

        "devanagari": [
            (0x0900, 0x097F),
        ],

        "bengali": [
            (0x0980, 0x09FF),
        ],

        "gurmukhi": [
            (0x0A00, 0x0A7F),
        ],

        "gujarati": [
            (0x0A80, 0x0AFF),
        ],

        "oriya": [
            (0x0B00, 0x0B7F),
        ],

        "tamil": [
            (0x0B80, 0x0BFF),
        ],

        "telugu": [
            (0x0C00, 0x0C7F),
        ],

        "kannada": [
            (0x0C80, 0x0CFF),
        ],

        "malayalam": [
            (0x0D00, 0x0D7F),
        ],
    }

    LANGUAGE_HINTS = {
        "devanagari": {
            "hindi": [
                "जिला",
                "तहसील",
                "खसरा",
                "खाता",
                "गांव",
                "गाँव",
                "भूमि",
                "नाम",
                "पिता",
                "पति",
            ],
            "marathi": [
                "जिल्हा",
                "तालुका",
                "गाव",
                "गट",
                "सर्वे",
                "मालक",
                "खाते",
                "जमीन",
            ],
        },

        "bengali": {
            "bengali": [
                "জেলা",
                "মৌজা",
                "খতিয়ান",
                "খতিয়ান",
                "দাগ",
                "জমি",
                "নাম",
                "ঠিকানা",
                "পিতা",
            ],
        },

        "oriya": {
            "odia": [
                "ଜିଲ୍ଲା",
                "ତହସିଲ",
                "ମୌଜା",
                "ଖତିଆନ",
                "ଜମି",
                "ନାମ",
            ],
        },

        "tamil": {
            "tamil": [
                "மாவட்டம்",
                "வட்டம்",
                "கிராமம்",
                "நிலம்",
                "பெயர்",
                "முகவரி",
            ],
        },

        "telugu": {
            "telugu": [
                "జిల్లా",
                "మండలం",
                "గ్రామం",
                "భూమి",
                "పేరు",
                "చిరునామా",
            ],
        },

        "kannada": {
            "kannada": [
                "ಜಿಲ್ಲೆ",
                "ತಾಲೂಕು",
                "ಗ್ರಾಮ",
                "ಭೂಮಿ",
                "ಹೆಸರು",
                "ವಿಳಾಸ",
            ],
        },

        "malayalam": {
            "malayalam": [
                "ജില്ല",
                "താലൂക്ക്",
                "ഗ്രാമം",
                "ഭൂമി",
                "പേര്",
                "വിലാസം",
            ],
        },

        "gurmukhi": {
            "punjabi": [
                "ਜ਼ਿਲ੍ਹਾ",
                "ਤਹਿਸੀਲ",
                "ਪਿੰਡ",
                "ਜ਼ਮੀਨ",
                "ਨਾਮ",
                "ਪਤਾ",
            ],
        },

        "gujarati": {
            "gujarati": [
                "જિલ્લો",
                "તાલુકો",
                "ગામ",
                "જમીન",
                "નામ",
                "સરનામું",
            ],
        },
    }

    def __init__(self):
        self.compiled_ranges = self._compile_ranges()

    def _compile_ranges(self):
        return {
            script: ranges
            for script, ranges in self.SCRIPT_RANGES.items()
        }

    @staticmethod
    def _in_range(codepoint, start, end):
        return start <= codepoint <= end

    def _detect_script_char(self, char):
        """
        Return the script associated with a single character.
        """
        codepoint = ord(char)

        for script, ranges in self.compiled_ranges.items():
            for start, end in ranges:
                if self._in_range(codepoint, start, end):
                    return script

        return None

    def _get_script_counts(self, text):
        """
        Count only meaningful alphabetic/script characters.

        Numbers, whitespace and punctuation are ignored.
        """
        counts = defaultdict(int)

        for char in text:
            script = self._detect_script_char(char)

            if script is not None:
                counts[script] += 1

        return dict(counts)

    def _detect_languages(self, text, script_counts):
        """
        Determine likely languages using script-specific vocabulary.

        This is intentionally a heuristic. Unicode alone cannot distinguish
        languages sharing the same script.
        """
        languages = []

        for script, count in script_counts.items():

            if script == "english":
                if count > 0:
                    languages.append("english")
                continue

            hints = self.LANGUAGE_HINTS.get(script, {})

            if not hints:
                languages.append(script)
                continue

            best_language = None
            best_score = 0

            for language, keywords in hints.items():
                score = 0

                for keyword in keywords:
                    if keyword in text:
                        score += 1

                if score > best_score:
                    best_score = score
                    best_language = language

            if best_language is not None:
                languages.append(best_language)
            else:
                # We know the script but cannot confidently identify
                # the exact language.
                languages.append(script)

        return languages
    
    def detect(self,text: str) -> str:
        if text is None or not isinstance(text,str):
            return None
        counts = { self.LANGUAGE_MAP[language]: 0 for language in self.SCRIPT_RANGES } 
        for char in text:
            script = self._detect_script_char(char)
            try:
                counts[self.LANGUAGE_MAP[script]] += 1 
            except:
                continue
            break
        if not any(counts.values()): 
            return None
        return max(counts, key=counts.get)
        

    def process(self, text):
        """
        Returns:
        {
            "languages": [...],
            "scripts": [...],
            "primary_language": "...",
            "primary_script": "...",
            "is_multilingual": True/False,
            "script_counts": {...},
            "language_confidence": {...}
        }
        """

        if not isinstance(text, str):
            raise TypeError("text must be a string")
        utf8_text = text.encode("utf-8").decode("utf-8")
        utf8_text = unicodedata.normalize("NFC", utf8_text)

        script_counts = self._get_script_counts(utf8_text)

        total_script_chars = sum(script_counts.values())

        if total_script_chars == 0:
            return {
                "languages": [],
                "scripts": [],
                "primary_language": None,
                "primary_script": None,
                "is_multilingual": False,
                "script_counts": {},
                "language_confidence": {},
            }
        sorted_scripts = sorted(
            script_counts.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        scripts = [script for script, _ in sorted_scripts]

        languages = self._detect_languages(
            utf8_text,
            script_counts,
        )

        languages = list(dict.fromkeys(languages))

        script_confidence = {
            script: round(count / total_script_chars, 4)
            for script, count in script_counts.items()
        }

        primary_script = sorted_scripts[0][0]

        primary_language = None

        primary_language_candidates = self._detect_languages(
            utf8_text,
            {primary_script: script_counts[primary_script]},
        )

        if primary_language_candidates:
            primary_language = primary_language_candidates[0]

        return {
            "languages": languages,
            "scripts": scripts,
            "primary_language": primary_language,
            "primary_script": primary_script,
            "is_multilingual": len(languages) > 1,
            "script_counts": script_counts,
            "language_confidence": script_confidence,
        }