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


class TicTacToeApp:
    """Tkinter-интерфейс игры. Не определяет победителя сам —
    все решения запрашивает у Game и AI.
    """

    def __init__(self, root: tk.Tk) -> None:
        """Инициализировать приложение и построить UI."""
        self._root = root
        self._game = Game()
        self._ai = AI()
        self.ai_thinking: bool = False
        self._buttons: list[list[tk.Button]] = []
        self._status_var = tk.StringVar()
        self._build_ui()
        self._update_status()

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

        # Кнопка «Новая игра»
        new_game_btn = ttk.Button(
            self._root,
            text="Новая игра",
            command=self.on_new_game_clicked,
        )
        new_game_btn.pack(pady=20)

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
        """Сбросить игру и очистить UI."""
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
