# # my_code/classes/piece_factory.py
# from pathlib import Path
# from .graphics import Graphics
# from .physics  import Physics
# from .moves    import Moves
# from .state    import State      # ← הוסף שורה זו אם חסרה
# from .piece    import Piece


# import cv2                                    # ← הוסף
# class PieceFactory:
#     def __init__(self, sprites_root: Path, moves, board):
#         self.sprites_root = Path(sprites_root)
#         self.moves  = moves
#         self.board  = board
#         self.cell_size = (board.cell_W_pix, board.cell_H_pix)

#     def create(self, piece_id: str, p_type: str, start_cell: tuple[int,int]):
#         gfx_folder = self.sprites_root / p_type / "states" / "idle" / "sprites"
#         gfx   = Graphics(gfx_folder, self.cell_size)    # ← מעביר גודל תא
#         phys  = Physics(self.board)
#         phys.reset(start_cell)
#         state = State(gfx, phys)
#         return Piece(piece_id, state)













# my_code/classes/piece_factory.py
from pathlib import Path

import cv2                                   # Flip images
from .graphics import Graphics
from .physics  import Physics
from .moves    import Moves
from .state    import State
from .piece    import Piece

# כלים שנראים הפוך בחצי הימני של הלוח
RIGHT_SIDE = {"RB", "NB", "BB"}   # צריח, סוס, רץ (שחור ולבן)

class PieceFactory:
    """
    יוצר Piece מלא (State + Physics + Graphics) לפי סוג ומיקום פתיחה
    """
    def __init__(self, sprites_root: Path, moves: Moves, board):
        self.sprites_root = Path(sprites_root)
        self.moves        = moves
        self.board        = board
        self.cell_size    = (board.cell_W_pix, board.cell_H_pix)

    # ----------------------------------------------------------------
    def create(self,
               piece_id:  str,
               p_type:    str,
               start_cell: tuple[int, int]) -> Piece:
        """
        piece_id   – מזהה יחודי   (למשל "PB3")
        p_type     – סוג הכלי     ("PB", "QB" ...)
        start_cell – תא פתיחה     (col,row)
        """
        # --- Graphics ---
        gfx_folder = (self.sprites_root / p_type /
                      "states" / "idle" / "sprites")
        gfx = Graphics(gfx_folder, self.cell_size)

        # הופכים אופקית אם זה כלי מ‑RIGHT_SIDE שנמצא בחצי הימני (col > 3)
        col, _ = start_cell
        if p_type in RIGHT_SIDE and col > 3:
            for frame in gfx.frames:                 # כל Img ב‑Animation
                frame.img = cv2.flip(frame.img, 1)   # 1 = flip ציר אופקי

        # --- Physics ---
        phys = Physics(self.board)
        phys.reset(start_cell)

        # --- State (graphics + physics) ---
        state = State(gfx, phys)

        return Piece(piece_id, state)
