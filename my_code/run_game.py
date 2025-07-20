# my_code/run_game.py
# -----------------------------------------------------------
# מפעיל משחק לדוגמה: לוח + כל החיילים במצב idle התחלתִי
# -----------------------------------------------------------

import pathlib, sys, cv2

# --- 1. איתור תיקיות בסיס ---
THIS_DIR  = pathlib.Path(__file__).resolve().parent
BASE_DIR  = THIS_DIR.parent

# --- 2. יבוא מחלקות ---
from .classes.board          import Board
from .classes.img            import Img
from .classes.moves          import Moves
from .classes.piece_factory  import PieceFactory
from .classes.game           import Game


# --- 3. קבצים חיצוניים (לוח ותיקיית חיילים) -------------
BOARD_IMG  =  "board.png"
PIECES_DIR =  pathlib.Path("pieces")        # בדיוק כמבנה ששלחת

# --- 4. בניית Board --------------------------------------
board = Board(cell_H_pix=100, cell_W_pix=100,
              W_cells=8,    H_cells=8,
              img=Img.read(BOARD_IMG))

# --- 5. כללי תנועה בסיסיים -------------------------------
dummy_rules = {
    "PB": [(0, 1)],  # רגלי שחור   (Pawn Black)
    "PW": [(0,-1)],  # רגלי לבן
    "NB": [(1,2), (2,1), (-1,2), (-2,1)],   # סוס
    "NW": [(1,-2),(2,-1),(-1,-2),(-2,-1)],
}
moves = Moves(dummy_rules)

# --- 6. ייצור כלים ---------------------------------------
factory = PieceFactory(PIECES_DIR, moves, board)
pieces  = []

# שחורים – שורה אחורית
black_back = ["RB","NB","BB","QB","KB","BB","NB","RB"]
for col, code in enumerate(black_back):
    pieces.append(factory.create(code+"1", code, (col,0)))
# שחורים – רגלים
for col in range(8):
    pieces.append(factory.create(f"PB{col}", "PB", (col,1)))

# לבנים – רגלים
for col in range(8):
    pieces.append(factory.create(f"PW{col}", "PW", (col,6)))
# לבנים – שורה אחורית
white_back = ["RW","NW","BW","QW","KW","BW","NW","RW"]
for col, code in enumerate(white_back):
    pieces.append(factory.create(code+"1", code, (col,7)))

# --- 7. Game ---------------------------------------------
game = Game(pieces, board)
game.run()                 # חלון OpenCV עם הלוח והכלים במצב idle
