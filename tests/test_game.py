"""Тесты игровой модели Game и find_winning_line."""

import unittest

from constants import BOARD_SIZE, EMPTY, PLAYER_O, PLAYER_X
from game import Game, find_winning_line


class TestFindWinningLine(unittest.TestCase):
    """Тесты чистой функции find_winning_line."""

    def _make_board(self) -> list[list[str]]:
        return [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]

    def test_no_win_empty_board(self) -> None:
        """На пустой доске победы нет."""
        board = self._make_board()
        result = find_winning_line(board, 2, 2, PLAYER_X)
        self.assertIsNone(result)

    def test_horizontal_win(self) -> None:
        """Горизонтальная линия из WIN_LENGTH возвращает клетки."""
        board = self._make_board()
        for c in range(5):
            board[0][c] = PLAYER_X
        result = find_winning_line(board, 0, 2, PLAYER_X)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 5)
        for r, c in result:
            self.assertEqual(r, 0)

    def test_vertical_win(self) -> None:
        """Вертикальная линия из WIN_LENGTH возвращает клетки."""
        board = self._make_board()
        for r in range(5):
            board[r][1] = PLAYER_O
        result = find_winning_line(board, 2, 1, PLAYER_O)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 5)
        for r, c in result:
            self.assertEqual(c, 1)

    def test_diagonal_win(self) -> None:
        """Диагональ из WIN_LENGTH возвращает клетки."""
        board = self._make_board()
        for i in range(5):
            board[i][i] = PLAYER_X
        result = find_winning_line(board, 2, 2, PLAYER_X)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 5)

    def test_anti_diagonal_win(self) -> None:
        """Обратная диагональ из WIN_LENGTH возвращает клетки."""
        board = self._make_board()
        for i in range(5):
            board[i][4 - i] = PLAYER_X
        result = find_winning_line(board, 2, 2, PLAYER_X)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 5)

    def test_four_in_row_not_win(self) -> None:
        """4 подряд — это ещё не победа."""
        board = self._make_board()
        for c in range(4):
            board[0][c] = PLAYER_X
        result = find_winning_line(board, 0, 3, PLAYER_X)
        self.assertIsNone(result)

    def test_hypothetical_move(self) -> None:
        """Победа проверяется без записи в доску (гипотетический ход)."""
        board = self._make_board()
        for c in range(4):
            board[0][c] = PLAYER_X
        # Клетка (0,4) пуста, но проверяем как будто X там стоит
        result = find_winning_line(board, 0, 4, PLAYER_X)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 5)
        # Доска не изменилась
        self.assertEqual(board[0][4], EMPTY)


class TestGameInit(unittest.TestCase):
    """Тесты начального состояния Game."""

    def setUp(self) -> None:
        self.game = Game()

    def test_board_size(self) -> None:
        """Поле имеет размер BOARD_SIZE × BOARD_SIZE."""
        board = self.game.get_board()
        self.assertEqual(len(board), BOARD_SIZE)
        for row in board:
            self.assertEqual(len(row), BOARD_SIZE)

    def test_all_cells_empty(self) -> None:
        """Все клетки пустые при инициализации."""
        board = self.game.get_board()
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                self.assertEqual(board[r][c], EMPTY)

    def test_no_winner(self) -> None:
        """Победителя нет при инициализации."""
        self.assertIsNone(self.game.get_winner())

    def test_not_game_over(self) -> None:
        """Игра не завершена при инициализации."""
        self.assertFalse(self.game.is_game_over())

    def test_not_draw(self) -> None:
        """Ничьей нет при инициализации."""
        self.assertFalse(self.game.is_draw())


class TestGameMakeMove(unittest.TestCase):
    """Тесты хода Game.make_move."""

    def setUp(self) -> None:
        self.game = Game()

    def test_valid_move_returns_true(self) -> None:
        """Корректный ход возвращает True."""
        result = self.game.make_move(0, 0, PLAYER_X)
        self.assertTrue(result)

    def test_valid_move_updates_cell(self) -> None:
        """После хода клетка содержит символ игрока."""
        self.game.make_move(2, 3, PLAYER_X)
        self.assertEqual(self.game.get_cell(2, 3), PLAYER_X)

    def test_occupied_cell_returns_false(self) -> None:
        """Ход в занятую клетку возвращает False."""
        self.game.make_move(0, 0, PLAYER_X)
        result = self.game.make_move(0, 0, PLAYER_O)
        self.assertFalse(result)

    def test_occupied_cell_unchanged(self) -> None:
        """Занятая клетка не меняется."""
        self.game.make_move(1, 1, PLAYER_X)
        self.game.make_move(1, 1, PLAYER_O)
        self.assertEqual(self.game.get_cell(1, 1), PLAYER_X)

    def test_out_of_bounds_returns_false(self) -> None:
        """Ход за пределами поля возвращает False."""
        self.assertFalse(self.game.make_move(-1, 0, PLAYER_X))
        self.assertFalse(self.game.make_move(0, BOARD_SIZE, PLAYER_X))

    def test_no_move_after_game_over(self) -> None:
        """После окончания игры ходы невозможны."""
        for c in range(5):
            self.game.make_move(0, c, PLAYER_X)
        self.assertTrue(self.game.is_game_over())
        result = self.game.make_move(1, 0, PLAYER_O)
        self.assertFalse(result)


