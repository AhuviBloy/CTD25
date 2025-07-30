
# # server.py
# # שלד ראשוני של סרבר TCP שמאזין ל-5000 ומחזיר echo


# import socket
# import json
# import sys
# import pathlib
# sys.path.append(str(pathlib.Path(__file__).parent / "KFC_Py"))
# from shared_types import GameState, ServerResponse, ClientMessage, MESSAGE_TYPES, PLAYERS
# import threading

# HOST = '127.0.0.1'
# PORT = 5000



# # --- אתחול מצב פתיחה אמיתי מהקבצים ---
# import pathlib
# from KFC_Py.Board import Board
# from KFC_Py.PieceFactory import PieceFactory
# from KFC_Py.GraphicsFactory import GraphicsFactory, ImgFactory
# from KFC_Py.img import Img

# def init_gamestate_from_csv():
#     pieces_dir = pathlib.Path(__file__).parent / "pieces"
#     board_img_path = pieces_dir / "board.png"
#     board_csv_path = pieces_dir / "board.csv"
#     if not board_img_path.exists() or not board_csv_path.exists():
#         print("[SERVER] board.png or board.csv not found! (משחק יתחיל ריק)")
#         return GameState(
#             pieces={},
#             pos_to_piece={},
#             current_player=PLAYERS["WHITE"],
#             game_time_ms=0,
#             white_score=0,
#             black_score=0,
#             game_ended=False,
#             winner=None,
#             last_move=None
#         )
#     board_img = Img().read(str(board_img_path))
#     board = Board(
#         cell_H_pix=100,
#         cell_W_pix=100,
#         W_cells=8,
#         H_cells=8,
#         img=board_img
#     )
#     gfx_factory = GraphicsFactory(ImgFactory())
#     pf = PieceFactory(board, pieces_dir, graphics_factory=gfx_factory)
#     pieces = {}
#     pos_to_piece = {}
#     with open(board_csv_path) as f:
#         for r, line in enumerate(f):
#             for c, code in enumerate(line.strip().split(",")):
#                 if code:
#                     piece = pf.create_piece(code, (r, c))
#                     pieces[piece.id] = {
#                         "id": code,
#                         "position": (r, c),
#                         "unique_id": piece.id
#                     }
#                     pos_to_piece[f"{r},{c}"] = piece.id
#     return GameState(
#         pieces=pieces,
#         pos_to_piece=pos_to_piece,
#         current_player=PLAYERS["WHITE"],
#         game_time_ms=0,
#         white_score=0,
#         black_score=0,
#         game_ended=False,
#         winner=None,
#         last_move=None
#     )

# game_state = init_gamestate_from_csv()

# clients = []  # רשימת חיבורים פתוחים
# lock = threading.Lock()

# def handle_client(conn, addr):
#     print(f"[SERVER] Connected by {addr}")
#     with lock:
#         clients.append(conn)
#         # שלח ללקוח החדש את מצב הפתיחה מיד
#         msg = {
#             "type": MESSAGE_TYPES["GAME_UPDATE"],
#             "game_state": game_state.to_dict()
#         }
#         try:
#             conn.sendall((json.dumps(msg) + "\n").encode())
#         except Exception as e:
#             print(f"[SERVER] Error sending initial GAME_UPDATE: {e}")
#     try:
#         while True:
#             data = conn.recv(4096)
#             if not data:
#                 break
#             try:
#                 msg = json.loads(data.decode())
#                 print(f"[SERVER] Received: {msg}")
#                 # המרת dict ל-ClientMessage
#                 if isinstance(msg, dict) and "type" in msg:
#                     client_msg = ClientMessage.from_dict(msg)
#                     resp, broadcast = handle_message(client_msg)
#                     # שלח תשובה אישית
#                     conn.sendall((json.dumps(resp.to_dict()) + "\n").encode())
#                     # אם צריך לשדר לכולם (למשל עדכון משחק) - שלח לכל הלקוחות
#                     if broadcast:
#                         broadcast_game_update()
#                 else:
#                     # תשובת echo לברירת מחדל
#                     response = {"echo": msg}
#                     conn.sendall((json.dumps(response) + "\n").encode())
#             except Exception as e:
#                 print(f"[SERVER] Error: {e}")
#                 break
#     finally:
#         with lock:
#             if conn in clients:
#                 clients.remove(conn)
#         conn.close()
#         print(f"[SERVER] Connection with {addr} closed.")

# def handle_message(msg: ClientMessage):
#     global game_state
#     # broadcast = האם צריך לשדר לכולם (move, התחלת משחק וכו')
#     broadcast = False
#     with lock:
#         if msg.type == MESSAGE_TYPES["GET_STATE"]:
#             return ServerResponse(success=True, message="Game state", game_state=game_state), False
#         elif msg.type == MESSAGE_TYPES["MOVE"]:
#             # דוגמה: רק מחליף current_player
#             prev = game_state.current_player
#             game_state.current_player = PLAYERS["BLACK"] if prev == PLAYERS["WHITE"] else PLAYERS["WHITE"]
#             game_state.last_move = msg.data
#             broadcast = True
#             return ServerResponse(success=True, message="Move accepted", game_state=game_state), broadcast
#         else:
#             return ServerResponse(success=False, message="Unknown message type", error_code="UNKNOWN_TYPE"), False

