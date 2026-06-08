from __future__ import annotations

import random

from dataclasses import dataclass


@dataclass(frozen=True)
class Word:
    term: str
    meaning: str


def normalize_answer(text: str) -> str:
    return " ".join(text.strip().lower().split())


def check_answer(word: Word, user_input: str, reverse: bool = False) -> bool:
    expected = word.term if reverse else word.meaning
    return normalize_answer(user_input) == normalize_answer(expected)


def draw_word(words: list[Word], rng: random.Random | None = None) -> Word:
    if not words:
        raise ValueError("Word list is empty")
    chooser = rng if rng is not None else random
    return chooser.choice(words)
