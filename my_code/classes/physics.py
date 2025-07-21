# class Physics:
#     def __init__(self, board:'Board', speed:float=1.0):
#         self.board = board
#         self.speed = speed
#         self.x = self.y = 0
#     def reset(self, cell:tuple[int,int]): self.x,self.y = cell
#     def update(self, dt_ms:int): pass   # add interpolation if תרצי
#     def get_cell(self): return int(self.x), int(self.y)

from typing import Tuple, Optional
from .command import Command
import math

class Physics:
    SLIDE_CELLS_PER_SEC = 4.0  # tweak to make all pieces slower/faster

    def __init__(self, start_cell: Tuple[int, int],
                 board: "Board", speed_m_s: float = 1.0):
        self.board = board
        self.speed_m_s = speed_m_s
        self.cell = start_cell  # תא נוכחי (שורה, עמודה)
        self.pixel_pos = self.board.cell_to_pixel(start_cell)  # מיקום פיקסל נוכחי
        self.cmd: Optional[Command] = None
        self.start_time_ms: Optional[int] = None
        self.start_pixel_pos = self.pixel_pos
        self.target_cell: Optional[Tuple[int, int]] = None
        self.target_pixel_pos: Optional[Tuple[int, int]] = None
        self.moving = False

    def reset(self, cmd: Command):
        """Reset physics state with a new command."""
        self.cmd = cmd
        self.start_time_ms = None  # יתעדכן ב-update הראשון
        self.start_pixel_pos = self.pixel_pos
        self.target_cell = cmd.target_cell
        self.target_pixel_pos = self.board.cell_to_pixel(self.target_cell)
        self.moving = True

    def update(self, now_ms: int):
        """Update physics state based on current time."""
        if not self.moving or not self.cmd:
            return

        if self.start_time_ms is None:
            self.start_time_ms = now_ms

        # חישוב מרחק וזמן תנועה
        dx = self.target_pixel_pos[0] - self.start_pixel_pos[0]
        dy = self.target_pixel_pos[1] - self.start_pixel_pos[1]
        distance = math.hypot(dx, dy)

        if distance == 0:
            self.moving = False
            return

        speed_px_per_ms = (self.SLIDE_CELLS_PER_SEC * self.board.cell_size) / 1000.0
        duration_ms = distance / speed_px_per_ms if speed_px_per_ms > 0 else 1

        elapsed = now_ms - self.start_time_ms
        t = min(1.0, elapsed / duration_ms)

        # עדכון מיקום
        new_x = int(self.start_pixel_pos[0] + dx * t)
        new_y = int(self.start_pixel_pos[1] + dy * t)
        self.pixel_pos = (new_x, new_y)

        if t >= 1.0:
            self.pixel_pos = self.target_pixel_pos
            self.cell = self.target_cell
            self.moving = False

    def can_be_captured(self) -> bool:
        """Check if this piece can be captured."""
        # ברירת מחדל: כל כלי יכול להיתפס
        return True

    def can_capture(self) -> bool:
        """Check if this piece can capture other pieces."""
        # ברירת מחדל: כל כלי יכול לתפוס
        return True

    def get_pos(self) -> Tuple[int, int]:
        """
        Current pixel-space upper-left corner of the sprite.
        Uses the sub-pixel coordinate computed in update();
        falls back to the square's origin before the first update().
        """
        return self.pixel_pos