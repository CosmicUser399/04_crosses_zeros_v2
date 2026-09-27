"""Тесты SearchEngine — поиск лучшего хода для произвольного игрока."""

import unittest

from constants import BOARD_SIZE, EMPTY, PLAYER_O, PLAYER_X
from game import Game
from search import SearchEngine


class TestSearchEngineWinX(unittest.TestCase):
    """SearchEngine выбирает победный ход для PLAYER_X."""

    def setUp(self) -> None:
        self.engine = SearchEngine()

    def test_takes_winning_move_horizontal_x(self) -> None:
        """X X X X . → SearchEngine ставит пятую X в строку."""
        game = Game()
        for c in range(4):
            game.make_move(0, c, PLAYER_X)
        move = self.engine.get_best_move(game, PLAYER_X)
        self.assertEqual(move, (0, 4))

    def test_takes_winning_move_vertical_x(self) -> None:
        """X в столбце 2, строки 0-3 → ставит в (4, 2)."""
        game = Game()
        for r in range(4):
            game.make_move(r, 2, PLAYER_X)
        move = self.engine.get_best_move(game, PLAYER_X)
        self.assertEqual(move, (4, 2))

    def test_takes_winning_move_diagonal_x(self) -> None:
        """X по диагонали (0,0)–(3,3) → ставит в (4, 4)."""
        game = Game()
        for i in range(4):
            game.make_move(i, i, PLAYER_X)
        move = self.engine.get_best_move(game, PLAYER_X)
        self.assertEqual(move, (4, 4))


class TestSearchEngineWinO(unittest.TestCase):
    """SearchEngine выбирает победный ход для PLAYER_O."""

    def setUp(self) -> None:
        self.engine = SearchEngine()

    def test_takes_winning_move_horizontal_o(self) -> None:
        """O O O O . → SearchEngine ставит пятую O в строку."""
        game = Game()
        for c in range(4):
            game.make_move(0, c, PLAYER_O)
        move = self.engine.get_best_move(game, PLAYER_O)
        self.assertEqual(move, (0, 4))

    def test_takes_winning_move_vertical_o(self) -> None:
        """O в столбце 0, строки 0-3 → ставит в (4, 0)."""
        game = Game()
        for r in range(4):
            game.make_move(r, 0, PLAYER_O)
        move = self.engine.get_best_move(game, PLAYER_O)
        self.assertEqual(move, (4, 0))


class TestSearchEngineBlockX(unittest.TestCase):
    """SearchEngine блокирует победный ход соперника."""

    def setUp(self) -> None:
        self.engine = SearchEngine()

    def test_blocks_horizontal_win_for_x(self) -> None:
        """O O O O . → X должен заблокировать (0, 4)."""
        game = Game()
        for c in range(4):
            game.make_move(0, c, PLAYER_O)
        move = self.engine.get_best_move(game, PLAYER_X)
        self.assertEqual(move, (0, 4))

    def test_blocks_vertical_win_for_o(self) -> None:
        """X X X X . → O должен заблокировать (0, 4)."""
        game = Game()
        for c in range(4):
            game.make_move(0, c, PLAYER_X)
        move = self.engine.get_best_move(game, PLAYER_O)
        self.assertEqual(move, (0, 4))


class TestSearchEngineBlockO(unittest.TestCase):
    """SearchEngine (для O) блокирует победный ход X."""

    def setUp(self) -> None:
        self.engine = SearchEngine()

    def test_blocks_horizontal_x_as_o(self) -> None:
        """X X X X . → O блокирует (0, 4)."""
        game = Game()
        for c in range(4):
            game.make_move(0, c, PLAYER_X)
        move = self.engine.get_best_move(game, PLAYER_O)
        self.assertEqual(move, (0, 4))

    def test_prefers_win_over_block_as_x(self) -> None:
        """Победный ход приоритетнее блокировки."""
        game = Game()
        # X может победить в строке 1
        for c in range(4):
            game.make_move(1, c, PLAYER_X)
        # O угрожает в строке 0
        for c in range(4):
            game.make_move(0, c, PLAYER_O)
        move = self.engine.get_best_move(game, PLAYER_X)
        self.assertEqual(move, (1, 4))


class TestSearchEngineCenterOnEmpty(unittest.TestCase):
    """SearchEngine предпочитает центр на пустом поле."""

    def test_center_for_x_depth_1(self) -> None:
        """На пустом поле X выбирает (2, 2) при depth=1."""
        game = Game()
        engine = SearchEngine()
        move = engine.get_best_move(game, PLAYER_X, depth=1)
        self.assertEqual(move, (2, 2))

    def test_center_for_o_depth_1(self) -> None:
        """На пустом поле O выбирает (2, 2) при depth=1."""
        game = Game()
        engine = SearchEngine()
        move = engine.get_best_move(game, PLAYER_O, depth=1)
        self.assertEqual(move, (2, 2))


class TestSearchEngineNoOccupiedCell(unittest.TestCase):
    """SearchEngine никогда не возвращает занятую клетку."""

    def test_never_picks_occupied_cell(self) -> None:
        """Ход всегда попадает в список доступных ходов."""
        import random as rnd
        engine = SearchEngine()
        rnd.seed(0)
        for _ in range(20):
            game = Game()
            cells = [
                (r, c)
                for r in range(BOARD_SIZE)
                for c in range(BOARD_SIZE)
            ]
            rnd.shuffle(cells)
            count = rnd.randint(0, 20)
            players = [PLAYER_X, PLAYER_O]
            for i, (r, c) in enumerate(cells[:count]):
                if game.is_game_over():
                    break
                game.make_move(r, c, players[i % 2])
            if game.is_game_over():
                continue
            available = game.get_available_moves()
            if not available:
                continue
            move = engine.get_best_move(game, PLAYER_X)
            self.assertIsNotNone(move)
            self.assertIn(move, available)


class TestSearchEngineDeterminism(unittest.TestCase):
    """SearchEngine детерминирован."""

    def test_deterministic_depth_1(self) -> None:
        """При depth=1 повторный вызов даёт тот же результат."""
        engine = SearchEngine()
        game = Game()
        game.make_move(0, 0, PLAYER_X)
        game.make_move(1, 1, PLAYER_O)
        move1 = engine.get_best_move(game, PLAYER_X, depth=1)
        move2 = engine.get_best_move(game, PLAYER_X, depth=1)
        self.assertEqual(move1, move2)

    def test_deterministic_depth_3(self) -> None:
        """При depth=3 повторный вызов даёт тот же результат."""
        engine = SearchEngine()
        game = Game()
        game.make_move(0, 0, PLAYER_X)
        game.make_move(2, 2, PLAYER_O)
        move1 = engine.get_best_move(game, PLAYER_X, depth=3)
        move2 = engine.get_best_move(game, PLAYER_X, depth=3)
        self.assertEqual(move1, move2)


class TestSearchEngineGameOver(unittest.TestCase):
    """SearchEngine возвращает None при завершённой игре."""

    def test_returns_none_when_game_over(self) -> None:
        """Победа игрока → get_best_move возвращает None."""
        engine = SearchEngine()
        game = Game()
        for c in range(5):
            game.make_move(0, c, PLAYER_X)
        self.assertTrue(game.is_game_over())
        result = engine.get_best_move(game, PLAYER_O)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
