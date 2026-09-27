"""Обобщённый поиск лучшего хода для произвольного игрока.

Не зависит от tkinter. Детерминирован: не использует random.
"""

from __future__ import annotations

from constants import BOARD_SIZE, EMPTY, PLAYER_O, PLAYER_X, WIN_LENGTH
from game import Game, _DIRECTIONS, find_winning_line


def _other(player: str) -> str:
    """Вернуть символ соперника."""
    return PLAYER_O if player == PLAYER_X else PLAYER_X


def _would_win(
    board: list[list[str]],
    row: int,
    col: int,
    player: str,
) -> bool:
    """Вернуть True, если ход player в (row, col) победит.

    Использует find_winning_line без мутации доски.
    """
    return find_winning_line(board, row, col, player) is not None


def _windows(
    row: int,
    col: int,
    dr: int,
    dc: int,
    size: int,
) -> list[list[tuple[int, int]]]:
    """Вернуть окна длины WIN_LENGTH в направлении (dr, dc).

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
    for start in range(
        max(0, idx - WIN_LENGTH + 1),
        min(len(all_cells) - WIN_LENGTH + 1, idx + 1),
    ):
        result.append(all_cells[start:start + WIN_LENGTH])
    return result


def _score_move(
    board: list[list[str]],
    row: int,
    col: int,
    player: str,
) -> int:
    """Вычислить эвристическую оценку хода player в (row, col).

    Веса:
    - центр поля:                         +10
    - «живая» линия с уже стоящим player: +6 за каждую линию
    - «живая» пустая линия:               +3 за каждую линию
    - угловая клетка:                     +3
    - прочие клетки:                      +1 (база)
    """
    size = len(board)
    opponent = _other(player)
    score = 1  # база

    center = BOARD_SIZE // 2
    if row == center and col == center:
        score += 10

    if row in (0, size - 1) and col in (0, size - 1):
        score += 3

    for dr, dc in _DIRECTIONS:
        for window in _windows(row, col, dr, dc, size):
            cells_in_window = [
                board[r][c]
                for r, c in window
                if not (r == row and c == col)
            ]
            if opponent in cells_in_window:
                continue  # линия заблокирована соперником
            player_count = cells_in_window.count(player)
            if player_count > 0:
                score += 6
            else:
                score += 3

    return score


def _evaluate_position(
    board: list[list[str]],
    player: str,
) -> int:
    """Эвристическая оценка всей позиции для player.

    Суммирует оценки своих клеток и вычитает оценки клеток
    соперника.
    """
    opponent = _other(player)
    score = 0
    size = len(board)
    for r in range(size):
        for c in range(size):
            if board[r][c] == player:
                score += _score_move(board, r, c, player)
            elif board[r][c] == opponent:
                score -= _score_move(board, r, c, opponent)
    return score


def _minimax(
    board: list[list[str]],
    depth: int,
    mover: str,
    root_player: str,
    alpha: int,
    beta: int,
) -> int:
    """Minimax с alpha-beta pruning, ограниченный по глубине.

    Возвращает оценку позиции с точки зрения root_player.
    Большее значение — лучше для root_player.
    """
    moves = sorted(
        (r, c)
        for r in range(BOARD_SIZE)
        for c in range(BOARD_SIZE)
        if board[r][c] == EMPTY
    )
    if not moves or depth == 0:
        return _evaluate_position(board, root_player)

    opponent = _other(mover)
    is_maximizing = (mover == root_player)

    if is_maximizing:
        best = -100_000
        for row, col in moves:
            # Проверить немедленную победу до мутации доски
            if _would_win(board, row, col, mover):
                return 10_000 + depth
            board[row][col] = mover
            val = _minimax(
                board, depth - 1, opponent, root_player,
                alpha, beta,
            )
            board[row][col] = EMPTY
            if val > best:
                best = val
            if best > alpha:
                alpha = best
            if alpha >= beta:
                break
        return best
    else:
        best = 100_000
        for row, col in moves:
            # Победа соперника плоха для root_player
            if _would_win(board, row, col, mover):
                return -(10_000 + depth)
            board[row][col] = mover
            val = _minimax(
                board, depth - 1, opponent, root_player,
                alpha, beta,
            )
            board[row][col] = EMPTY
            if val < best:
                best = val
            if best < beta:
                beta = best
            if alpha >= beta:
                break
        return best


class SearchEngine:
    """Поиск лучшего хода для произвольного игрока.

    Не зависит от tkinter. Детерминирован: не использует random.
    Используется HintEngine как общий алгоритм поиска.
    """

    def get_best_move(
        self,
        game: Game,
        player: str,
        depth: int = 1,
    ) -> tuple[int, int] | None:
        """Вернуть лучший ход для player или None.

        Возвращает None, если игра завершена или нет свободных
        клеток.

        Приоритеты:
        1. Немедленная победа player.
        2. Блокировка немедленной победы соперника.
        3. При depth <= 1 — эвристический score хода.
           При depth > 1  — minimax с alpha-beta.
        """
        if game.is_game_over():
            return None
        moves = sorted(game.get_available_moves())
        if not moves:
            return None

        board = game.get_board()

        # Шаг 1: немедленная победа player
        for row, col in moves:
            if _would_win(board, row, col, player):
                return row, col

        # Шаг 2: блокировка немедленной победы соперника
        opponent = _other(player)
        for row, col in moves:
            if _would_win(board, row, col, opponent):
                return row, col

        # Шаг 3: оценка хода
        if depth <= 1:
            best_move = moves[0]
            best_score = -1
            for row, col in moves:
                s = _score_move(board, row, col, player)
                if s > best_score:
                    best_score = s
                    best_move = (row, col)
            return best_move

        # Шаг 3 (depth > 1): minimax
        best_move = moves[0]
        best_score = -100_000
        for row, col in moves:
            board[row][col] = player
            score = _minimax(
                board, depth - 1, opponent, player,
                -100_000, 100_000,
            )
            board[row][col] = EMPTY
            if score > best_score:
                best_score = score
                best_move = (row, col)
        return best_move
