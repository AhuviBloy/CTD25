# from pathlib import Path
# import itertools
# from .img import Img

# class Graphics:
#     def __init__(self,
#                  sprites_folder: Path,
#                  cell_size: tuple[int,int],  # ← גובה/רוחב תא
#                  fps: int = 5,
#                  loop: bool = True):
#         w_cell, h_cell = cell_size
#         sprites_folder = Path(sprites_folder)

#         self.frames = [
#             Img.read(p, size=(w_cell, h_cell), keep_aspect=True)
#             for p in sorted(sprites_folder.glob("*.png"))
#         ]

#         if not self.frames:
#             raise FileNotFoundError(
#                 f"No PNGs found in {sprites_folder}"
#             )

#         self._iter = itertools.cycle(self.frames) if loop else iter(self.frames)

#     def current(self) -> Img:
#         return next(self._iter)


import pathlib
from typing import List
import time
from .img import Img
from .command import Command
import copy
import os

class Graphics:
    def __init__(self,
                 sprites_folder: pathlib.Path,
                 cell_size: tuple[int, int],
                 loop: bool = True,
                 fps: float = 6.0):
        """Initialize graphics with sprites folder, cell size, loop setting, and FPS."""
        self.sprites_folder = sprites_folder
        self.cell_size = cell_size
        self.loop = loop
        self.fps = fps
        self.frame_time = 1000 / fps  # milliseconds per frame
        self.frames: List[Img] = self._load_frames()
        self.current_frame = 0
        self.last_update_ms = 0
        self.current_cmd: Command | None = None

    def _load_frames(self) -> List[Img]:
        """Load all frames from sprites folder and resize to cell size."""
        frames = []
        
        # בדוק שהתיקייה קיימת
        if not self.sprites_folder.exists():
            raise FileNotFoundError(f"Sprites folder not found: {self.sprites_folder}")
        
        # קבצים בתיקייה
        files = sorted(self.sprites_folder.glob("*.png"))
        if not files:
            raise FileNotFoundError(f"No sprite images found in: {self.sprites_folder}")
        
        # טען את התמונות
        for img_path in files:
            img = Img.read(str(img_path))
            if img.img is None:  # לא נטענה תמונה
                raise ValueError(f"Failed to load image: {img_path}")
            
            frames.append(img.resize(self.cell_size))
        
        return frames

        # """Load all frames from sprites folder and resize to cell size."""
        # frames = []
        # for file in sorted(os.listdir(self.sprites_folder)):
        #     if file.lower().endswith(('.png', '.jpg', '.jpeg')):
        #         img_path = self.sprites_folder / file
        #         frames.append(Img(img_path).resize(self.cell_size))
        # return frames

    def copy(self):
        """Create a shallow copy of the graphics object."""
        return copy.deepcopy(self)

    def reset(self, cmd: Command):
        """Reset the animation with a new command."""
        self.current_cmd = cmd
        self.current_frame = 0
        self.last_update_ms = 0

    def update(self, now_ms: int):
        """Advance animation frame based on game-loop time."""
        if len(self.frames) <= 1:
            return
        if now_ms - self.last_update_ms >= self.frame_time:
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
            self.last_update_ms = now_ms

    def get_img(self) -> Img:
        """Get the current frame image."""
        return self.frames[self.current_frame]
