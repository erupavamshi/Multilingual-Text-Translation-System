
from importlib import import_module

try:
    _langdetect = import_module("langdetect")
    detect = _langdetect.detect
    LangDetectException = _langdetect.LangDetectException
except ImportError:
    detect = None
    LangDetectException = Exception


SUPPORTED_LANGUAGES = {
    "en": "English",
    "ta": "Tamil",
    "hi": "Hindi",
    "te": "Telugu",
    "ml": "Malayalam",
    "fr": "French",
    "es": "Spanish",
    "de": "German",
    "ar": "Arabic",
    "zh-cn": "Chinese",
    "zh-tw": "Chinese"
}


def detect_language(text):
    if not isinstance(text, str) or not text.strip():
        return "Unable to detect language"

    text = text.strip()

    if len(text.split()) < 3:
        return "Text too short"

    if detect is None:
        return "Language detection unavailable; install the 'langdetect' package"

    try:
        language_code = detect(text)
        language_name = SUPPORTED_LANGUAGES.get(language_code)

        if language_name:
            return language_name

        return "Unsupported language"

    except LangDetectException:
        return "Unable to detect language"
