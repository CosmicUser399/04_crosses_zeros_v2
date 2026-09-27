"""Tkinter-интерфейс игры «Крестики-нолики 5×5».

Не определяет победителя — все решения запрашивает у Game и AI.
"""

from __future__ import annotations

import logging
import tkinter as tk
from tkinter import ttk

from ai import AI
from constants import (
    AI_MOVE_DELAY_MS,
    BOARD_SIZE,
    CELL_FONT,
    DEFAULT_DIFFICULTY,
    DIFFICULTY_NAMES,
    DIFFICULTY_ORDER,
    PLAYER_O,
    PLAYER_O_NAME,
    PLAYER_X,
    PLAYER_X_NAME,
)
from game import Game


_logger = logging.getLogger(__name__)

_COLOR_DEFAULT = "SystemButtonFace"
_COLOR_WIN = "#FFD700"
_COLOR_X = "#2196F3"
_COLOR_O = "#F44336"

# Обратное отображение «русское название → код уровня»
_NAME_TO_DIFFICULTY = {v: k for k, v in DIFFICULTY_NAMES.items()}


class TicTacToeApp:
    """Tkinter-интерфейс игры. Не определяет победителя сам —
    все решения запрашивает у Game и AI.
    """

    def __init__(self, root: tk.Tk) -> None:
        """Инициализировать приложение и построить UI."""
        self._root = root
        self._game = Game()
        self._active_difficulty: str = DEFAULT_DIFFICULTY
        self._ai = AI(difficulty=self._active_difficulty)
        self.ai_thinking: bool = False
        self._buttons: list[list[tk.Button]] = []
        self._status_var = tk.StringVar()
        self._active_diff_var = tk.StringVar()
        self._build_ui()
        self._update_status()
        self._update_active_difficulty_label()

    def _build_ui(self) -> None:
        """Построить виджеты окна."""
        # Статус-лейбл
        status_label = ttk.Label(
            self._root,
            textvariable=self._status_var,
            font=("Arial", 14),
            anchor="center",
        )
        status_label.pack(fill=tk.X, padx=20, pady=(20, 10))

        # Строка выбора сложности
        diff_frame = ttk.Frame(self._root)
        diff_frame.pack(padx=20, pady=(0, 6))

        ttk.Label(
            diff_frame,
            text="Уровень сложности:",
            font=("Arial", 11),
        ).pack(side=tk.LEFT, padx=(0, 8))

        difficulty_names = [
            DIFFICULTY_NAMES[d] for d in DIFFICULTY_ORDER
        ]
        self._diff_combo = ttk.Combobox(
            diff_frame,
            values=difficulty_names,
            state="readonly",
            width=10,
            font=("Arial", 11),
        )
        self._diff_combo.set(DIFFICULTY_NAMES[DEFAULT_DIFFICULTY])
        self._diff_combo.pack(side=tk.LEFT)

        # Сетка игровых клеток
        grid_frame = ttk.Frame(self._root)
        grid_frame.pack(padx=20, pady=10)

        for r in range(BOARD_SIZE):
            row_buttons: list[tk.Button] = []
            for c in range(BOARD_SIZE):
                btn = tk.Button(
                    grid_frame,
                    text="",
                    font=CELL_FONT,
                    width=3,
                    height=1,
                    relief=tk.RAISED,
                    command=lambda row=r, col=c: self.on_cell_clicked(
                        row, col
                    ),
                )
                btn.grid(row=r, column=c, padx=2, pady=2)
                row_buttons.append(btn)
            self._buttons.append(row_buttons)

        # Нижняя панель: кнопка «Новая игра» + label активной сложности
        bottom_frame = ttk.Frame(self._root)
        bottom_frame.pack(pady=20)

        new_game_btn = ttk.Button(
            bottom_frame,
            text="Новая игра",
            command=self.on_new_game_clicked,
        )
        new_game_btn.pack(side=tk.LEFT, padx=(0, 16))

        ttk.Label(
            bottom_frame,
            textvariable=self._active_diff_var,
            font=("Arial", 11),
            foreground="#555555",
        ).pack(side=tk.LEFT)

    # ------------------------------------------------------------------
    # Обработчики событий
    # ------------------------------------------------------------------

    def on_cell_clicked(self, row: int, col: int) -> None:
        """Обработать клик игрока по клетке (row, col)."""
        if self.ai_thinking or self._game.is_game_over():
            _logger.debug(
                "Клик (%d, %d) проигнорирован: ai_thinking=%s, "
                "game_over=%s",
                row, col, self.ai_thinking, self._game.is_game_over(),
            )
            return

        if not self._game.make_move(row, col, PLAYER_X):
            _logger.debug("Недопустимый ход (%d, %d)", row, col)
            return

        self._refresh_board()

        if self._game.is_game_over():
            self._update_status()
            self._highlight_winning_cells()
            return

        self.ai_thinking = True
        self._update_status()
        self._root.after(AI_MOVE_DELAY_MS, self._make_ai_move)

    def _make_ai_move(self) -> None:
        """Выполнить ход ИИ (вызывается через root.after)."""
        row, col = self._ai.get_move(self._game)
        _logger.info("ИИ выбрал ход (%d, %d)", row, col)
        self._game.make_move(row, col, PLAYER_O)
        self._refresh_board()

        if self._game.is_game_over():
            self._update_status()
            self._highlight_winning_cells()

        self.ai_thinking = False
        if not self._game.is_game_over():
            self._update_status()

    def on_new_game_clicked(self) -> None:
        """Применить выбранную сложность, сбросить игру и очистить UI."""
        selected_name = self._diff_combo.get()
        difficulty = _NAME_TO_DIFFICULTY.get(
            selected_name, DEFAULT_DIFFICULTY
        )
        self._active_difficulty = difficulty
        self._ai = AI(difficulty=difficulty)
        self._update_active_difficulty_label()

        self._game.reset()
        self.ai_thinking = False
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                self._buttons[r][c].configure(
                    text="",
                    bg=_COLOR_DEFAULT,
                    fg="black",
                )
        self._update_status()

    # ------------------------------------------------------------------
    # Вспомогательные методы UI
    # ------------------------------------------------------------------

    def _refresh_board(self) -> None:
        """Обновить текст и цвет всех кнопок по состоянию игры."""
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                value = self._game.get_cell(r, c)
                btn = self._buttons[r][c]
                if value == PLAYER_X:
                    btn.configure(text=PLAYER_X, fg=_COLOR_X)
                elif value == PLAYER_O:
                    btn.configure(text=PLAYER_O, fg=_COLOR_O)
                else:
                    btn.configure(text="", fg="black")

    def _highlight_winning_cells(self) -> None:
        """Подсветить клетки победной линии."""
        for r, c in self._game.get_winning_cells():
            self._buttons[r][c].configure(bg=_COLOR_WIN)

    def _update_status(self) -> None:
        """Обновить текст статус-лейбла."""
        if self._game.get_winner() == PLAYER_X:
            self._status_var.set("Вы победили!")
        elif self._game.get_winner() == PLAYER_O:
            self._status_var.set(f"{PLAYER_O_NAME} победил!")
        elif self._game.is_draw():
            self._status_var.set("Ничья!")
        elif self.ai_thinking:
            self._status_var.set("Ход компьютера...")
        else:
            self._status_var.set(f"Ваш ход, {PLAYER_X_NAME}")

    def _update_active_difficulty_label(self) -> None:
        """Обновить label с текущей активной сложностью."""
        name = DIFFICULTY_NAMES.get(self._active_difficulty, "")
        self._active_diff_var.set(f"Сложность: {name}")
