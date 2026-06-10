from __future__ import annotations

import random
import tkinter as tk

from tkinter import ttk, font, messagebox

from vocabulary_quiz_app.quiz_logic import Word, check_answer, draw_word, WrongNoteSession


class VocabularyQuizApp:
    def __init__(self, root: tk.Tk, words: list[Word]) -> None:
        self.words = words
        self.rng = random.Random()
        self.current: Word | None = None
        self.checked = False
        self.score = 0
        self.total = 0
        self.question_num = 0
        self.reverse = False
        self.wrong_mode = False  # 오답 노트 모드 여부
        self.wrong_note = WrongNoteSession()

        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="NanumGothic", size=12)

        root.title("Vocabulary Quiz")
        root.geometry("420x380")
        root.resizable(False, False)

        self.word_var = tk.StringVar(value="단어를 불러오는 중...")
        self.feedback_var = tk.StringVar(value="")
        self.score_var = tk.StringVar(value="Score: 0/0")
        self.hint_var = tk.StringVar(value="")
        self.progress_var = tk.StringVar(value="")
        self.mode_var = tk.StringVar(value="모드: 영어 → 한국어")
        self.wrong_count_var = tk.StringVar(value="오답 노트: 0개")
        self.hint_used = False

        ttk.Label(root, textvariable=self.progress_var, foreground="gray").pack(pady=(12, 0))
        ttk.Label(root, textvariable=self.mode_var, foreground="#4a90d9").pack(pady=(2, 0))
        ttk.Label(root, text="문제").pack(pady=(4, 2))
        ttk.Label(root, textvariable=self.word_var, font=("NanumGothic", 24)).pack()

        self.answer_entry = ttk.Entry(root, font=("NanumGothic", 14))
        self.answer_entry.pack(pady=12, ipadx=6, ipady=4)

        buttons = ttk.Frame(root)
        buttons.pack(pady=4)
        self.check_button = ttk.Button(buttons, text="채점", command=self.check_current)
        self.check_button.pack(side=tk.LEFT, padx=6)
        self.hint_button = ttk.Button(buttons, text="힌트", command=self.show_hint)
        self.hint_button.pack(side=tk.LEFT, padx=6)
        ttk.Button(buttons, text="다음", command=self.next_word).pack(side=tk.LEFT, padx=6)

        extra = ttk.Frame(root)
        extra.pack(pady=(4, 0))
        ttk.Button(extra, text="⇄ 출제 방향 전환", command=self.toggle_mode).pack(side=tk.LEFT, padx=6)
        self.wrong_button = ttk.Button(extra, text="📝 오답 노트", command=self.toggle_wrong_mode)
        self.wrong_button.pack(side=tk.LEFT, padx=6)

        ttk.Label(root, textvariable=self.wrong_count_var, foreground="#c0392b").pack(pady=(4, 0))
        ttk.Label(root, textvariable=self.hint_var, foreground="gray").pack()
        ttk.Label(root, textvariable=self.feedback_var).pack(pady=4)
        ttk.Label(root, textvariable=self.score_var).pack()

        self.next_word()

    def _active_words(self) -> list[Word]:
        return self.wrong_note.words if self.wrong_mode else self.words

    def toggle_mode(self) -> None:
        self.reverse = not self.reverse
        self.mode_var.set("모드: 한국어 → 영어" if self.reverse else "모드: 영어 → 한국어")
        self.next_word()

    def toggle_wrong_mode(self) -> None:
        if not self.wrong_mode:
            if self.wrong_note.count == 0:
                messagebox.showinfo("오답 노트", "아직 틀린 단어가 없어요!")
                return
            self.wrong_mode = True
            self.wrong_button.configure(text="📚 전체 단어로")
            self.score = 0
            self.total = 0
            self.question_num = 0
        else:
            self.wrong_mode = False
            self.wrong_button.configure(text="📝 오답 노트")
            self.score = 0
            self.total = 0
            self.question_num = 0
        self.next_word()

    def next_word(self) -> None:
        self.question_num += 1
        pool = self._active_words()
        self.current = draw_word(pool, self.rng)
        display = self.current.meaning if self.reverse else self.current.term
        self.word_var.set(display)
        self.answer_entry.delete(0, tk.END)
        self.feedback_var.set("")
        self.hint_var.set("")
        self.hint_used = False
        self.checked = False
        self.check_button.state(["!disabled"])
        self.hint_button.state(["!disabled"])
        label = "오답" if self.wrong_mode else "전체"
        self.progress_var.set(f"{self.question_num}번째 문제 / {label} {len(pool)}개")
        self.answer_entry.focus()

    def show_hint(self) -> None:
        if self.current is None or self.hint_used or self.checked:
            return
        self.hint_used = True
        answer = self.current.term if self.reverse else self.current.meaning
        first_char = answer[0]
        dashes = " _" * (len(answer) - 1)
        self.hint_var.set(f"힌트: {first_char}{dashes}")
        self.hint_button.state(["disabled"])

    def check_current(self) -> None:
        if self.current is None or self.checked:
            return
        self.checked = True
        self.total += 1
        user_input = self.answer_entry.get()
        if check_answer(self.current, user_input, reverse=self.reverse):
            self.score += 1
            self.feedback_var.set("정답입니다!")
            # 오답 노트 모드에서 맞히면 오답 노트에서 제거
            if self.wrong_mode:
                self.wrong_note.remove(self.current)
        else:
            answer = self.current.term if self.reverse else self.current.meaning
            self.feedback_var.set(f"오답입니다. 정답: {answer}")
            self.wrong_note.add(self.current)
        self.score_var.set(f"Score: {self.score}/{self.total}")
        self.wrong_count_var.set(f"오답 노트: {self.wrong_note.count}개")
        self.check_button.state(["disabled"])
        # 오답 노트 모드에서 단어를 다 맞히면 완료 안내
        if self.wrong_mode and self.wrong_note.count == 0:
            messagebox.showinfo("오답 노트", "오답 노트의 모든 단어를 맞혔어요! 🎉")
            self.toggle_wrong_mode()
