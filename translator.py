
import torch  # type: ignore[import-not-found]
from functools import lru_cache
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM  # type: ignore[import-not-found]


MODEL_NAME = "facebook/nllb-200-distilled-600M"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

LANGUAGES = {
    "English": "eng_Latn",
    "Tamil": "tam_Taml",
    "Hindi": "hin_Deva",
    "Telugu": "tel_Telu",
    "Malayalam": "mal_Mlym",
    "French": "fra_Latn",
    "Spanish": "spa_Latn",
    "German": "deu_Latn",
    "Arabic": "arb_Arab",
    "Chinese": "zho_Hans"
}


@lru_cache(maxsize=1)
def load_translation_model():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

    model.to(DEVICE)
    model.eval()

    return tokenizer, model


def translate_text(text, source_language, target_language):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Please enter some text to translate.")

    if source_language not in LANGUAGES:
        raise ValueError("The selected source language is not supported.")

    if target_language not in LANGUAGES:
        raise ValueError("The selected target language is not supported.")

    if source_language == target_language:
        raise ValueError("Please select two different languages.")

    tokenizer, model = load_translation_model()

    tokenizer.src_lang = LANGUAGES[source_language]

    inputs = tokenizer(
        text.strip(),
        return_tensors="pt",
        truncation=True,
        max_length=512
    ).to(DEVICE)

    target_language_id = tokenizer.convert_tokens_to_ids(
        LANGUAGES[target_language]
    )

    with torch.no_grad():
        output_tokens = model.generate(
            **inputs,
            forced_bos_token_id=target_language_id,
            max_length=512,
            num_beams=4
        )

    translated_text = tokenizer.batch_decode(
        output_tokens,
        skip_special_tokens=True
    )

    return translated_text[0]
