"""Подсказка оптимального хода для игрока.

Не выполняет ходов — только вычисляет рекомендацию.
Не зависит от tkinter.
"""

from __future__ import annotations

from constants import HINT_SEARCH_DEPTH
from game import Game
from search import SearchEngine


class HintEngine:
    """Подсказка оптимального хода для игрока.

    Не выполняет ходов — только вычисляет рекомендацию.
    Не зависит от tkinter. Оборачивает SearchEngine и учитывает
    состояние is_game_over().
    """

    def __init__(
        self,
        search_engine: SearchEngine | None = None,
    ) -> None:
        """Инициализировать с опциональным поисковым движком."""
        self._search = search_engine or SearchEngine()

    def get_best_move(
        self,
        game: Game,
        player: str,
    ) -> tuple[int, int] | None:
        """Вернуть рекомендуемый ход для player или None.

        Возвращает None, если игра завершена.
        Глубина поиска определяется константой HINT_SEARCH_DEPTH.
        """
        if game.is_game_over():
            return None
        return self._search.get_best_move(
            game, player, depth=HINT_SEARCH_DEPTH,
        )
