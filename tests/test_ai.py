"""Тесты эвристического ИИ (класс AI)."""

import unittest

from constants import (
    BOARD_SIZE,
    DIFFICULTY_EASY,
    DIFFICULTY_HARD,
    DIFFICULTY_MEDIUM,
    EMPTY,
    PLAYER_O,
    PLAYER_X,
)
from ai import AI
from game import Game


class TestAIWinningMove(unittest.TestCase):
    """ИИ (Medium) делает победный ход, если он доступен."""

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
    """ИИ (Medium) блокирует победный ход игрока."""

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
    """ИИ (Medium) предпочитает центр на пустом поле."""

    def test_prefers_center_on_empty_board(self) -> None:
        """На пустом поле ИИ выбирает (2, 2)."""
        game = Game()
        ai = AI()
        move = ai.get_move(game)
        self.assertEqual(move, (2, 2))


class TestAIValidMoves(unittest.TestCase):
    """ИИ (Medium) никогда не выбирает занятую клетку."""

    def test_never_picks_occupied_cell(self) -> None:
        """Ход ИИ всегда попадает в список доступных ходов."""
        import random as rnd
        ai = AI()
        rnd.seed(42)
        for _ in range(20):
            game = Game()
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
    """Повторный вызов get_move с тем же состоянием — тот же ход."""

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


# ------------------------------------------------------------------
# Общие проверки для всех уровней
# ------------------------------------------------------------------

class TestAIDifficultyGeneral(unittest.TestCase):
    """Базовые инварианты для всех трёх уровней сложности."""

    DIFFICULTIES = (DIFFICULTY_EASY, DIFFICULTY_MEDIUM, DIFFICULTY_HARD)

    def _make_partial_game(self) -> Game:
        """Создать частично заполненную игру (не завершённую)."""
        game = Game()
        game.make_move(0, 0, PLAYER_X)
        game.make_move(1, 1, PLAYER_O)
        game.make_move(0, 1, PLAYER_X)
        return game

    def test_returns_valid_move_on_empty_board(self) -> None:
        """Любой уровень возвращает допустимый ход на пустом поле."""
        for diff in self.DIFFICULTIES:
            with self.subTest(difficulty=diff):
                ai = AI(difficulty=diff)
                game = Game()
                move = ai.get_move(game)
                self.assertIn(move, game.get_available_moves())

    def test_returns_valid_move_on_partial_board(self) -> None:
        """Любой уровень возвращает допустимый ход на частичн. поле."""
        for diff in self.DIFFICULTIES:
            with self.subTest(difficulty=diff):
                ai = AI(difficulty=diff)
                game = self._make_partial_game()
                move = ai.get_move(game)
                self.assertIn(move, game.get_available_moves())

    def test_never_picks_occupied_cell(self) -> None:
        """Любой уровень никогда не выбирает занятую клетку."""
        import random as rnd
        rnd.seed(7)
        for diff in self.DIFFICULTIES:
            ai = AI(difficulty=diff)
            for _ in range(10):
                game = Game()
                cells = [(r, c)
                         for r in range(BOARD_SIZE)
                         for c in range(BOARD_SIZE)]
                rnd.shuffle(cells)
                count = rnd.randint(0, 16)
                players = [PLAYER_X, PLAYER_O]
                for i, (r, c) in enumerate(cells[:count]):
                    if game.is_game_over():
                        break
                    game.make_move(r, c, players[i % 2])
                if (game.is_game_over()
                        or not game.get_available_moves()):
                    continue
                with self.subTest(difficulty=diff):
                    move = ai.get_move(game)
                    self.assertIn(move, game.get_available_moves())

    def test_raises_on_no_moves(self) -> None:
        """Любой уровень бросает ValueError, если нет ходов."""
        for diff in self.DIFFICULTIES:
            with self.subTest(difficulty=diff):
                ai = AI(difficulty=diff)
                game = Game()
                # заполняем всё поле без победителя
                players = [PLAYER_X, PLAYER_O]
                count = 0
                for r in range(BOARD_SIZE):
                    for c in range(BOARD_SIZE):
                        game.make_move(r, c, players[count % 2])
                        count += 1
                        if game.is_game_over():
                            break
                    if game.is_game_over():
                        break
                if game.get_available_moves():
                    continue  # победитель найден — пропускаем
                with self.assertRaises(ValueError):
                    ai.get_move(game)


# ------------------------------------------------------------------
# Тесты Easy
# ------------------------------------------------------------------

