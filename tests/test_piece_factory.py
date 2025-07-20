from pathlib import Path
from my_code.classes.board import Board
from my_code.classes.img import Img
from my_code.classes.moves import Moves
from my_code.classes.piece_factory import PieceFactory
import numpy as np

def test_factory_creates_piece(tmp_path):
    # בונים מבנה sprites מינימלי
    pdir = tmp_path/"PW/states/idle/sprites"
    pdir.mkdir(parents=True)
    (pdir/"1.png").write_bytes(b"\x89PNG\r\n\x1a\n")  # header בלבד מספיק ל‑cv2 לקרוא כ‑None → יזרוק, לכן ניצור תמונת בזק אמיתית
    import cv2, numpy as np
    cv2.imwrite(str(pdir/"1.png"), np.zeros((2,2,3), dtype=np.uint8))

    board = Board(100,100,8,8, Img(np.zeros((800,800,3),dtype=np.uint8)))
    moves = Moves({})
    factory = PieceFactory(Path(tmp_path), moves, board)
    piece = factory.create("PW0","PW",(0,6))
    assert piece.id == "PW0"
