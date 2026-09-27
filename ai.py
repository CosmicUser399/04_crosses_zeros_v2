"""Эвристический ИИ для игры «Крестики-нолики 5×5».

Не зависит от tkinter. Детерминирован: не использует random.
"""

from __future__ import annotations

from constants import (
    BOARD_SIZE,
    DEFAULT_DIFFICULTY,
    DIFFICULTY_EASY,
    DIFFICULTY_HARD,
    EMPTY,
    PLAYER_O,
    PLAYER_X,
    WIN_LENGTH,
)
from game import Game, _DIRECTIONS, find_winning_line


# ------------------------------------------------------------------
# Весовые схемы для _score_move
# ------------------------------------------------------------------

_DEFAULT_WEIGHTS: dict[str, int] = {
    "base": 1,
    "center": 10,
    "corner": 3,
    "own_line": 6,
    "empty_line": 3,
}

_EASY_WEIGHTS: dict[str, int] = {
    "base": 1,
    "center": 0,
    "corner": 1,
    "own_line": 0,
    "empty_line": 1,
}

# ------------------------------------------------------------------
# Константы поиска (Hard)
# ------------------------------------------------------------------

_HARD_SEARCH_DEPTH = 2
_HARD_TOP_LEVEL_CANDIDATES = 10
_HARD_NODE_CANDIDATES = 6
_WIN_SCORE = 100_000


# ------------------------------------------------------------------
# Вспомогательные функции
# ------------------------------------------------------------------

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
    player: str = PLAYER_O,
    weights: dict[str, int] | None = None,
) -> int:
    """Эвристическая оценка хода player в (row, col).

    Веса задаются словарём weights (по умолчанию _DEFAULT_WEIGHTS).
    Ключи: 'base', 'center', 'corner', 'own_line', 'empty_line'.
    """
    if weights is None:
        weights = _DEFAULT_WEIGHTS
    opponent = PLAYER_X if player == PLAYER_O else PLAYER_O

    size = len(board)
    score = weights["base"]

    # центр
    center = BOARD_SIZE // 2
    if row == center and col == center:
        score += weights["center"]

    # угол
    if row in (0, size - 1) and col in (0, size - 1):
        score += weights["corner"]

    # «живые» линии через (row, col)
    for dr, dc in _DIRECTIONS:
        for window in _windows(row, col, dr, dc, size):
            cells_in_window = [
                board[r][c]
                for r, c in window
                if not (r == row and c == col)
            ]
            if opponent in cells_in_window:
                continue  # линия заблокирована соперником
            own_count = cells_in_window.count(player)
            if own_count > 0:
                score += weights["own_line"]
            else:
                score += weights["empty_line"]

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
    all_cells: list[tuple[int, int]] = []
    r, c = row, col
    while 0 <= r < size and 0 <= c < size:
        all_cells.append((r, c))
        r -= dr
        c -= dc
    all_cells.reverse()
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


# ------------------------------------------------------------------
# Алгоритмы по уровням сложности
# ------------------------------------------------------------------

def _get_move_medium(
    board: list[list[str]],
    moves: list[tuple[int, int]],
) -> tuple[int, int]:
    """Средний уровень: победа → блок → наилучший score.

    Поведение идентично исходному AI.get_move.
    """
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


def _get_move_easy(
    board: list[list[str]],
    moves: list[tuple[int, int]],
) -> tuple[int, int]:
    """Простой уровень: победа — да, блокировка — нет.

    Оценка ходов выполняется по ослабленным весам
    (без бонуса за центр и «живые» линии).
    """
    for row, col in moves:
        if _would_win(board, row, col, PLAYER_O):
            return row, col

    # блокировка сознательно не выполняется
    best_move = moves[0]
    best_score = -1
    for row, col in moves:
        s = _score_move(board, row, col, PLAYER_O, _EASY_WEIGHTS)
        if s > best_score:
            best_score = s
            best_move = row, col
    return best_move


def _top_candidates(
    board: list[list[str]],
    moves: list[tuple[int, int]],
    player: str,
    limit: int,
) -> list[tuple[int, int]]:
    """Топ-N ходов player по _score_move.

    Сортировка стабильна и детерминирована: (-score, row, col).
    """
    scored = [
        (_score_move(board, r, c, player), r, c)
        for r, c in moves
    ]
    scored.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [(r, c) for _, r, c in scored[:limit]]


