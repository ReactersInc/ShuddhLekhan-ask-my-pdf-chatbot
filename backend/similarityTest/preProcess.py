from pathlib import Path
import nltk

def set_indic_resources(indic_resources_path: str | Path):
    try:
        from indicnlp import common
        common.set_resources_path(str(indic_resources_path))
    except Exception as e:
        print("Warning: could not set indic_nlp resources:", e)

def ensure_nltk_data():
    nltk.download("punkt", quiet=True)
    nltk.download("stopwords", quiet=True)

# English preprocessing
def preprocess_english(text: str, english_stopwords=None) -> str:
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords

    if english_stopwords is None:
        english_stopwords = set(stopwords.words("english"))

    tokens = word_tokenize(text)
    filtered = [tok.lower() for tok in tokens if tok.isalpha() and tok.lower() not in english_stopwords]
    return " ".join(filtered)

def preprocess_hindi(text: str, hindi_stopwords: set | None = None) -> str:
    try:
        from indicnlp.tokenize.indic_tokenize import trivial_tokenize
        tokens = trivial_tokenize(text)
    except Exception:
        tokens = text.split()

    punct_chars = set(".,।()[]{}—–-;:")

    if hindi_stopwords:
        filtered = [tok for tok in tokens if tok.strip() and not all(ch in punct_chars for ch in tok) and tok not in hindi_stopwords]
    else:
        filtered = [tok for tok in tokens if tok.strip() and not all(ch in punct_chars for ch in tok)]

    return " ".join(filtered)

def load_hindi_stopwords():
    try:
        from stopwords_hindi import hindi_sw
        sw = set(hindi_sw.get_hindi_sw() or [])
        return sw
    except Exception:
        try:
            import stopwordsiso as siso
            return set(siso.stopwords("hi"))
        except Exception:
            print("Warning: no Hindi stopwords package found. Continuing without Hindi stopwords.")
            return set()
