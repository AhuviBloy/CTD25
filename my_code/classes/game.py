# import queue, time
# import cv2                # ← הוסף
# from .command import Command



# class Game:
#     def __init__(self, pieces:list['Piece'], board:'Board'):
#         self.pieces = {p.id: p for p in pieces}
#         self.board  = board
#         self.user_input_queue: queue.Queue[Command] = queue.Queue()
#         self.running = True

#     def enqueue_command(self, cmd:Command):
#         self.user_input_queue.put(cmd)
#     def _process_input(self, cmd:Command):
#         if cmd.piece_id in self.pieces:
#             self.pieces[cmd.piece_id].on_command(cmd)


#     def run(self):
#         last = time.time()
#         selected_piece_id = None

#         # פונקציית עכבר: בודקת על איזה כלי נלחץ
#         def mouse_callback(event, x, y, flags, param):
#             nonlocal selected_piece_id
#             if event == cv2.EVENT_LBUTTONDOWN:
#                 col = x // self.board.cell_W_pix
#                 row = y // self.board.cell_H_pix
#                 # חפש כלי שנמצא בתא הזה
#                 for piece in self.pieces.values():
#                     p_col, p_row = piece.state.physics.get_cell()
#                     if (col, row) == (p_col, p_row):
#                         selected_piece_id = piece.id
#                         print(f"נבחר: {selected_piece_id}")
#                         break

#         cv2.namedWindow("game")
#         cv2.setMouseCallback("game", mouse_callback)

#         while self.running:
#             now = time.time()
#             dt = (now-last)*1000
#             last = now

#             # קלט מקלדת
#             key = cv2.waitKey(10)
#             if key == 27:
#                 self.running = False
#             # if cv2.getWindowProperty("game", cv2.WND_PROP_VISIBLE) < 1:
#             #     self.running = False

#             # אם יש כלי נבחר, שלח לו פקודת תנועה לפי החץ שנלחץ
#             if selected_piece_id is not None:
#                 if key == 81:  # חץ שמאל
#                     self.enqueue_command(Command(selected_piece_id, "LEFT"))
#                 elif key == 82:  # חץ למעלה
#                     self.enqueue_command(Command(selected_piece_id, "UP"))
#                 elif key == 83:  # חץ ימין
#                     self.enqueue_command(Command(selected_piece_id, "RIGHT"))
#                 elif key == 84:  # חץ למטה
#                     self.enqueue_command(Command(selected_piece_id, "DOWN"))

#             # עיבוד פקודות
#             while not self.user_input_queue.empty():
#                 self._process_input(self.user_input_queue.get())

#             # עדכון חיילים
#             for p in self.pieces.values():
#                 p.update(dt)

#             # ציור
#             self._draw()

#         cv2.destroyAllWindows()



#     # --------------------------------------------------
#     def _draw(self):
#         canvas = self.board.clone()           # Board לציור
#         for p in self.pieces.values():        # ← values!
#             p.draw(canvas)
#         canvas.img.show("game")




#     # def run(self):
#     #     last = time.time()
#     #     while self.running:
#     #         now = time.time()
#     #         dt = (now-last)*1000
#     #         last = now

#     #         # קלט משתמש
#     #         while not self.user_input_queue.empty():
#     #             self._process_input(self.user_input_queue.get())

#     #         # עדכון חיילים
#     #         for p in self.pieces.values():
#     #             p.update(dt)

#     #         # ציור
#     #         self._draw()

#     #         # סגירה ב-ESC או ב-X
#     #         if cv2.waitKey(10) == 27:
#     #             self.running = False
#     #         # # בדיקה אם החלון נסגר ע"י X
#     #         if cv2.getWindowProperty("game", cv2.WND_PROP_VISIBLE) < 1:
#     #             self.running = False

#     #     cv2.destroyAllWindows()
        
#     # def run(self):
#     #     last = time.time()
#     #     while self.running:
#     #         now = time.time()
#     #         dt = (now-last)*1000
#     #         last = now

#     #         # קלט משתמש
#     #         while not self.user_input_queue.empty():
#     #             self._process_input(self.user_input_queue.get())

#     #         # עדכון חיילים
#     #         for p in self.pieces.values():
#     #             p.update(dt)

#     #         # ציור
#     #         self._draw()

#     #         if cv2.waitKey(10) == 27:      # ESC → יציאה
#     #             self.running = False

#     #     cv2.destroyAllWindows()


import queue
import time
import cv2
from .command import Command

