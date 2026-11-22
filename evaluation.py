from sacrebleu import sentence_bleu


def calculate_bleu(reference, translated):
    if not isinstance(reference, str) or not isinstance(translated, str):
        raise TypeError("Reference and translated text must be strings.")

    reference = reference.strip()
    translated = translated.strip()

    if not reference or not translated:
        raise ValueError("Both reference and translated text are required.")

    score = sentence_bleu(
        translated,
        [reference],
        smooth_method="exp",
        use_effective_order=True
    )

    return round(score.score, 2)