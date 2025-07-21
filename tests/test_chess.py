import pytest
import pathlib
import numpy as np
from unittest.mock import Mock, patch

from my_code.classes.board import Board
from my_code.classes.command import Command
from my_code.classes.graphics import Graphics
from my_code.classes.graphics_factory import GraphicsFactory
from my_code.classes.moves import Moves
from my_code.classes.physics import Physics
from my_code.classes.state import State
from my_code.classes.piece import Piece
from my_code.classes.piece_factory import PieceFactory


# ----------- HELPERS -------------
class DummyImg:
    def __init__(self):
        self.img = np.zeros((10, 10, 3), dtype=np.uint8)

    def copy(self):
        return DummyImg()

    def draw_on(self, other, x, y): pass
    def overlay(self, overlay_img, x, y, alpha): pass


# ----------- TEST Board -----------
def test_board_clone_and_cell_to_pixel():
    img = DummyImg()
    board = Board(50, 50, 8, 8, img)
    clone = board.clone()
    assert isinstance(clone, Board)
    assert clone.img is not board.img
    assert board.cell_to_pixel((1, 2)) == (100, 50)


# ----------- TEST Command -----------
def test_command_str():
    cmd = Command(timestamp=1000, piece_id="P1", type="Move", params=["e2", "e4"])
    assert "Move" in str(cmd)
    assert "P1" in str(cmd)


# ----------- TEST Graphics -----------
def test_graphics_load_and_update(monkeypatch):
    with patch.object(Graphics, "_load_frames", return_value=[DummyImg(), DummyImg()]):
        g = Graphics(sprites_folder=pathlib.Path("."), cell_size=(50, 50))
        assert len(g.frames) == 2
        g.reset(Command(0, "P1", "Idle", []))
        g.update(100)
        img = g.get_img()
        assert isinstance(img, DummyImg)


# ----------- TEST GraphicsFactory -----------
def test_graphics_factory_load(monkeypatch):
    factory = GraphicsFactory()
    # עוקפים טעינת קבצים אמיתית
    monkeypatch.setattr("my_code.classes.graphics.Graphics._load_frames", lambda self: [])
    result = factory.load(pathlib.Path("."), {"fps": 10, "loop": False}, (50, 50))
    assert result is not None


# ----------- TEST Moves -----------
def test_moves_loading_and_get_moves(tmp_path):
    moves_file = tmp_path / "moves.txt"
    moves_file.write_text("1,0\n-1,0\n0,1\n0,-1\n")
    moves = Moves(moves_file, (8, 8))
    res = moves.get_moves(3, 3)
    assert (4, 3) in res
    assert (2, 3) in res


# ----------- TEST Physics -----------
def test_physics_reset_and_update():
    board = Mock()
    board.cell_to_pixel.return_value = (0, 0)
    board.cell_size = 100
    physics = Physics(start_cell=(0, 0), board=board)
    cmd = Mock()
    cmd.target_cell = (1, 1)
    physics.reset(cmd)
    physics.update(1)  # זמן קצר כדי לא לסיים תנועה
    assert isinstance(physics.get_pos(), tuple)


# ----------- TEST State -----------
def test_state_transitions():
    moves = Mock()
    graphics = Mock()
    physics = Mock()
    state1 = State(moves, graphics, physics)
    state2 = State(moves, graphics, physics)
    state1.set_transition("Move", state2)
    cmd = Command(0, "P1", "Move", [])
    next_state = state1.get_state_after_command(cmd, 0)
    assert next_state == state2
    state1.reset(cmd)
    state1.update(100)
    assert state1.get_command() == cmd


# ----------- TEST Piece -----------
def test_piece_on_command_and_draw():
    state = Mock()
    state.update.return_value = state
    state.physics.get_pixel_position.return_value = (0, 0)
    state.graphics.get_img.return_value = DummyImg()
    piece = Piece("P1", state)
    cmd = Command(0, "P1", "Move", [])
    piece.on_command(cmd, 0)
    piece.update(100)
    board = Mock()
    piece.draw_on_board(board, 100)
    assert piece.piece_id == "P1"


# ----------- TEST PieceFactory -----------
# def test_piece_factory_create(monkeypatch):
#     factory = PieceFactory(pathlib.Path("."), board=Mock())

#     # Mock את כל מה שצריך להימנע מקריאה אמיתית לקבצים או פונקציות מסובכות  
#     monkeypatch.setattr("my_code.classes.graphics.Graphics._load_frames", lambda self: [])
#     monkeypatch.setattr("my_code.classes.graphics.Graphics", Mock(return_value="gfx"))
#     monkeypatch.setattr("my_code.classes.physics.Physics", Mock(return_value="phys"))
    
#     # כאן אנחנו מגדירים שכשיקראו ל-Moves, יחזירו Mock ולא ינסו לקרוא קובץ אמיתי
#     monkeypatch.setattr("my_code.classes.moves.Moves", Mock(return_value="moves"))

#     monkeypatch.setattr("my_code.classes.state.State", Mock(return_value="state"))
#     monkeypatch.setattr("my_code.classes.piece.Piece", Mock(return_value="piece"))

#     # עכשיו ניצור piece עם שם חייל כלשהו (למשל "PB") – אבל זה כבר לא ינסה לקרוא קבצים
#     piece = factory.create("P1", "PB", (0, 0))

#     assert piece == "piece"

# from unittest.mock import Mock
# import pathlib

# def test_piece_factory_create(monkeypatch):
#     # Mock board
#     board_mock = Mock()
#     board_mock.cell_W_pix = 64
#     board_mock.cell_H_pix = 64
#     board_mock.shape = (8, 8)
#     board_mock.cell_to_pixel = Mock(return_value=(128, 128))

#     factory = PieceFactory(pathlib.Path("."), board_mock)

#     # Mock כל המחלקות
#     monkeypatch.setattr("my_code.classes.graphics.Graphics", Mock(return_value="gfx"))
#     monkeypatch.setattr("my_code.classes.physics.Physics", Mock(return_value=Mock(
#         pixel_pos=None,
#         start_pixel_pos=None,
#         target_cell=None
#     )))
#     monkeypatch.setattr("my_code.classes.moves.Moves", Mock(return_value="moves"))
#     monkeypatch.setattr("my_code.classes.state.State", Mock(return_value="state"))
#     monkeypatch.setattr("my_code.classes.piece.Piece", Mock(return_value="piece"))

#     # כעת קריאה לפונקציה create - כעת היא אמורה להשתמש במוקים
#     piece = factory.create("P1", "PB", (0, 0))

#     # בדיקה בסיסית
#     assert piece == "piece"
