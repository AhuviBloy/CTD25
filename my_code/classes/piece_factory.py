# כלים שנראים הפוך בחצי הימני של הלוח
RIGHT_SIDE = {"RB", "NB", "BB"}   # צריח, סוס, רץ (שחור ולבן)

from pathlib import Path
import cv2                              
from .graphics import Graphics
from .physics  import Physics
from .moves    import Moves
from .state    import State
from .piece    import Piece


class PieceFactory:

    def __init__(self, sprites_root: Path, board):
        self.sprites_root = Path(sprites_root)  # לדוגמה "pieces"
        self.board = board
        self.cell_size = (board.cell_W_pix, board.cell_H_pix)


    def create(self, piece_id: str, p_type: str, start_cell: tuple[int, int]) -> Piece:
        gfx_folder = self.sprites_root / p_type / "states" / "idle" / "sprites"
        gfx = Graphics(gfx_folder, self.cell_size)

        phys = Physics(start_cell, self.board)
        phys.pixel_pos = self.board.cell_to_pixel(start_cell)
        phys.start_pixel_pos = phys.pixel_pos
        phys.target_cell = start_cell

        moves_path = self.sprites_root / p_type / "moves.txt"
        # moves = Moves(moves_path, self.board.shape)
        moves = Moves(moves_path, (self.board.W_cells, self.board.H_cells))


        state = State(moves,gfx, phys)
        return Piece(piece_id, state)



