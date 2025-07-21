# demo_single_piece.py  ── דוגמת הרצה לכלי בודד על לוח

from __future__ import annotations

import time                           # מדידת זמן במילישניות
import cv2                            # תצוגה וקלט מקשים
import numpy as np                    # עבודה עם תמונה כ‑ndarray

# ייבוא יחסי מתוך אותה‑חבילה (my_code.classes)
from .piece   import Piece
from .board   import Board
from .command import Command
from .state   import State


def main() -> None:
    """הרצת דמו: לוח 8×8 וכלי אדום שאפשר להזיז עם חיצים."""
    board  = Board()          # Board יוצר לוח 8×8 עם תאים 80×80 px
    state  = State(3, 3)      # הכלי מתחיל באמצע (שורה 3, עמודה 3)
    piece  = Piece("pawn1", state)

    # map מקשי‑חץ בקוד OpenCV → תזוזת תא
    keymap = {
        81: (-1, 0),  # ←
        82: (0, -1),  # ↑
        83: (1, 0),   # →
        84: (0, 1),   # ↓
    }

    while True:
        now_ms = int(time.time() * 1000)

        # ----- קלט מקשים ---------------------------------------------
        key = cv2.waitKey(1) & 0xFF
        if key == 27:                # Esc = יציאה
            break
        if key in keymap:
            dx, dy = keymap[key]
            piece.on_command(Command(dx, dy), now_ms)

        # ----- עדכון לוגיקה ------------------------------------------
        piece.update(now_ms)

        # ----- ציור ---------------------------------------------------
        canvas = board.img.copy()                       # שכפול רקע
        board_copy = Board(cell_px=board.cell_px,       # Board "דמה"
                           cells=board.cells)
        board_copy.img = canvas
        piece.draw_on_board(board_copy, now_ms)         # הדבקת הכלי

        cv2.imshow("Demo Piece", canvas)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
