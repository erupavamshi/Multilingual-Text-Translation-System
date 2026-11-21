
from functools import lru_cache

from importlib import import_module

torch = import_module("torch")
transformers = import_module("transformers")
M2M100ForConditionalGeneration = transformers.M2M100ForConditionalGeneration
M2M100Tokenizer = transformers.M2M100Tokenizer

from translator import translate_text


MODEL_NAME = "facebook/m2m100_418M"

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

M2M100_LANGUAGES = {
    "Tamil": "ta",
    "Hindi": "hi"
}

COMPARISON_LANGUAGES = ["Tamil", "Hindi", "Telugu"]


@lru_cache(maxsize=1)
def load_m2m100():
    tokenizer = M2M100Tokenizer.from_pretrained(MODEL_NAME)

    model = M2M100ForConditionalGeneration.from_pretrained(
        MODEL_NAME
    )

    model.to(DEVICE)
    model.eval()

    return tokenizer, model


def translate_with_m2m100(text, target_language):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Please enter text to translate.")

    if target_language not in M2M100_LANGUAGES:
        raise ValueError(
            f"M2M100 comparison is not available for {target_language}."
        )

    tokenizer, model = load_m2m100()

    tokenizer.src_lang = "en"

    inputs = tokenizer(
        text.strip(),
        return_tensors="pt",
        truncation=True,
        max_length=512
    ).to(DEVICE)

    target_language_id = tokenizer.get_lang_id(
        M2M100_LANGUAGES[target_language]
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


def compare_models(text, target_language):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Please enter text to compare.")

    if target_language not in COMPARISON_LANGUAGES:
        raise ValueError("The selected language is not supported.")

    nllb_result = translate_text(
        text,
        "English",
        target_language
    )

    if target_language == "Telugu":
        return nllb_result, None

    m2m100_result = translate_with_m2m100(
        text,
        target_language
    )

    return nllb_result, m2m100_result
