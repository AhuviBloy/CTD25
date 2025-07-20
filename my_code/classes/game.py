# import queue, time
# from .command import Command

# class Game:
#     def __init__(self, pieces:list['Piece'], board:'Board'):
#         self.pieces = {p.id: p for p in pieces}
#         self.board  = board
#         self.user_input_queue: queue.Queue[Command] = queue.Queue()
#         self.running = True

#     def enqueue_command(self, cmd:Command): self.user_input_queue.put(cmd)

#     def _process_input(self, cmd:Command):
#         if cmd.piece_id in self.pieces:
#             self.pieces[cmd.piece_id].on_command(cmd)

#     def run(self):
#         last = time.time()
#         while self.running:
#             now = time.time(); dt = (now-last)*1000; last = now
#             while not self.user_input_queue.empty():
#                 self._process_input(self.user_input_queue.get())
#             for p in self.pieces.values(): p.update(dt)
#             self._draw()
#             if cv2.waitKey(10) == 27:  # ESC לסגור
#                 self.running = False
#         cv2.destroyAllWindows()

#     def _draw(self):
#         canvas = self.board.clone()        # Board חדש לציור
#         for p in self.pieces:
#             p.draw(canvas)                 # ← שולחים Board, לא (canvas, x, y)
#         canvas.img.show("game")
















import queue, time
import cv2                     # ← הוסף
from .command import Command

class Game:
    def __init__(self, pieces:list['Piece'], board:'Board'):
        self.pieces = {p.id: p for p in pieces}
        self.board  = board
        self.user_input_queue: queue.Queue[Command] = queue.Queue()
        self.running = True

    def enqueue_command(self, cmd:Command):
        self.user_input_queue.put(cmd)

    def _process_input(self, cmd:Command):
        if cmd.piece_id in self.pieces:
            self.pieces[cmd.piece_id].on_command(cmd)

    def run(self):
        last = time.time()
        while self.running:
            now = time.time()
            dt = (now-last)*1000
            last = now

            # קלט משתמש
            while not self.user_input_queue.empty():
                self._process_input(self.user_input_queue.get())

            # עדכון חיילים
            for p in self.pieces.values():
                p.update(dt)

            # ציור
            self._draw()

            if cv2.waitKey(10) == 27:      # ESC → יציאה
                self.running = False

        cv2.destroyAllWindows()

    # --------------------------------------------------
    def _draw(self):
        canvas = self.board.clone()           # Board לציור
        for p in self.pieces.values():        # ← values!
            p.draw(canvas)
        canvas.img.show("game")
