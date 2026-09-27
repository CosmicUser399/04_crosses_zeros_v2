"""Игровая модель «Крестики-нолики 5×5».

Не зависит от tkinter. Хранит состояние поля, применяет ходы,
определяет победу и ничью.
"""

from __future__ import annotations

from constants import BOARD_SIZE, EMPTY, WIN_LENGTH


_DIRECTIONS: tuple[tuple[int, int], ...] = (
    (0, 1),   # горизонталь
    (1, 0),   # вертикаль
    (1, 1),   # диагональ
    (1, -1),  # обратная диагональ
)


def find_winning_line(
    board: list[list[str]],
    row: int,
    col: int,
    player: str,
) -> list[tuple[int, int]] | None:
    """Найти победную линию player, проходящую через (row, col).

    Клетка (row, col) считается занятой символом player
    независимо от того, что реально записано в board — это
    позволяет проверять как реальные, так и гипотетические
    ходы без мутации доски.

    Возвращает список из WIN_LENGTH координат линии победы
    или None, если победы нет.
    """
    size = len(board)
    for dr, dc in _DIRECTIONS:
        cells = [(row, col)]
        # вперёд
        r, c = row + dr, col + dc
        while (
            0 <= r < size
            and 0 <= c < size
            and (board[r][c] == player or (r == row and c == col))
        ):
            if board[r][c] == player:
                cells.append((r, c))
            r += dr
            c += dc
        # назад
        r, c = row - dr, col - dc
        while (
            0 <= r < size
            and 0 <= c < size
            and (board[r][c] == player or (r == row and c == col))
        ):
            if board[r][c] == player:
                cells.append((r, c))
            r -= dr
            c -= dc
        if len(cells) >= WIN_LENGTH:
            # возвращаем окно WIN_LENGTH клеток, содержащее (row, col)
            # сортируем, чтобы выбрать подходящее окно
            cells.sort()
            idx = cells.index((row, col))
            for start in range(max(0, idx - WIN_LENGTH + 1),
                               min(len(cells) - WIN_LENGTH + 1,
                                   idx + 1)):
                window = cells[start:start + WIN_LENGTH]
                if (row, col) in window:
                    return window
    return None


class Game:
    """Игровая модель «Крестики-нолики 5×5».

    Хранит поле, применяет ходы, определяет победу и ничью.
    Не зависит от tkinter.
    """

    def __init__(self) -> None:
        """Инициализировать игру и сбросить поле."""
        self._board: list[list[str]] = []
        self._winner: str | None = None
        self._winning_cells: list[tuple[int, int]] = []
        self._game_over: bool = False
        self.reset()

    def reset(self) -> None:
        """Сбросить поле и все состояния для новой игры."""
        self._board = [
            [EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)
        ]
        self._winner = None
        self._winning_cells = []
        self._game_over = False

    def make_move(self, row: int, col: int, player: str) -> bool:
        """Применить ход player в клетку (row, col).

        Возвращает True, если ход успешно применён, иначе False.
        """
        if self._game_over:
            return False
        if not self.is_valid_move(row, col):
            return False
        self._board[row][col] = player
        winning = find_winning_line(self._board, row, col, player)
        if winning is not None:
            self._winner = player
            self._winning_cells = winning
            self._game_over = True
        elif self.is_draw():
            self._game_over = True
        return True

    def is_valid_move(self, row: int, col: int) -> bool:
        """Проверить, что (row, col) в границах и клетка пуста."""
        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
            return False
        return self._board[row][col] == EMPTY

    def check_winner(self, player: str) -> bool:
        """Вернуть True, если player выиграл."""
        return self._winner == player

    def is_draw(self) -> bool:
        """Вернуть True, если поле заполнено и победителя нет."""
        if self._winner is not None:
            return False
        return all(
            self._board[r][c] != EMPTY
            for r in range(BOARD_SIZE)
            for c in range(BOARD_SIZE)
        )

    def is_game_over(self) -> bool:
        """Вернуть True, если игра завершена."""
        return self._game_over

    def get_winner(self) -> str | None:
        """Вернуть победителя или None."""
        return self._winner

    def get_available_moves(self) -> list[tuple[int, int]]:
        """Вернуть список незанятых клеток."""
        return [
            (r, c)
            for r in range(BOARD_SIZE)
            for c in range(BOARD_SIZE)
            if self._board[r][c] == EMPTY
        ]

    def get_winning_cells(self) -> list[tuple[int, int]]:
        """Вернуть координаты клеток победной линии."""
        return list(self._winning_cells)

    def get_cell(self, row: int, col: int) -> str:
        """Вернуть содержимое клетки (row, col)."""
        return self._board[row][col]

    def get_board(self) -> list[list[str]]:
        """Вернуть глубокую копию поля."""
        return [list(row) for row in self._board]
