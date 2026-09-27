"""Тесты эвристического ИИ (класс AI)."""

import unittest

from constants import BOARD_SIZE, EMPTY, PLAYER_O, PLAYER_X
from ai import AI
from game import Game


class TestAIWinningMove(unittest.TestCase):
    """ИИ делает победный ход, если он доступен."""

    def setUp(self) -> None:
        self.ai = AI()

    def test_takes_winning_move_horizontal(self) -> None:
        """O O O O . → ИИ добавляет пятую O в ряд."""
        game = Game()
        for c in range(4):
            game.make_move(0, c, PLAYER_O)
        move = self.ai.get_move(game)
        self.assertEqual(move, (0, 4))

    def test_takes_winning_move_vertical(self) -> None:
        """O стоят в столбце 2, строки 0-3; ИИ ставит в (4,2)."""
        game = Game()
        for r in range(4):
            game.make_move(r, 2, PLAYER_O)
        move = self.ai.get_move(game)
        self.assertEqual(move, (4, 2))

    def test_takes_winning_move_diagonal(self) -> None:
        """O по диагонали (0,0)-(3,3); ИИ ставит в (4,4)."""
        game = Game()
        for i in range(4):
            game.make_move(i, i, PLAYER_O)
        move = self.ai.get_move(game)
        self.assertEqual(move, (4, 4))


class TestAIBlock(unittest.TestCase):
    """ИИ блокирует победный ход игрока."""

    def setUp(self) -> None:
        self.ai = AI()

    def test_blocks_horizontal_win(self) -> None:
        """X X X X . → ИИ ставит O на свободную клетку."""
        game = Game()
        for c in range(4):
            game.make_move(0, c, PLAYER_X)
        move = self.ai.get_move(game)
        self.assertEqual(move, (0, 4))

    def test_blocks_vertical_win(self) -> None:
        """X в столбце 1 строки 0-3 → ИИ блокирует (4,1)."""
        game = Game()
        for r in range(4):
            game.make_move(r, 1, PLAYER_X)
        move = self.ai.get_move(game)
        self.assertEqual(move, (4, 1))

    def test_prefers_win_over_block(self) -> None:
        """Победный ход приоритетнее блокировки."""
        game = Game()
        # O может победить в строке 1
        for c in range(4):
            game.make_move(1, c, PLAYER_O)
        # X угрожает в строке 0
        for c in range(4):
            game.make_move(0, c, PLAYER_X)
        move = self.ai.get_move(game)
        self.assertEqual(move, (1, 4))


class TestAICenter(unittest.TestCase):
    """ИИ предпочитает центр на пустом поле."""

    def test_prefers_center_on_empty_board(self) -> None:
        """На пустом поле ИИ выбирает (2, 2)."""
        game = Game()
        ai = AI()
        move = ai.get_move(game)
        self.assertEqual(move, (2, 2))


class TestAIValidMoves(unittest.TestCase):
    """ИИ никогда не выбирает занятую клетку."""

    def test_never_picks_occupied_cell(self) -> None:
        """Ход ИИ всегда попадает в список доступных ходов."""
        import random as rnd
        ai = AI()
        rnd.seed(42)
        for _ in range(20):
            game = Game()
            # случайно заполняем несколько клеток
            cells = [(r, c)
                     for r in range(BOARD_SIZE)
                     for c in range(BOARD_SIZE)]
            rnd.shuffle(cells)
            count = rnd.randint(0, 20)
            players = [PLAYER_X, PLAYER_O]
            for i, (r, c) in enumerate(cells[:count]):
                if game.is_game_over():
                    break
                game.make_move(r, c, players[i % 2])
            if game.is_game_over() or not game.get_available_moves():
                continue
            move = ai.get_move(game)
            self.assertIn(move, game.get_available_moves())


class TestAIDeterminism(unittest.TestCase):
    """Повторный вызов get_move с тем же состоянием даёт тот же результат."""

    def test_deterministic(self) -> None:
        """get_move детерминирован."""
        ai = AI()
        game = Game()
        game.make_move(0, 0, PLAYER_X)
        game.make_move(1, 1, PLAYER_O)
        move1 = ai.get_move(game)
        move2 = ai.get_move(game)
        self.assertEqual(move1, move2)

    def test_deterministic_after_multiple_moves(self) -> None:
        """Детерминизм сохраняется при сложном состоянии доски."""
        ai = AI()
        game = Game()
        moves = [
            (0, 0, PLAYER_X), (0, 1, PLAYER_O),
            (1, 0, PLAYER_X), (1, 1, PLAYER_O),
            (2, 0, PLAYER_X),
        ]
        for r, c, p in moves:
            game.make_move(r, c, p)
        move1 = ai.get_move(game)
        move2 = ai.get_move(game)
        self.assertEqual(move1, move2)


if __name__ == "__main__":
    unittest.main()
