# import sys
# import os
# import pytest

# # הוספת נתיב ל-my_code/classes
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'my_code', 'classes')))

# from board import Board
# from img import Img

# def test_board_clone():
#     img = Img().read("board.png")
#     board = Board(
#         cell_H_pix=10,
#         cell_W_pix=10,
#         W_cells=8,
#         H_cells=8,
#         img=img
#     )
#     cloned = board.clone()
#     assert cloned is not board
#     assert cloned.img is not board.img
#     assert (cloned.img.img == board.img.img).all()


import sys, os, pytest, pathlib

# מוסיף את תקיית CTD25/my_code ל‑sys.path (לא את classes!)
BASE_DIR = pathlib.Path(__file__).resolve().parents[1]   # CTD25
sys.path.insert(0, str(BASE_DIR / "my_code"))

# כעת מייבאים עם השם המלא של החבילה
from my_code.classes.board import Board
from my_code.classes.img   import Img


def test_board_clone():
    img = Img().read("board.png")           # בטסטים יחסית ל‑CTD25
    board = Board(cell_H_pix=10, cell_W_pix=10,
                  W_cells=8, H_cells=8,
                  img=img)

    cloned = board.clone()
    assert cloned is not board
    assert cloned.img is not board.img
    assert (cloned.img.img == board.img.img).all()
