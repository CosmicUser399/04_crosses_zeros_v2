"""Настройки игры «Крестики-нолики 5×5».

Модуль не содержит игровой логики — только константы.
"""

BOARD_SIZE = 5
WIN_LENGTH = 5

PLAYER_X = "X"
PLAYER_O = "O"

EMPTY = ""

PLAYER_X_NAME = "Игрок"
PLAYER_O_NAME = "Компьютер"

WINDOW_TITLE = "Крестики-нолики 5×5"
WINDOW_SIZE = "700x800"
CELL_FONT = ("Arial", 24, "bold")

AI_MOVE_DELAY_MS = 300

HINT_SEARCH_DEPTH = 3
HINT_BUTTON_TEXT = "Подсказать ход"
HINT_STATUS_TEXT = "Попробуйте сделать ход в подсвеченную клетку."
DIFFICULTY_EASY = "easy"
DIFFICULTY_MEDIUM = "medium"
DIFFICULTY_HARD = "hard"

DIFFICULTY_ORDER = (
    DIFFICULTY_EASY,
    DIFFICULTY_MEDIUM,
    DIFFICULTY_HARD,
)

DIFFICULTY_NAMES = {
    DIFFICULTY_EASY: "Простой",
    DIFFICULTY_MEDIUM: "Средний",
    DIFFICULTY_HARD: "Сложный",
}

DEFAULT_DIFFICULTY = DIFFICULTY_MEDIUM