class TestGameWin(unittest.TestCase):
    """Тесты обнаружения победы."""

    def setUp(self) -> None:
        self.game = Game()

    def _make_horizontal_win(self) -> None:
        for c in range(5):
            self.game.make_move(0, c, PLAYER_X)

    def _make_vertical_win(self) -> None:
        for r in range(5):
            self.game.make_move(r, 0, PLAYER_X)

    def _make_diagonal_win(self) -> None:
        for i in range(5):
            self.game.make_move(i, i, PLAYER_X)

    def _make_anti_diagonal_win(self) -> None:
        for i in range(5):
            self.game.make_move(i, 4 - i, PLAYER_X)

    def test_horizontal_win(self) -> None:
        """Победа по горизонтали определяется корректно."""
        self._make_horizontal_win()
        self.assertTrue(self.game.is_game_over())
        self.assertEqual(self.game.get_winner(), PLAYER_X)

    def test_vertical_win(self) -> None:
        """Победа по вертикали определяется корректно."""
        self._make_vertical_win()
        self.assertTrue(self.game.is_game_over())
        self.assertEqual(self.game.get_winner(), PLAYER_X)

    def test_diagonal_win(self) -> None:
        """Победа по диагонали определяется корректно."""
        self._make_diagonal_win()
        self.assertTrue(self.game.is_game_over())
        self.assertEqual(self.game.get_winner(), PLAYER_X)

    def test_anti_diagonal_win(self) -> None:
        """Победа по обратной диагонали определяется корректно."""
        self._make_anti_diagonal_win()
        self.assertTrue(self.game.is_game_over())
        self.assertEqual(self.game.get_winner(), PLAYER_X)

    def test_four_in_row_not_win(self) -> None:
        """4 в ряд — не победа."""
        for c in range(4):
            self.game.make_move(0, c, PLAYER_X)
        self.assertFalse(self.game.is_game_over())
        self.assertIsNone(self.game.get_winner())

    def test_winning_cells_count(self) -> None:
        """get_winning_cells возвращает ровно 5 клеток."""
        self._make_horizontal_win()
        cells = self.game.get_winning_cells()
        self.assertEqual(len(cells), 5)

    def test_winning_cells_correct(self) -> None:
        """Победные клетки принадлежат выигрышной горизонтали."""
        self._make_horizontal_win()
        cells = self.game.get_winning_cells()
        for r, c in cells:
            self.assertEqual(r, 0)
            self.assertIn(c, range(5))

    def test_winning_cells_empty_before_win(self) -> None:
        """До победы get_winning_cells возвращает пустой список."""
        self.game.make_move(0, 0, PLAYER_X)
        self.assertEqual(self.game.get_winning_cells(), [])


class TestGameDraw(unittest.TestCase):
    """Тесты ничьей."""

    def setUp(self) -> None:
        self.game = Game()

    def _fill_draw(self) -> None:
        """Заполнить доску без победы ни одного игрока.

        Шаблон:
          X O X O X
          O X O X O
          X O X O X
          O X O X O
          O X O X O
        """
        pattern = [
            [PLAYER_X, PLAYER_O, PLAYER_X, PLAYER_O, PLAYER_X],
            [PLAYER_O, PLAYER_X, PLAYER_O, PLAYER_X, PLAYER_O],
            [PLAYER_X, PLAYER_O, PLAYER_X, PLAYER_O, PLAYER_X],
            [PLAYER_O, PLAYER_X, PLAYER_O, PLAYER_X, PLAYER_O],
            [PLAYER_O, PLAYER_X, PLAYER_O, PLAYER_X, PLAYER_O],
        ]
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                self.game.make_move(r, c, pattern[r][c])

    def test_draw_detected(self) -> None:
        """Ничья определяется при полном заполнении без победителя."""
        self._fill_draw()
        self.assertTrue(self.game.is_game_over())
        self.assertIsNone(self.game.get_winner())
        self.assertTrue(self.game.is_draw())


class TestGameReset(unittest.TestCase):
    """Тесты сброса Game.reset."""

    def test_reset_clears_board(self) -> None:
        """После reset поле пустое."""
        game = Game()
        game.make_move(0, 0, PLAYER_X)
        game.reset()
        board = game.get_board()
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                self.assertEqual(board[r][c], EMPTY)

    def test_reset_clears_game_over(self) -> None:
        """После reset игра не считается завершённой."""
        game = Game()
        for c in range(5):
            game.make_move(0, c, PLAYER_X)
        game.reset()
        self.assertFalse(game.is_game_over())

    def test_reset_clears_winner(self) -> None:
        """После reset победителя нет."""
        game = Game()
        for c in range(5):
            game.make_move(0, c, PLAYER_X)
        game.reset()
        self.assertIsNone(game.get_winner())


class TestGetBoard(unittest.TestCase):
    """Тесты get_board и get_cell."""

    def test_get_board_is_copy(self) -> None:
        """get_board возвращает независимую копию."""
        game = Game()
        board = game.get_board()
        board[0][0] = PLAYER_X
        self.assertEqual(game.get_cell(0, 0), EMPTY)

    def test_get_cell(self) -> None:
        """get_cell возвращает корректное значение."""
        game = Game()
        game.make_move(3, 4, PLAYER_O)
        self.assertEqual(game.get_cell(3, 4), PLAYER_O)


if __name__ == "__main__":
    unittest.main()
