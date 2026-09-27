"""Точка входа приложения «Крестики-нолики 5×5»."""

import logging
import tkinter as tk

from constants import WINDOW_SIZE, WINDOW_TITLE
from ui import TicTacToeApp


def main() -> None:
    """Запустить приложение."""
    logging.basicConfig(level=logging.INFO)
    root = tk.Tk()
    root.title(WINDOW_TITLE)
    root.geometry(WINDOW_SIZE)
    TicTacToeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
