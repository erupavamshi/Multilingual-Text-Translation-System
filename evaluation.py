
from collections import Counter
import math


def _sentence_bleu(reference, translated):
    reference_tokens = reference.split()
    translated_tokens = translated.split()
    precisions = []
    smooth = 1

    for order in range(1, 5):
        reference_ngrams = Counter(
            tuple(reference_tokens[i:i + order])
            for i in range(len(reference_tokens) - order + 1)
        )
        translated_ngrams = Counter(
            tuple(translated_tokens[i:i + order])
            for i in range(len(translated_tokens) - order + 1)
        )
        total = sum(translated_ngrams.values())
        matches = sum(
            min(count, reference_ngrams[ngram])
            for ngram, count in translated_ngrams.items()
        )

        if total == 0:
            precisions.append(0)
        elif matches == 0:
            smooth *= 2
            precisions.append(1 / (smooth * total))
        else:
            precisions.append(matches / total)

    if not translated_tokens or any(precision == 0 for precision in precisions):
        return 0

    brevity_penalty = min(
        1, math.exp(1 - len(reference_tokens) / len(translated_tokens))
    )
    return 100 * brevity_penalty * math.exp(
        sum(math.log(precision) for precision in precisions) / 4
    )


def calculate_bleu(reference, translated):
    if not isinstance(reference, str) or not isinstance(translated, str):
        raise TypeError("Reference and translated text must be strings.")

    reference = reference.strip()
    translated = translated.strip()

    if not reference or not translated:
        raise ValueError("Both reference and translated text are required.")

    return round(_sentence_bleu(reference, translated), 2)