class Game:
    def __init__(self, pieces: list['Piece'], board: 'Board'):
        self.pieces = {p.id: p for p in pieces}
        self.board = board
        self.user_input_queue: queue.Queue[Command] = queue.Queue()
        self.running = True

    def enqueue_command(self, cmd: Command):
        self.user_input_queue.put(cmd)

    def _process_input(self, cmd: Command):
        if cmd.piece_id in self.pieces:
            self.pieces[cmd.piece_id].on_command(cmd)

    # def run(self):
    #     last = time.time()
    #     selected_piece_id = None

    #     # פונקציה לטיפול בלחיצות עכבר
    #     def mouse_callback(event, x, y, flags, param):
    #         nonlocal selected_piece_id
    #         if event == cv2.EVENT_LBUTTONDOWN:
    #             col = x // self.board.cell_W_pix
    #             row = y // self.board.cell_H_pix
    #             for piece in self.pieces.values():
    #                 p_col, p_row = piece.state.physics.cell
    #                 # p_col, p_row = piece.state.physics.get_cell()
    #                 if (col, row) == (p_col, p_row):
    #                     selected_piece_id = piece.id
    #                     print(f"Selected piece: {selected_piece_id}")
    #                     break

    #     cv2.namedWindow("game")
    #     cv2.setMouseCallback("game", mouse_callback)

    #     while self.running:
    #         now = time.time()
    #         dt = (now - last) * 1000  # dt במילישניות
    #         last = now

    #         key = cv2.waitKey(10)

    #         if key == 10:  # ESC ליציאה
    #             self.running = False

    #         # שליחת פקודות תנועה לפי מקשי החצים אם כלי נבחר
    #         if selected_piece_id:
    #             if key == 81:  # חץ שמאל
    #                 self.enqueue_command(Command(selected_piece_id, "LEFT"))
    #             elif key == 82:  # חץ למעלה
    #                 self.enqueue_command(Command(selected_piece_id, "UP"))
    #             elif key == 83:  # חץ ימין
    #                 self.enqueue_command(Command(selected_piece_id, "RIGHT"))
    #             elif key == 84:  # חץ למטה
    #                 self.enqueue_command(Command(selected_piece_id, "DOWN"))

    #         # עיבוד פקודות שהגיעו
    #         while not self.user_input_queue.empty():
    #             self._process_input(self.user_input_queue.get())

    #         # עדכון כלים
    #         for p in self.pieces.values():
    #             p.update(dt)

    #         # ציור כל הכלים על הלוח
    #         self._draw()

    #     cv2.destroyAllWindows()
    def run(self):
        last = time.time()
        selected_piece_id = None

        # פונקציה לטיפול בלחיצות עכבר
        def mouse_callback(event, x, y, flags, param):
            nonlocal selected_piece_id
            if event == cv2.EVENT_LBUTTONDOWN:
                col = x // self.board.cell_W_pix
                row = y // self.board.cell_H_pix
                for piece in self.pieces.values():
                    p_row, p_col = piece.state.physics.cell
                    if (row, col) == (p_row, p_col):
                        selected_piece_id = piece.id
                        print(f"Selected piece: {selected_piece_id}")
                        break

        cv2.namedWindow("game")
        cv2.setMouseCallback("game", mouse_callback)

        while self.running:
            now = time.time()
            dt = (now - last) * 1000  # dt במילישניות
            last = now

            key = cv2.waitKey(10)

            if key == 10:  # ESC ליציאה
                self.running = False

            # שליחת פקודות תנועה לפי מקשי החצים אם כלי נבחר
            if selected_piece_id:
                current_cell = self.pieces[selected_piece_id].state.physics.cell
                new_cell = None

                if key == 81:  # LEFT
                    new_cell = (current_cell[0], current_cell[1] - 1)
                elif key == 82:  # UP
                    new_cell = (current_cell[0] - 1, current_cell[1])
                elif key == 83:  # RIGHT
                    new_cell = (current_cell[0], current_cell[1] + 1)
                elif key == 84:  # DOWN
                    new_cell = (current_cell[0] + 1, current_cell[1])

                # לוודא שהתא החדש בגבולות הלוח
                if new_cell and 0 <= new_cell[0] < self.board.rows and 0 <= new_cell[1] < self.board.cols:
                    cmd = Command(selected_piece_id, "MOVE", target_cell=new_cell)
                    self.enqueue_command(cmd)

            # עיבוד פקודות שהגיעו
            while not self.user_input_queue.empty():
                self._process_input(self.user_input_queue.get())

            # עדכון כלים
            for p in self.pieces.values():
                p.update(dt)

            # ציור כל הכלים על הלוח
            self._draw()

        cv2.destroyAllWindows()
    def _draw(self):
        canvas = self.board.clone()
        now_ms = int(time.time() * 1000)  # הזמן הנוכחי במילישניות
        for p in self.pieces.values():
            p.draw_on_board(canvas, now_ms)   # כאן שולחים גם את הלוח וגם את הזמן
        canvas.img.show("game")
