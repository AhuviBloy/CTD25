import sys
import os
import pytest

# הוספת הנתיב הנכון שמכיל את img.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'my_code', 'classes')))

from img import Img

def test_read_existing_image():
    img = Img().read("board.png")
    assert img.img is not None
    assert img.img.shape[0] > 0 and img.img.shape[1] > 0

def test_read_missing_image():
    with pytest.raises(FileNotFoundError):
        Img().read("no_such_file.png")

def test_resize_with_aspect():
    img = Img().read("board.png", size=(100, 50), keep_aspect=True)
    h, w = img.img.shape[:2]
    assert w <= 100 and h <= 50

def test_put_text_and_save(tmp_path):
    img = Img().read("board.png")
    img.put_text("TEST", 50, 50, 1.0)
    output_path = tmp_path / "output.png"
    img.save(output_path)
    assert output_path.exists()

def test_draw_on_same_size():
    background = Img().read("board.png")
    overlay = Img().read("board.png", size=(50, 50))
    overlay.draw_on(background, 10, 10)
    assert background.img is not None
