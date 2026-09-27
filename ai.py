"""Эвристический ИИ для игры «Крестики-нолики 5×5».

Не зависит от tkinter. Детерминирован: не использует random.
"""

from __future__ import annotations

from constants import (
    BOARD_SIZE,
    EMPTY,
    PLAYER_O,
    PLAYER_X,
    WIN_LENGTH,
)
from game import Game, _DIRECTIONS, find_winning_line


def _would_win(
    board: list[list[str]],
    row: int,
    col: int,
    player: str,
) -> bool:
    """Вернуть True, если ход player в (row, col) приведёт к победе.

    Использует find_winning_line без мутации доски.
    """
    return find_winning_line(board, row, col, player) is not None


def _score_move(
    board: list[list[str]],
    row: int,
    col: int,
) -> int:
    """Вычислить эвристическую оценку хода O в (row, col).

    Веса:
    - центр поля:                        +10
    - «живая» линия с уже стоящим O:     +6 за каждую линию
    - «живая» пустая линия:              +3 за каждую линию
    - угловая клетка:                    +3
    - прочие клетки:                     +1 (база)
    """
    size = len(board)
    score = 1  # база

    # центр
    center = BOARD_SIZE // 2
    if row == center and col == center:
        score += 10

    # угол
    if row in (0, size - 1) and col in (0, size - 1):
        score += 3

    # «живые» линии через (row, col)
    for dr, dc in _DIRECTIONS:
        for start in _windows(row, col, dr, dc, size):
            cells_in_window = [
                board[r][c]
                for r, c in start
                if not (r == row and c == col)
            ]
            if PLAYER_X in cells_in_window:
                continue  # линия заблокирована X
            o_count = cells_in_window.count(PLAYER_O)
            if o_count > 0:
                score += 6
            else:
                score += 3

    return score


def _windows(
    row: int,
    col: int,
    dr: int,
    dc: int,
    size: int,
) -> list[list[tuple[int, int]]]:
    """Вернуть окна длины WIN_LENGTH в направлении (dr,dc).

    Каждое окно — список клеток, содержащий (row, col).
    """
    # Собираем все клетки в данном направлении
    # (одна прямая, проходящая через (row, col))
    all_cells: list[tuple[int, int]] = []
    # идём назад от (row, col)
    r, c = row, col
    while 0 <= r < size and 0 <= c < size:
        all_cells.append((r, c))
        r -= dr
        c -= dc
    all_cells.reverse()
    # продолжаем вперёд
    r, c = row + dr, col + dc
    while 0 <= r < size and 0 <= c < size:
        all_cells.append((r, c))
        r += dr
        c += dc

    idx = all_cells.index((row, col))
    result = []
    for start in range(max(0, idx - WIN_LENGTH + 1),
                       min(len(all_cells) - WIN_LENGTH + 1, idx + 1)):
        result.append(all_cells[start:start + WIN_LENGTH])
    return result


class AI:
    """Эвристический ИИ, играющий за PLAYER_O.

    Не зависит от tkinter. Детерминирован: не использует random.
    """

    def get_move(self, game: Game) -> tuple[int, int]:
        """Выбрать и вернуть ход для PLAYER_O.

        Алгоритм:
        1. Если есть победный ход — сделать его.
        2. Если есть ход, блокирующий победу X — сделать его.
        3. Иначе — выбрать ход с максимальным score.

        При равных score выбирается первый по (row, col) —
        детерминизм гарантируется сортировкой и строгим `>`.
        """
        moves = sorted(game.get_available_moves())
        if not moves:
            raise ValueError("Нет доступных ходов для ИИ")

        board = game.get_board()

        for row, col in moves:          # шаг 1: победный ход
            if _would_win(board, row, col, PLAYER_O):
                return row, col

        for row, col in moves:          # шаг 2: блокировка
            if _would_win(board, row, col, PLAYER_X):
                return row, col

        best_move = moves[0]            # шаг 3: максимизация score
        best_score = -1
        for row, col in moves:
            s = _score_move(board, row, col)
            if s > best_score:
                best_score = s
                best_move = row, col
        return best_move
