from my_code.classes.graphics import Graphics
from my_code.classes.img import Img
import pathlib, numpy as np, cv2, tempfile

def test_graphics_loads_png():
    tmp = pathlib.Path(tempfile.mkdtemp())
    png = tmp/"1.png"
    cv2.imwrite(str(png), np.zeros((2,2,3), dtype=np.uint8))
    gfx = Graphics(tmp, cell_size=(50,50))
    sprite = gfx.current()
    assert isinstance(sprite, Img)
