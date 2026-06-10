from __future__ import annotations

import random

from dataclasses import dataclass, field


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


@dataclass
class WrongNoteSession:
    """틀린 단어를 누적하고 오답 전용 출제를 관리한다."""
    _wrong: list[Word] = field(default_factory=list)

    def add(self, word: Word) -> None:
        if word not in self._wrong:
            self._wrong.append(word)

    def remove(self, word: Word) -> None:
        if word in self._wrong:
            self._wrong.remove(word)

    @property
    def words(self) -> list[Word]:
        return list(self._wrong)

    @property
    def count(self) -> int:
        return len(self._wrong)

    def draw(self, rng: random.Random | None = None) -> Word:
        return draw_word(self._wrong, rng)

    def clear(self) -> None:
        self._wrong.clear()
