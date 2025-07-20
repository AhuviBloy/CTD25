from dataclasses import dataclass
from .img import Img
import copy

@dataclass
class Board:
    cell_H_pix: int
    cell_W_pix: int
    W_cells: int
    H_cells: int
    img: Img

    # convenience, not required by dataclass
    def clone(self) -> "Board":
        """Clone the board with a copy of the image."""
        cloned_img = Img()
        cloned_img.img = self.img.img.copy()  # העתק תוכן התמונה בפועל
        return Board(
            cell_H_pix=self.cell_H_pix,
            cell_W_pix=self.cell_W_pix,
            W_cells=self.W_cells,
            H_cells=self.H_cells,
            img=cloned_img
        )
