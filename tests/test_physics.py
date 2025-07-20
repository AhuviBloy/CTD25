from my_code.classes.physics import Physics
from my_code.classes.board import Board
from my_code.classes.img import Img
import numpy as np

def test_physics_init():
    board = Board(100,100,8,8, Img(np.zeros((800,800,3),dtype=np.uint8)))
    phys = Physics(board)
    phys.reset((0,0))
    assert phys.get_cell() == (0,0)