def _evaluate_board(
    board: list[list[str]],
    moves: list[tuple[int, int]],
) -> int:
    """Позиционная оценка: потенциал O минус X по свободным клеткам.

    Переиспользует _score_move.
    """
    return sum(
        _score_move(board, r, c, PLAYER_O)
        - _score_move(board, r, c, PLAYER_X)
        for r, c in moves
    )


def _minimax(
    board: list[list[str]],
    moves: list[tuple[int, int]],
    depth: int,
    maximizing: bool,
    alpha: int,
    beta: int,
) -> int:
    """Оценка позиции с alpha-beta pruning.

    maximizing=True — ход O (максимизирует), False — ход X.
    """
    if depth == 0 or not moves:
        return _evaluate_board(board, moves)

    player = PLAYER_O if maximizing else PLAYER_X
    candidates = _top_candidates(
        board, moves, player, _HARD_NODE_CANDIDATES
    )
    best = -_WIN_SCORE - 1 if maximizing else _WIN_SCORE + 1

    for row, col in candidates:
        board[row][col] = player
        remaining = [m for m in moves if m != (row, col)]
        if find_winning_line(board, row, col, player) is not None:
            value = _WIN_SCORE if maximizing else -_WIN_SCORE
        else:
            value = _minimax(
                board, remaining, depth - 1, not maximizing,
                alpha, beta,
            )
        board[row][col] = EMPTY

        if maximizing:
            if value > best:
                best = value
            alpha = max(alpha, best)
        else:
            if value < best:
                best = value
            beta = min(beta, best)
        if alpha >= beta:
            break
    return best


def _get_move_hard(
    board: list[list[str]],
    moves: list[tuple[int, int]],
) -> tuple[int, int]:
    """Сложный уровень: победа → блок → minimax с alpha-beta.

    Поиск ограничен глубиной _HARD_SEARCH_DEPTH и числом
    рассматриваемых кандидатов _HARD_TOP_LEVEL_CANDIDATES /
    _HARD_NODE_CANDIDATES.
    """
    for row, col in moves:                       # шаг 1: победа
        if _would_win(board, row, col, PLAYER_O):
            return row, col
    for row, col in moves:                       # шаг 2: блок
        if _would_win(board, row, col, PLAYER_X):
            return row, col

    candidates = _top_candidates(
        board, moves, PLAYER_O, _HARD_TOP_LEVEL_CANDIDATES
    )
    best_move = candidates[0]
    best_value = -_WIN_SCORE - 1
    for row, col in candidates:
        board[row][col] = PLAYER_O
        remaining = [m for m in moves if m != (row, col)]
        value = _minimax(
            board, remaining, _HARD_SEARCH_DEPTH - 1, False,
            -_WIN_SCORE - 1, _WIN_SCORE + 1,
        )
        board[row][col] = EMPTY
        if value > best_value:
            best_value = value
            best_move = row, col
    return best_move


# ------------------------------------------------------------------
# Публичный класс
# ------------------------------------------------------------------

class AI:
    """ИИ, играющий за PLAYER_O. Поведение зависит от difficulty.

    Не зависит от tkinter. Детерминирован: не использует random.
    """

    def __init__(
        self, difficulty: str = DEFAULT_DIFFICULTY
    ) -> None:
        """Создать ИИ с заданным уровнем сложности."""
        self._difficulty = difficulty

    def get_move(self, game: Game) -> tuple[int, int]:
        """Выбрать и вернуть ход для PLAYER_O.

        Диспетчеризация по self._difficulty:
        - EASY   — победа без блокировки, слабые веса;
        - HARD   — minimax с alpha-beta pruning;
        - MEDIUM — победа → блок → лучший score (по умолчанию).
        """
        moves = sorted(game.get_available_moves())
        if not moves:
            raise ValueError("Нет доступных ходов для ИИ")
        board = game.get_board()
        if self._difficulty == DIFFICULTY_EASY:
            return _get_move_easy(board, moves)
        if self._difficulty == DIFFICULTY_HARD:
            return _get_move_hard(board, moves)
        return _get_move_medium(board, moves)