# def broadcast_game_update():
#     global game_state
#     with lock:
#         msg = {
#             "type": MESSAGE_TYPES["GAME_UPDATE"],
#             "game_state": game_state.to_dict()
#         }
#         dead = []
#         for conn in clients:
#             try:
#                 conn.sendall((json.dumps(msg) + "\n").encode())
#             except Exception as e:
#                 print(f"[SERVER] Broadcast error: {e}")
#                 dead.append(conn)
#         for conn in dead:
#             clients.remove(conn)

# def main():
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         s.bind((HOST, PORT))
#         s.listen()
#         print(f"[SERVER] Listening on {HOST}:{PORT}")
#         while True:
#             conn, addr = s.accept()
#             threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

# if __name__ == "__main__":
#     main()

# server_ws.py






import asyncio
import websockets
import json
import sys
import pathlib
import logging
from typing import Dict

# הגדרת לוגים
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# הוספת תיקיית KFC_Py לפייתון פאת'
sys.path.append(str(pathlib.Path(__file__).parent / "KFC_Py"))

from shared_types import GameState, ServerResponse, ClientMessage, MESSAGE_TYPES, PLAYERS
from KFC_Py.Board import Board
from KFC_Py.PieceFactory import PieceFactory
from KFC_Py.GraphicsFactory import GraphicsFactory, ImgFactory
from KFC_Py.img import Img


# ---------------- אתחול מצב משחק ----------------
def init_gamestate_from_csv():
    pieces_dir = pathlib.Path(__file__).parent / "pieces"
    board_img_path = pieces_dir / "board.png"
    board_csv_path = pieces_dir / "board.csv"
    if not board_img_path.exists() or not board_csv_path.exists():
        print("[SERVER] board.png or board.csv not found! (משחק יתחיל ריק)")
        return GameState(
            pieces={},
            pos_to_piece={},
            current_player=PLAYERS["WHITE"],
            game_time_ms=0,
            white_score=0,
            black_score=0,
            game_ended=False,
            winner=None,
            last_move=None
        )
    board_img = Img().read(str(board_img_path))
    board = Board(
        cell_H_pix=100,
        cell_W_pix=100,
        W_cells=8,
        H_cells=8,
        img=board_img
    )
    gfx_factory = GraphicsFactory(ImgFactory())
    pf = PieceFactory(board, pieces_dir, graphics_factory=gfx_factory)
    pieces = {}
    pos_to_piece = {}
    with open(board_csv_path) as f:
        for r, line in enumerate(f):
            for c, code in enumerate(line.strip().split(",")):
                if code:
                    piece = pf.create_piece(code, (r, c))
                    pieces[piece.id] = {
                        "id": code,
                        "position": (r, c),
                        "unique_id": piece.id
                    }
                    pos_to_piece[f"{r},{c}"] = piece.id
    return GameState(
        pieces=pieces,
        pos_to_piece=pos_to_piece,
        current_player=PLAYERS["WHITE"],
        game_time_ms=0,
        white_score=0,
        black_score=0,
        game_ended=False,
        winner=None,
        last_move=None
    )


# ---------------- מחלקת השרת ----------------
class ChessServer:
    def __init__(self):
        self.clients: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.game_state = init_gamestate_from_csv()
        logger.info("✅ ChessServer initialized")

    async def handle_client(self, websocket):
        """טיפול בחיבור לקוח חדש"""
        player_id = str(id(websocket))  # מזהה זמני
        self.clients[player_id] = websocket
        logger.info(f"🔗 New client connected: {player_id}")

        # שליחת מצב פתיחה
        await websocket.send(json.dumps({
            "type": MESSAGE_TYPES["GAME_UPDATE"],
            "game_state": self.game_state.to_dict()
        }))

        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    client_msg = ClientMessage.from_dict(data)
                    logger.info(f"📨 Received {client_msg.type} from {player_id}")

                    resp, broadcast = self.handle_message(client_msg)

                    # שליחת תשובה אישית
                    await websocket.send(json.dumps(resp.to_dict()))

                    # אם צריך לשדר לכולם
                    if broadcast:
                        await self.broadcast_game_update()

                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    await websocket.send(json.dumps({
                        "success": False,
                        "message": f"Server error: {e}"
                    }))
        finally:
            logger.info(f"❌ Client disconnected: {player_id}")
            if player_id in self.clients:
                del self.clients[player_id]

    def handle_message(self, msg: ClientMessage):
        broadcast = False
        if msg.type == MESSAGE_TYPES["GET_STATE"]:
            return ServerResponse(success=True, message="Game state", game_state=self.game_state), False
        elif msg.type == MESSAGE_TYPES["MOVE"]:
            prev = self.game_state.current_player
            self.game_state.current_player = PLAYERS["BLACK"] if prev == PLAYERS["WHITE"] else PLAYERS["WHITE"]
            self.game_state.last_move = msg.data
            broadcast = True
            return ServerResponse(success=True, message="Move accepted", game_state=self.game_state), broadcast
        else:
            return ServerResponse(success=False, message="Unknown message type", error_code="UNKNOWN_TYPE"), False

    async def broadcast_game_update(self):
        msg = {
            "type": MESSAGE_TYPES["GAME_UPDATE"],
            "game_state": self.game_state.to_dict()
        }
        dead = []
        for pid, ws in self.clients.items():
            try:
                await ws.send(json.dumps(msg))
            except:
                dead.append(pid)
        for pid in dead:
            del self.clients[pid]


# ---------------- main ----------------
async def main():
    server = ChessServer()
    print("🌐 Starting Chess Server on ws://localhost:8889")
    async with websockets.serve(server.handle_client, "localhost", 8889):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
