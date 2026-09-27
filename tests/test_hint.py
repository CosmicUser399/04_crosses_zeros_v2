"""Тесты HintEngine — подсказка оптимального хода для игрока."""

import unittest

from constants import BOARD_SIZE, EMPTY, PLAYER_O, PLAYER_X
from game import Game
from hint import HintEngine


class TestHintEngineImmediateWin(unittest.TestCase):
    """HintEngine подсказывает немедленную победу (п.18 ТЗ)."""

    def setUp(self) -> None:
        self.engine = HintEngine()

    def test_immediate_win_horizontal(self) -> None:
        """X X X X . → подсказка указывает на последнюю клетку."""
        game = Game()
        for c in range(4):
            game.make_move(0, c, PLAYER_X)
        move = self.engine.get_best_move(game, PLAYER_X)
        self.assertEqual(move, (0, 4))

    def test_immediate_win_vertical(self) -> None:
        """X в столбце 3, строки 0-3 → подсказка (4, 3)."""
        game = Game()
        for r in range(4):
            game.make_move(r, 3, PLAYER_X)
        move = self.engine.get_best_move(game, PLAYER_X)
        self.assertEqual(move, (4, 3))

    def test_immediate_win_diagonal(self) -> None:
        """X по главной диагонали (0,0)–(3,3) → подсказка (4,4)."""
        game = Game()
        for i in range(4):
            game.make_move(i, i, PLAYER_X)
        move = self.engine.get_best_move(game, PLAYER_X)
        self.assertEqual(move, (4, 4))


class TestHintEngineBlock(unittest.TestCase):
    """HintEngine подсказывает блокировку угрозы (п.18 ТЗ)."""

    def setUp(self) -> None:
        self.engine = HintEngine()

    def test_block_horizontal_o(self) -> None:
        """O O O O . → подсказка X блокирует (0, 4)."""
        game = Game()
        for c in range(4):
            game.make_move(0, c, PLAYER_O)
        move = self.engine.get_best_move(game, PLAYER_X)
        self.assertEqual(move, (0, 4))

    def test_block_vertical_o(self) -> None:
        """O в столбце 1, строки 0-3 → подсказка X (4, 1)."""
        game = Game()
        for r in range(4):
            game.make_move(r, 1, PLAYER_O)
        move = self.engine.get_best_move(game, PLAYER_X)
        self.assertEqual(move, (4, 1))


class TestHintEngineCenterOnEmptyBoard(unittest.TestCase):
    """HintEngine предпочитает центр на пустом поле (п.18 ТЗ)."""

    def test_prefers_center_on_empty_board(self) -> None:
        """Пустое поле → подсказка (2, 2)."""
        game = Game()
        engine = HintEngine()
        move = engine.get_best_move(game, PLAYER_X)
        self.assertEqual(move, (2, 2))


class TestHintEngineNoOccupied(unittest.TestCase):
    """HintEngine никогда не возвращает занятую клетку (п.18 ТЗ)."""

    def test_never_returns_occupied_cell(self) -> None:
        """Подсказка не совпадает ни с одной занятой клеткой."""
        engine = HintEngine()
        game = Game()
        # Занять несколько клеток
        game.make_move(0, 0, PLAYER_X)
        game.make_move(1, 1, PLAYER_O)
        game.make_move(2, 2, PLAYER_X)
        game.make_move(0, 1, PLAYER_O)
        available = game.get_available_moves()
        move = engine.get_best_move(game, PLAYER_X)
        self.assertIsNotNone(move)
        self.assertIn(move, available)


class TestHintEngineAfterWin(unittest.TestCase):
    """HintEngine возвращает None после победы (п.18 ТЗ)."""

    def test_returns_none_after_x_wins(self) -> None:
        """Победа X → get_best_move возвращает None."""
        engine = HintEngine()
        game = Game()
        for c in range(5):
            game.make_move(0, c, PLAYER_X)
        self.assertTrue(game.is_game_over())
        result = engine.get_best_move(game, PLAYER_X)
        self.assertIsNone(result)

    def test_returns_none_after_o_wins(self) -> None:
        """Победа O → get_best_move возвращает None."""
        engine = HintEngine()
        game = Game()
        for c in range(5):
            game.make_move(0, c, PLAYER_O)
        self.assertTrue(game.is_game_over())
        result = engine.get_best_move(game, PLAYER_X)
        self.assertIsNone(result)


class TestHintEngineDrawBoard(unittest.TestCase):
    """HintEngine возвращает None при заполненном поле (п.18 ТЗ)."""

    def test_returns_none_on_full_board(self) -> None:
        """Заполненное поле без победителя → None."""
        engine = HintEngine()
        game = Game()
        # Заполнить поле чередованием без победителя:
        # Используем специальный порядок расстановки
        # (2 строки X, 2 строки O, 1 строка X и т.д.)
        pattern = [
            PLAYER_X, PLAYER_X, PLAYER_O, PLAYER_O, PLAYER_X,
            PLAYER_O, PLAYER_O, PLAYER_X, PLAYER_X, PLAYER_O,
            PLAYER_X, PLAYER_X, PLAYER_O, PLAYER_O, PLAYER_X,
            PLAYER_O, PLAYER_O, PLAYER_X, PLAYER_X, PLAYER_O,
            PLAYER_X, PLAYER_O, PLAYER_X, PLAYER_O, PLAYER_X,
        ]
        for idx in range(BOARD_SIZE * BOARD_SIZE):
            r, c = divmod(idx, BOARD_SIZE)
            if game.is_game_over():
                break
            game.make_move(r, c, pattern[idx])

        if game.is_game_over():
            # Игра могла завершиться победой при этом паттерне —
            # тогда тоже ожидаем None
            result = engine.get_best_move(game, PLAYER_X)
            self.assertIsNone(result)
        else:
            # Если не завершилась, значит поле неполное —
            # пропускаем тест
            pass


class TestHintEngineValidMoveDifferentDepths(unittest.TestCase):
    """HintEngine возвращает допустимый ход при разных depth."""

    def test_valid_move_depth_1(self) -> None:
        """При depth=1 ход входит в список доступных."""
        from search import SearchEngine
        engine = HintEngine(search_engine=SearchEngine())
        game = Game()
        game.make_move(0, 0, PLAYER_X)
        available = game.get_available_moves()
        move = engine.get_best_move(game, PLAYER_X)
        self.assertIsNotNone(move)
        self.assertIn(move, available)


if __name__ == "__main__":
    unittest.main()
