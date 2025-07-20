# import itertools, cv2
# from pathlib import Path
# from .img import Img

# class Graphics:
#     def __init__(self, sprites_folder:Path, fps:int=5, loop=True):
#         self.frames = [Img.read(p) for p in sorted(Path(sprites_folder).glob("*.png"))]
#         self.fps  = fps
#         self.loop = loop
#         self._iter = itertools.cycle(self.frames) if loop else iter(self.frames)
#     def current(self): return next(self._iter)







# import itertools
# from pathlib import Path
# from .img import Img   # יבוא יחסי
# import cv2

# class Graphics:
#     """
#     טוען את כל קובצי ה‑PNG בתיקיית sprites ונותן frame נוכחי בכל קריאה.
#     """

#     def __init__(self, sprites_folder: Path, fps: int = 5, loop: bool = True):
#         sprites_folder = Path(sprites_folder)          # להבטיח שזה Path‑אובייקט
#         # קורא *רק* קבצי ‎.png  (לא משנה אותיות גדולות/קטנות)
#         self.frames = [Img.read(p) for p in sorted(sprites_folder.glob("*.png"))]

#         # ---------- קטע דיבוג חשוב ---------- #
#         if not self.frames:
#             raise FileNotFoundError(
#                 f"No PNGs found in {sprites_folder}\n"
#                 "ודא שהתיקייה קיימת ובתוכה לפחות קובץ ‎*.png‎ אחד."
#             )
#         # ---------- סוף דיבוג ---------------- #

#         self.fps  = fps
#         self.loop = loop
#         self._iter = itertools.cycle(self.frames) if loop else iter(self.frames)

#     def current(self) -> Img:
#         """ה‑frame הבא לאנימציה (מתחלף ב‑cycle)."""
#         return next(self._iter)






# my_code/classes/graphics.py
from pathlib import Path
import itertools
from .img import Img

class Graphics:
    def __init__(self,
                 sprites_folder: Path,
                 cell_size: tuple[int,int],  # ← גובה/רוחב תא
                 fps: int = 5,
                 loop: bool = True):
        w_cell, h_cell = cell_size
        sprites_folder = Path(sprites_folder)

        self.frames = [
            Img.read(p, size=(w_cell, h_cell), keep_aspect=True)
            for p in sorted(sprites_folder.glob("*.png"))
        ]

        if not self.frames:
            raise FileNotFoundError(
                f"No PNGs found in {sprites_folder}"
            )

        self._iter = itertools.cycle(self.frames) if loop else iter(self.frames)

    def current(self) -> Img:
        return next(self._iter)
