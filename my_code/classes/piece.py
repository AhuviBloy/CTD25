# from .command import Command
# class Piece:
#     def __init__(self, piece_id:str, start_state:'State'):
#         self.id   = piece_id
#         self.state= start_state
#     def on_command(self, cmd:Command):
#         self.state = self.state.on_command(cmd.type)
#     def update(self, dt): self.state.update(dt)
#     def draw(self, board:'Board'):
#         x,y = self.state.physics.get_cell()
#         self.state.draw(board.img, x*board.cell_W_pix, y*board.cell_H_pix)


# my_code/classes/piece.py



# from __future__ import annotations
# from .command import Command
# from .state   import State

# class Piece:
#     def __init__(self, piece_id: str, init_state: State):
#         self.id       = piece_id
#         self.state    = init_state
#         self.idle_ms  = 0          # מתי חזר לאחרונה לאידל
#         self.cooldown = 200        # לדוגמה: 200 ms קירור

#     # ---------- API הרשמי ---------- #
#     def on_command(self, cmd: Command, now_ms: int):
#         """מעדכן מצב + מתחיל cooldown"""
#         self.state = self.state.on_command(cmd.type)
#         self.idle_ms = now_ms

#     def reset(self, start_ms: int):
#         self.state.reset()
#         self.idle_ms = start_ms

#     def update(self, now_ms: int):
#         dt = now_ms - self.idle_ms
#         self.state.update(dt)

#     def draw_on_board(self, board: "Board", now_ms: int):
#         """
#         מצייר את החייל במרכז התא; אם הוא ב‑cool‑down מוסיף חצי‑שקף
#         """
#         # מיקום התא
#         col, row = self.state.physics.get_cell()
#         cw, ch   = board.cell_W_pix, board.cell_H_pix

#         sprite = self.state.graphics.current()
#         sh, sw = sprite.img.shape[:2]
#         x_pix  = col*cw + (cw-sw)//2
#         y_pix  = row*ch + (ch-sh)//2
#         sprite.draw_on(board.img, x_pix, y_pix)

#         # ----------------- overlay cooldown -----------------
#         if now_ms - self.idle_ms < self.cooldown:
#             import cv2
#             alpha = 0.4
#             overlay = board.img.img.copy()
#             cv2.rectangle(overlay, (x_pix, y_pix),
#                           (x_pix+sw, y_pix+sh), (0,0,255,120), -1)
#             cv2.addWeighted(overlay, alpha,
#                             board.img.img, 1-alpha, 0, board.img.img)

#     # ---------- התאמה אחורנית (לוגיקה קיימת) ---------- #
#     # פונקציות קצרות שמפנות לממשק החדש, כדי שקוד ישן לא יישבר
#     def on_command_short(self, cmd: Command):
#         self.on_command(cmd, 0)
#     def draw(self, board: "Board"):
#         self.draw_on_board(board, 0)


from .board import Board
from .command import Command
from .state import State
import cv2

class Piece:
    def __init__(self, piece_id: str, init_state: State):
        """Initialize a piece with ID and initial state."""
        self.id = piece_id
        self.state = init_state
        self.cooldown_ms = 0  # זמן המתנה (למשל אחרי פעולה)
        self.last_update_ms = 0

    def on_command(self, cmd: Command, now_ms: int):
        """Handle a command for this piece."""
        # מציאת יעד חדש לפי כיוון
        row, col = self.state.physics.cell
        if cmd.type == "UP":
            new_cell = (col, row - 1)
        elif cmd.type == "DOWN":
            new_cell = (col, row + 1)
        elif cmd.type == "LEFT":
            new_cell = (col - 1, row)
        elif cmd.type == "RIGHT":
            new_cell = (col + 1, row)
        else:
            new_cell = (col, row)

        cmd.target_cell = new_cell  # יעד התנועה

        # הפעלת מעבר מצב רגיל
        next_state = self.state.get_state_after_command(cmd, now_ms)
        if next_state:
            self.state = next_state
        self.state.reset(cmd)
        # """Handle a command for this piece."""
        # # אם המצב יכול להשתנות בעקבות פקודה, נעשה זאת
        # next_state = self.state.get_state_after_command(cmd, now_ms)
        # if next_state:
        #     self.state = next_state
        #     self.state.reset(cmd)

    def reset(self, start_ms: int):
        """Reset the piece to idle state."""
        self.state.reset(Command(timestamp=start_ms, piece_id=self.piece_id, type="Idle", params=[]))
        self.last_update_ms = start_ms

    def update(self, now_ms: int):
        """Update the piece state based on current time."""
        self.state = self.state.update(now_ms)
        self.last_update_ms = now_ms

    def draw_on_board(self, board: Board, now_ms: int):
        """Draw the piece on the board with cooldown overlay."""
        img = self.state.graphics.get_img()
        pos = self.state.physics.get_pos()
        if isinstance(pos, tuple) and len(pos) == 2:
            pos_x, pos_y = pos
        else:
            pos_x, pos_y = (0, 0)  # fallback for mocks
        img.draw_on(board.img, pos_x, pos_y)
