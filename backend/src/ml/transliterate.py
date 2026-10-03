import ctranslate2


class Transliterator:
    def __init__(self, base_dir="indicxlit_indic2en_ct2"):
        self.translator = ctranslate2.Translator(base_dir, device="cpu", compute_type="int8")
    @staticmethod
    def transliterate_digit(text:str,denorm_digit):
        if (not text) or (not denorm_digit):
            return text
        return text.translate(denorm_digit)
    @staticmethod
    def transliterate_land_class(text:str,land_class:dict[str,str]):
        if (not text) or (not land_class):
            return text
        return land_class[text]
    def transliterate(self, text: str, src_lang: str="bn", beam_size: int = 5)->list[str]:
        if not text:
            return text
        output = " ".join([self.word_transliterate(word)[0] for word in text.split()])
        return output
    def word_transliterate(self, word: str, src_lang: str="bn", beam_size: int = 5) -> list[str]:
        if not word.strip():
            return []
        char_tokens = self._tokenize(word)
        src_prefix = f"__{src_lang}__"
        
        
        input_sequence = [src_prefix] + char_tokens
        results = self.translator.translate_batch(
            [input_sequence], 
            beam_size=beam_size
        )
 
        predictions = []
        for hypothesis in results[0].hypotheses:
            clean_tokens = [t for t in hypothesis if t not in (src_prefix, "</s>", "<s>")]
            predictions.append(self._detokenize(clean_tokens))
            
        return predictions

            
    def _tokenize(self, text):
        return list(text.strip())

    def _detokenize(self, tokens):
        return "".join(tokens).replace(" ", " ").strip()