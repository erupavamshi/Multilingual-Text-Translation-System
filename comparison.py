
from functools import lru_cache

import torch
from transformers import (
    M2M100ForConditionalGeneration,
    M2M100Tokenizer
)

from translator import translate_text, LANGUAGES


MODEL_NAME = "facebook/m2m100_418M"

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

M2M100_LANGUAGES = {
    "English": "en",
    "Tamil": "ta",
    "Hindi": "hi",
    "Telugu": "te",
    "Malayalam": "ml",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Arabic": "ar",
    "Chinese": "zh"
}

COMPARISON_LANGUAGES = list(LANGUAGES.keys())


@lru_cache(maxsize=1)
def load_m2m100():
    tokenizer = M2M100Tokenizer.from_pretrained(MODEL_NAME)

    model = M2M100ForConditionalGeneration.from_pretrained(
        MODEL_NAME
    )

    model.to(DEVICE)
    model.eval()

    return tokenizer, model


def translate_with_m2m100(text, source_language, target_language):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Please enter some text to translate.")

    if source_language not in M2M100_LANGUAGES:
        raise ValueError(
            f"M2M100 does not have a configured code for {source_language}."
        )

    if target_language not in M2M100_LANGUAGES:
        raise ValueError(
            f"M2M100 does not have a configured code for {target_language}."
        )

    if source_language == target_language:
        raise ValueError("Please select two different languages.")

    tokenizer, model = load_m2m100()

    source_code = M2M100_LANGUAGES[source_language]
    target_code = M2M100_LANGUAGES[target_language]

    if source_code not in tokenizer.lang_code_to_id:
        raise ValueError(
            f"M2M100 tokenizer does not support {source_language}."
        )

    if target_code not in tokenizer.lang_code_to_id:
        raise ValueError(
            f"M2M100 tokenizer does not support {target_language}."
        )

    tokenizer.src_lang = source_code

    inputs = tokenizer(
        text.strip(),
        return_tensors="pt",
        truncation=True,
        max_length=512
    ).to(DEVICE)

    target_language_id = tokenizer.get_lang_id(target_code)

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


def compare_models(text, source_language, target_language=None):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Please enter some text to compare.")

    # Keep compatibility with the previous English-to-target function call.
    if target_language is None:
        target_language = source_language
        source_language = "English"

    if source_language not in COMPARISON_LANGUAGES:
        raise ValueError("The selected source language is not supported.")

    if target_language not in COMPARISON_LANGUAGES:
        raise ValueError("The selected target language is not supported.")

    if source_language == target_language:
        raise ValueError("Please select two different languages.")

    nllb_result = translate_text(
        text,
        source_language,
        target_language
    )

    m2m100_result = translate_with_m2m100(
        text,
        source_language,
        target_language
    )

    return nllb_result, m2m100_result
