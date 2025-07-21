# # my_code/run_game.py
# # -----------------------------------------------------------
# # מפעיל משחק לדוגמה: לוח + כל החיילים במצב idle התחלתִי
# # -----------------------------------------------------------

# import pathlib, sys, cv2

# # --- 1. איתור תיקיות בסיס ---
# THIS_DIR  = pathlib.Path(__file__).resolve().parent
# BASE_DIR  = THIS_DIR.parent

# # --- 2. יבוא מחלקות ---
# from .classes.board          import Board
# from .classes.img            import Img
# from .classes.moves          import Moves
# from .classes.piece_factory  import PieceFactory
# from .classes.game           import Game


# # --- 3. קבצים חיצוניים (לוח ותיקיית חיילים) -------------
# BOARD_IMG  =  "board.png"
# PIECES_DIR =  pathlib.Path("pieces")        # בדיוק כמבנה ששלחת

# # --- 4. בניית Board --------------------------------------
# board = Board(cell_H_pix=100, cell_W_pix=100,
#               W_cells=8,    H_cells=8,
#               img=Img.read(BOARD_IMG))

# # --- 5. כללי תנועה בסיסיים -------------------------------

# factory = PieceFactory(PIECES_DIR, board)

# pieces  = []

# # שחורים – שורה אחורית
# black_back = ["RB","NB","BB","QB","KB","BB","NB","RB"]
# for col, code in enumerate(black_back):
#     pieces.append(factory.create(f"{code}{col}", code, (col, 0)))

# # לבנים – שורה אחורית
# white_back = ["RW","NW","BW","QW","KW","BW","NW","RW"]
# for col, code in enumerate(white_back):
#     pieces.append(factory.create(f"{code}{col}", code, (col, 7)))

# # שחורים – רגלים
# for col in range(8):
#     pieces.append(factory.create(f"PB{col}", "PB", (col,1)))

# # לבנים – רגלים
# for col in range(8):
#     pieces.append(factory.create(f"PW{col}", "PW", (col,6)))

# # --- 7. Game ---------------------------------------------
# game = Game(pieces, board)
# game.run()                 # חלון OpenCV עם הלוח והכלים במצב idle



# my_code/run_game.py

import pathlib
import cv2

from .classes.board import Board
from .classes.img import Img
from .classes.piece_factory import PieceFactory
from .classes.game import Game

def main():
    THIS_DIR = pathlib.Path(__file__).resolve().parent
    BASE_DIR = THIS_DIR.parent

    BOARD_IMG  =  "board.png"
    PIECES_DIR =  pathlib.Path("pieces")

    # יצירת הלוח
    board = Board(cell_H_pix=100, cell_W_pix=100,
                  W_cells=8, H_cells=8,
                  img=Img.read(str(BOARD_IMG)))

    # יצירת PieceFactory עם נתיב תיקיית חיילים
    factory = PieceFactory(PIECES_DIR, board)

    pieces = []

    # שחורים - שורה אחורית
    black_back = ["RB","NB","BB","QB","KB","BB","NB","RB"]
    for col, code in enumerate(black_back):
        pieces.append(factory.create(f"{code}{col}", code, (0, col)))

    # לבנים - שורה אחורית
    white_back = ["RW","NW","BW","QW","KW","BW","NW","RW"]
    for col, code in enumerate(white_back):
        pieces.append(factory.create(f"{code}{col}", code, (7, col)))

    # שחורים - רגלים
    for col in range(8):
        pieces.append(factory.create(f"PB{col}", "PB", (1, col)))

    # לבנים - רגלים
    for col in range(8):
        pieces.append(factory.create(f"PW{col}", "PW", (6, col)))

    # יצירת המשחק
    game = Game(pieces, board)
    game.run()

if __name__ == "__main__":
    main()
