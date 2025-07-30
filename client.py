

# client.py
# מאזין להודעות מהשרת, ובכל GAME_UPDATE מצייר את הלוח והחיילים

import asyncio
import websockets
import json
from shared_types import MESSAGE_TYPES, GameState
import threading
import queue
import time
import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent / "KFC_Py"))
from KFC_Py.Board import Board
from KFC_Py.img import Img


from KFC_Py.GameFactory import create_game
from KFC_Py.GraphicsFactory import ImgFactory

WS_URL = 'ws://localhost:8889'



# --- יצירת אובייקט Game מלא ---
game = None
input_queue = queue.Queue()
def draw_board_from_gamestate(game_state: GameState):
    global game
    pieces_dir = pathlib.Path(__file__).parent / "pieces"
    if game is None:
        game = create_game(pieces_dir, ImgFactory())
        game.user_input_queue = input_queue
        # Start the full UI/game loop in a thread (so we can update board from server)
        def run_game():
            try:
                game.run(is_with_graphics=True)
            except Exception as e:
                print(f"[CLIENT] Game UI error: {e}")
        threading.Thread(target=run_game, daemon=True).start()
    # Update only the board state from the server
    for piece_id, pdata in game_state.pieces.items():
        pos = pdata.get("position")
        if pos is not None and piece_id in game.piece_by_id:
            piece = game.piece_by_id[piece_id]
            if hasattr(piece, 'state') and hasattr(piece.state, 'physics'):
                piece.state.physics._cell = tuple(pos)
    print(f"[CLIENT] Synced board. Current player: {game_state.current_player}")

async def listen_to_server():
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("[CLIENT] Connected to server. Waiting for updates...")

            # Start a thread to listen for local user input and send to server
            def input_sender():
                while True:
                    cmd = input_queue.get()
                    # Send move/jump command to server
                    msg = {
                        "type": MESSAGE_TYPES["MOVE"],
                        "player_id": "user1",  # TODO: support real player id
                        "data": {
                            "timestamp": cmd.timestamp,
                            "piece_id": cmd.piece_id,
                            "type": cmd.type,
                            "params": cmd.params
                        }
                    }
                    asyncio.run_coroutine_threadsafe(websocket.send(json.dumps(msg)), asyncio.get_event_loop())

            threading.Thread(target=input_sender, daemon=True).start()

            async for message in websocket:
                try:
                    msg_obj = json.loads(message)
                    if msg_obj.get("type") == MESSAGE_TYPES["GAME_UPDATE"]:
                        gs = GameState.from_dict(msg_obj["game_state"])
                        draw_board_from_gamestate(gs)
                    else:
                        print(f"[CLIENT] Received: {msg_obj}")
                except Exception as e:
                    print(f"[CLIENT] JSON error: {e}")
    except Exception as e:
        print(f"[CLIENT] Connection error: {e}")

def main():
    asyncio.run(listen_to_server())

if __name__ == "__main__":
    main()