class TestAIEasy(unittest.TestCase):
    """Тесты поведения ИИ на уровне Easy."""

    def setUp(self) -> None:
        self.ai = AI(difficulty=DIFFICULTY_EASY)

    def test_takes_winning_move(self) -> None:
        """Easy-ИИ всё же делает победный ход."""
        game = Game()
        for c in range(4):
            game.make_move(0, c, PLAYER_O)
        move = self.ai.get_move(game)
        self.assertEqual(move, (0, 4))

    def test_takes_winning_move_vertical(self) -> None:
        """Easy-ИИ побеждает вертикально."""
        game = Game()
        for r in range(4):
            game.make_move(r, 0, PLAYER_O)
        move = self.ai.get_move(game)
        self.assertEqual(move, (4, 0))

    def test_does_not_block_opponent(self) -> None:
        """Easy-ИИ НЕ блокирует угрозу X из 4 в ряд.

        X в строке 2, колонки 0-3. Блокирующая клетка (2,4)
        не является угловой, поэтому Easy предпочтёт угол.
        """
        game = Game()
        for c in range(4):
            game.make_move(2, c, PLAYER_X)
        move = self.ai.get_move(game)
        self.assertNotEqual(move, (2, 4))

    def test_valid_move_on_empty_board(self) -> None:
        """Easy-ИИ возвращает допустимый ход на пустом поле."""
        game = Game()
        move = self.ai.get_move(game)
        self.assertIn(move, game.get_available_moves())

    def test_deterministic(self) -> None:
        """Easy-ИИ детерминирован."""
        game = Game()
        game.make_move(0, 0, PLAYER_X)
        move1 = self.ai.get_move(game)
        move2 = self.ai.get_move(game)
        self.assertEqual(move1, move2)


# ------------------------------------------------------------------
# Тесты Hard
# ------------------------------------------------------------------

class TestAIHard(unittest.TestCase):
    """Тесты поведения ИИ на уровне Hard."""

    def setUp(self) -> None:
        self.ai = AI(difficulty=DIFFICULTY_HARD)

    def test_takes_winning_move(self) -> None:
        """Hard-ИИ делает победный ход."""
        game = Game()
        for c in range(4):
            game.make_move(0, c, PLAYER_O)
        move = self.ai.get_move(game)
        self.assertEqual(move, (0, 4))

    def test_blocks_opponent(self) -> None:
        """Hard-ИИ блокирует угрозу X из 4 в ряд."""
        game = Game()
        for c in range(4):
            game.make_move(0, c, PLAYER_X)
        move = self.ai.get_move(game)
        self.assertEqual(move, (0, 4))

    def test_prefers_win_over_block(self) -> None:
        """Hard-ИИ выбирает победу, а не блокировку."""
        game = Game()
        for c in range(4):
            game.make_move(1, c, PLAYER_O)
        for c in range(4):
            game.make_move(0, c, PLAYER_X)
        move = self.ai.get_move(game)
        self.assertEqual(move, (1, 4))

    def test_valid_move_on_empty_board(self) -> None:
        """Hard-ИИ возвращает допустимый ход на пустом поле."""
        game = Game()
        move = self.ai.get_move(game)
        self.assertIn(move, game.get_available_moves())

    def test_blocks_diagonal_threat(self) -> None:
        """Hard-ИИ блокирует диагональную угрозу X."""
        game = Game()
        # X угрожает по диагонали: (0,0),(1,1),(2,2),(3,3)
        for i in range(4):
            game.make_move(i, i, PLAYER_X)
        move = self.ai.get_move(game)
        self.assertEqual(move, (4, 4))

    def test_deterministic(self) -> None:
        """Hard-ИИ детерминирован."""
        game = Game()
        game.make_move(0, 0, PLAYER_X)
        move1 = self.ai.get_move(game)
        move2 = self.ai.get_move(game)
        self.assertEqual(move1, move2)

    def test_minimax_picks_center_vs_fork(self) -> None:
        """Hard-ИИ занимает центр при формирующемся форке X.

        X стоят на (0,0),(0,2),(2,0) — три угла 3×3-подсетки.
        Центр (2,2) свободен; Hard выбирает его как лучшую
        позицию, подтверждённую в том числе минимакс-поиском.
        """
        game = Game()
        game.make_move(0, 0, PLAYER_X)
        game.make_move(0, 2, PLAYER_X)
        game.make_move(2, 0, PLAYER_X)
        move = self.ai.get_move(game)
        self.assertIn(move, game.get_available_moves())
        # (2,2) должен быть свободен (X не занимал его)
        self.assertIn((2, 2), game.get_available_moves())
        # Hard выбирает центральную точку (лучшую оборонит. позицию)
        self.assertEqual(move, (2, 2))

    def test_hard_differs_from_medium_via_lookahead(self) -> None:
        """Hard видит дальше Medium и может выбрать другой ход.

        Позиция: X стоят на (0,3),(1,3),(4,1); O — на (2,0),(4,2).
        Medium жадно выбирает центр (2,2); Hard с учётом ответа
        противника выбирает иначе — оба хода допустимы.
        """
        hard_ai = AI(difficulty=DIFFICULTY_HARD)
        medium_ai = AI(difficulty=DIFFICULTY_MEDIUM)
        game = Game()
        game.make_move(0, 3, PLAYER_X)
        game.make_move(2, 0, PLAYER_O)
        game.make_move(1, 3, PLAYER_X)
        game.make_move(4, 2, PLAYER_O)
        game.make_move(4, 1, PLAYER_X)
        hard_move = hard_ai.get_move(game)
        medium_move = medium_ai.get_move(game)
        self.assertIn(hard_move, game.get_available_moves())
        self.assertIn(medium_move, game.get_available_moves())
        # Hard и Medium выбирают разные ходы — проявление lookahead
        self.assertNotEqual(hard_move, medium_move)


if __name__ == "__main__":
    unittest.main()
