import queue, threading, time, math, logging
from typing import List, Dict, Tuple, Optional, Set
from collections import defaultdict

from Board import Board
from Command import Command
from Piece import Piece
from GameEventPublisher import game_event_publisher
from EventType import EventType
from GameUISubscriber import GameUISubscriber
from SoundManager import SoundManager

from KeyboardInput import KeyboardProcessor, KeyboardProducer

# set up a module-level logger – real apps can configure handlers/levels
logger = logging.getLogger(__name__)


class InvalidBoard(Exception): ...


class Game:
    def __init__(self, pieces: List[Piece], board: Board, pieces_root=None, graphics_factory=None):
        self.pieces = pieces
        self.board = board
        self.pieces_root = pieces_root  # Add pieces root for creating new pieces
        self.graphics_factory = graphics_factory  # Add graphics factory
        self.curr_board = None
        self.user_input_queue = queue.Queue()
        self.piece_by_id = {p.id: p for p in pieces}
        self.pos: Dict[Tuple[int, int], List[Piece]] = defaultdict(list)
        self.START_NS = time.time_ns()
        self._time_factor = 1  
        self.kp1 = None
        self.kp2 = None
        self.kb_prod_1 = None
        self.kb_prod_2 = None
        self.selected_id_1: Optional[str] = None
        self.selected_id_2: Optional[str] = None  
        self.last_cursor1 = (0, 0)
        self.last_cursor2 = (0, 0)
        
        # Event publisher for Pub/Sub system
        self.event_publisher = game_event_publisher
        
        # Sound manager for game audio
        self.sound_manager = SoundManager()

    def game_time_ms(self) -> int:
        return self._time_factor * (time.monotonic_ns() - self.START_NS) // 1_000_000

    def clone_board(self) -> Board:
        return self.board.clone()

    def start_user_input_thread(self):

        # player 1 key‐map
        p1_map = {
            "up": "up", "down": "down", "left": "left", "right": "right",
            "enter": "select"
        }
        # player 2 key‐map
        p2_map = {
            "w": "up", "s": "down", "a": "left", "d": "right",
             "space": "select"
        }

        # create two processors with initial positions
        # Player 1 (white) starts at bottom (row 7), Player 2 (black) starts at top (row 0)
        self.kp1 = KeyboardProcessor(self.board.H_cells,
                                     self.board.W_cells,
                                     keymap=p1_map,
                                     initial_pos=(7, 0))  # White pieces start at bottom
        self.kp2 = KeyboardProcessor(self.board.H_cells,
                                     self.board.W_cells,
                                     keymap=p2_map,
                                     initial_pos=(0, 0))  # Black pieces start at top

        # **pass the player number** as the 4th argument!
        self.kb_prod_1 = KeyboardProducer(self,
                                          self.user_input_queue,
                                          self.kp1,
                                          player=1)
        self.kb_prod_2 = KeyboardProducer(self,
                                          self.user_input_queue,
                                          self.kp2,
                                          player=2)

        self.kb_prod_1.start()
        self.kb_prod_2.start()

    def _update_cell2piece_map(self):
        self.pos.clear()
        for p in self.pieces:
            self.pos[p.current_cell()].append(p)

    def _run_game_loop(self, num_iterations=None, is_with_graphics=True):
        it_counter = 0
        while not self._is_win():
            now = self.game_time_ms()

            for p in self.pieces:
                p.update(now)

            self._update_cell2piece_map()

            while not self.user_input_queue.empty():
                cmd: Command = self.user_input_queue.get()
                self._process_input(cmd)

            if is_with_graphics:
                self._draw()
                self._show()

            self._resolve_collisions()

            # for testing
            if num_iterations is not None:
                it_counter += 1
                if num_iterations <= it_counter:
                    return

    def run(self, num_iterations=None, is_with_graphics=True):
        # יצירת UI subscriber
        self.ui_subscriber = GameUISubscriber()
        
        # רישום ה-UI subscriber למערכת הודעות
        from MessageBroker import game_message_broker
        for event_type in self.ui_subscriber.get_subscribed_events():
            game_message_broker.subscribe(event_type, self.ui_subscriber.handle_event)
        
        # רישום מאזין לאירועי תזוזה לצלילים ולהכתרה
        game_message_broker.subscribe(EventType.PIECE_MOVED, lambda event_type, data: self._on_piece_moved(data))
        
        # Subscribe to pawn promotion events to handle piece replacement
        game_message_broker.subscribe(EventType.PAWN_PROMOTED, lambda event_type, data: self._on_pawn_promoted(data))
        
        # Publish game started event
        self.event_publisher.publish_game_started("White Player", "Black Player")
        
        self.start_user_input_thread()
        start_ms = self.START_NS
        for p in self.pieces:
            p.reset(start_ms)

        self._run_game_loop(num_iterations, is_with_graphics)

        self._announce_win()
        if self.kb_prod_1:
            self.kb_prod_1.stop()
            self.kb_prod_2.stop()

    def _draw(self):
        self.curr_board = self.clone_board()
        for p in self.pieces:
            p.draw_on_board(self.curr_board, now_ms=self.game_time_ms())

        # overlay both players' cursors, but only log on change
        if self.kp1 and self.kp2:
            for player, kp, last in (
                    (1, self.kp1, 'last_cursor1'),
                    (2, self.kp2, 'last_cursor2')
            ):
                r, c = kp.get_cursor()
                # draw rectangle
                y1 = r * self.board.cell_H_pix
                x1 = c * self.board.cell_W_pix
                y2 = y1 + self.board.cell_H_pix - 1
                x2 = x1 + self.board.cell_W_pix - 1
                
                # Change cursor color based on selection state
                # Red if piece is selected, normal color otherwise
                has_selection = False
                if player == 1 and self.selected_id_1 is not None:
                    has_selection = True
                elif player == 2 and self.selected_id_2 is not None:
                    has_selection = True
                
                if has_selection:
                    color = (0, 0, 255)  # Red for selected state
                else:
                    color = (0, 255, 0) if player == 1 else (255, 0, 0)  # Normal colors
                    
                self.curr_board.img.draw_rect(x1, y1, x2, y2, color)

                # only print if moved
                prev = getattr(self, last)
                if prev != (r, c):
                    logger.debug("Marker P%s moved to (%s, %s)", player, r, c)
                    setattr(self, last, (r, c))
        
        # יצירת UI מורחבת עם טבלאות מהלכים וניקוד
        if hasattr(self, 'ui_subscriber'):
            # העברת תמונת הלוח הנוכחית ל-UI subscriber
            enhanced_board_img = self.ui_subscriber.create_ui_overlay(self.curr_board.img.img)
            # עדכון התמונה במבנה הלוח
            self.curr_board.img.img = enhanced_board_img

    def _show(self):
        self.curr_board.show()

    def _side_of(self, piece_id: str) -> str:
        return piece_id[1]

    def _process_input(self, cmd: Command):
        mover = self.piece_by_id.get(cmd.piece_id)
        if not mover:
            logger.debug("Unknown piece id %s", cmd.piece_id)
            return

        # Store piece position before move for event publishing
        piece_position_before = mover.current_cell()

        # Process the command - Piece.on_command() determines my_color internally
        mover.on_command(cmd, self.pos)
        
        # Publish move event if it was a move command and piece actually moved
        if cmd.type == "move" and len(cmd.params) >= 2:
            from_cell = cmd.params[0]
            to_cell = cmd.params[1]
            # Only publish if the piece's state actually changed (move was accepted)
            if mover.state.name == "move":  # Piece entered moving state
                self.event_publisher.publish_piece_moved(cmd.piece_id, from_cell, to_cell)
        
        logger.info(f"Processed command: {cmd} for piece {cmd.piece_id}")

    def _resolve_collisions(self):
        self._update_cell2piece_map()
        occupied = self.pos

        for cell, plist in occupied.items():
            if len(plist) < 2:
                continue

            logger.debug(f"Collision detected at {cell}: {[p.id for p in plist]}")

            # Choose the piece that most recently entered the square
            # But prioritize pieces that are actually moving over idle pieces
            moving_pieces = [p for p in plist if p.state.name != 'idle']
            if moving_pieces:
                winner = max(moving_pieces, key=lambda p: p.state.physics.get_start_ms())
                logger.debug(f"Winner (moving): {winner.id} (state: {winner.state.name})")
            else:
                # If no moving pieces, choose the most recent idle piece
                winner = max(plist, key=lambda p: p.state.physics.get_start_ms())
                logger.debug(f"Winner (idle): {winner.id} (state: {winner.state.name})")

            # Determine if captures allowed: default allow
            if not winner.state.can_capture():
                # Allow capture even for idle pieces to satisfy game rules
                pass

            # Remove every other piece that *can be captured*
            for p in plist:
                if p is winner:
                    continue
                if p.state.can_be_captured():
                    logger.debug(f"Checking if {p.id} can be captured (state: {p.state.name})")
                    
                    # Don't remove knights that are moving (they're jumping in the air)
                    if p.id.startswith(('NW', 'NB')) and p.state.name == 'move':
                        logger.debug(f"Knight {p.id} is moving (jumping) - not removing")
                        continue
                    # Don't remove pieces that are jumping (they're in the air)
                    if p.state.name == 'jump':
                        logger.debug(f"Piece {p.id} is jumping - not removing")
                        continue
                    # Don't remove pieces if the winner is jumping (winner is in the air)
                    if winner.state.name == 'jump':
                        logger.debug(f"Winner {winner.id} is jumping - not removing {p.id}")
                        continue
                    # Don't remove pieces if the winner is a knight moving (knight is jumping in the air)
                    if winner.id.startswith(('NW', 'NB')) and winner.state.name == 'move':
                        logger.debug(f"Winner knight {winner.id} is moving (jumping) - not removing {p.id}")
                        continue
                    
                    # Don't capture pieces of the same color (friendly pieces)
                    if winner.id[1] == p.id[1]:  # Same color (W/B)
                        logger.debug(f"Winner {winner.id} and {p.id} are same color - not capturing")
                        continue
                    
                    logger.info(f"CAPTURE: {winner.id} captures {p.id} at {cell}")
                    
                    # Publish piece captured event
                    self.event_publisher.publish_piece_captured(p.id, winner.id, cell)
                    
                    self.pieces.remove(p)
                else:
                    logger.debug(f"Piece {p.id} cannot be captured (state: {p.state.name})")

        # After all collisions are resolved, handle pawn promotions
        # This ensures pawns capture pieces before being promoted
        for piece in self.pieces[:]:  # Use slice to iterate over copy
            cell = piece.current_cell()
            if self._needs_pawn_promotion(piece, cell):
                print(f"DEBUG: Pawn promotion detected for {piece.id} at {cell}")
                self._handle_pawn_promotion(piece, cell)

    def _validate(self, pieces):
        """Ensure both kings present and no two pieces share a cell."""
        has_white_king = has_black_king = False
        seen_cells: dict[tuple[int, int], str] = {}
        for p in pieces:
            cell = p.current_cell()
            if cell in seen_cells:
                # Allow overlap only if piece is from opposite side
                if seen_cells[cell] == p.id[1]:
                    return False
            else:
                seen_cells[cell] = p.id[1]
            if p.id.startswith("KW"):
                has_white_king = True
            elif p.id.startswith("KB"):
                has_black_king = True
        return has_white_king and has_black_king

    def _is_win(self) -> bool:
        kings = [p for p in self.pieces if p.id.startswith(('KW', 'KB'))]
        return len(kings) < 2

    def _announce_win(self):
        # Determine winner by which king is still on the board
        black_king_alive = any(p.id.startswith('KB') for p in self.pieces)
        white_king_alive = any(p.id.startswith('KW') for p in self.pieces)
        
        if black_king_alive and not white_king_alive:
            winner = 'B'  # Black wins
            winner_name = 'Black Player'
        elif white_king_alive and not black_king_alive:
            winner = 'W'  # White wins  
            winner_name = 'White Player'
        else:
            winner = 'Draw'  # Should not happen in normal gameplay
            winner_name = 'Draw'
        
        text = f'{winner_name} wins!'
        
        # Publish game ended event with single letter code
        self.event_publisher.publish_game_ended(winner, "checkmate")
        
        print(text)
    
    def _on_piece_moved(self, event_data):
        """Handle piece moved events and play appropriate sounds"""
        piece_id = event_data.piece_id
        from_cell = event_data.from_cell  
        to_cell = event_data.to_cell
        
        # Check if this was a jump (more than one cell distance)
        if abs(from_cell[0] - to_cell[0]) > 1 or abs(from_cell[1] - to_cell[1]) > 1:
            # This was a jump
            self.sound_manager.play_piece_jump()
        else:
            # This was a regular move
            self.sound_manager.play_piece_move()

        logger.debug(f"Played sound for piece {piece_id} moving from {from_cell} to {to_cell}")
    
    def _needs_pawn_promotion(self, piece, cell: tuple) -> bool:
        """Check if a pawn needs promotion based on its position"""
        # Check if it's a pawn
        if not piece.id.startswith('P'):
            # print(f"DEBUG: {piece.id} is not a pawn")
            return False
            
        row, col = cell
        player_color = piece.id[1] if len(piece.id) >= 2 else 'W'
        
        # print(f"DEBUG: Checking promotion for {piece.id} at row {row}, player color {player_color}")
        
        # White pawns promote at row 0 (top), Black pawns promote at row 7 (bottom)
        if player_color == 'W' and row == 0:
            print(f"DEBUG: White pawn promotion needed!")
            return True
        elif player_color == 'B' and row == 7:
            print(f"DEBUG: Black pawn promotion needed!")
            return True
        
        # print(f"DEBUG: No promotion needed")
        return False
    
    def _handle_pawn_promotion(self, pawn_piece, cell: tuple):
        """Handle pawn promotion by creating a new piece and replacing the old one"""
        from PieceFactory import PieceFactory
        
        player_color = pawn_piece.id[1] if len(pawn_piece.id) >= 2 else 'W'
        old_piece_id = pawn_piece.id
        
        print(f"DEBUG: Starting pawn promotion for {old_piece_id} at {cell}")
        
        # Show promotion dialog to get user choice
        promoted_to = self._get_promotion_choice(player_color)
        
        print(f"DEBUG: User chose to promote to {promoted_to}")
        
        if promoted_to:
            # Create new piece ID
            new_piece_type = f"{promoted_to}{player_color}"
            # Use timestamp to ensure unique identifier
            import time
            unique_id = int(time.time() * 1000) % 10000  # Last 4 digits of milliseconds
            new_piece_id = f"{promoted_to}{player_color}_{unique_id}"
            
            print(f"DEBUG: Creating new piece {new_piece_type} with ID {new_piece_id}")
            
            # Create new piece at the promotion position if we have pieces_root
            if self.pieces_root:
                print(f"DEBUG: pieces_root available: {self.pieces_root}")
                pf = PieceFactory(self.board, self.pieces_root, graphics_factory=self.graphics_factory)
                new_piece = pf.create_piece(new_piece_type, cell)
                new_piece.id = new_piece_id
                
                # Give the new piece the same state timing as the original pawn to maintain priority
                # This ensures the promoted piece inherits the movement timing and wins collisions
                if hasattr(pawn_piece.state, 'physics') and hasattr(pawn_piece.state.physics, 'get_start_ms'):
                    current_timestamp = pawn_piece.state.physics.get_start_ms()
                    # Reset the new piece state with current timestamp to maintain collision priority
                    new_piece.state.reset(Command(current_timestamp, new_piece.id, "move", [cell]))
                
                print(f"DEBUG: Created new piece {new_piece.id} with inherited timing")
                
                # Replace the old piece with the new piece
                self._replace_piece(pawn_piece, new_piece)
                
                # Publish promotion event
                self.event_publisher.publish_pawn_promoted(old_piece_id, new_piece_id, cell, promoted_to)
                
                print(f"DEBUG: Promotion completed!")
                logger.info(f"Pawn {old_piece_id} promoted to {promoted_to} at {cell}")
            else:
                print(f"DEBUG: pieces_root not available!")
                logger.warning("Cannot create promoted piece: pieces_root not available")
    
    def _get_promotion_choice(self, player_color: str) -> str:
        """Get promotion choice from user using UI dialog"""
        # Use the UI subscriber's promotion dialog
        if hasattr(self, 'ui_subscriber') and self.ui_subscriber:
            choice = self.ui_subscriber._show_promotion_dialog(player_color)
            # Force refresh of main game window after dialog
            try:
                import cv2
                # Ensure main game window is active
                cv2.namedWindow("Image", cv2.WINDOW_AUTOSIZE)
                cv2.setWindowProperty("Image", cv2.WND_PROP_TOPMOST, 1)
                cv2.setWindowProperty("Image", cv2.WND_PROP_TOPMOST, 0)
            except:
                pass
            return choice
        else:
            # Fallback to Queen if no UI available
            return 'Q'
    
    def _replace_piece(self, old_piece, new_piece):
        """Replace an old piece with a new piece in all game structures"""
        # Remove old piece from pieces list
        if old_piece in self.pieces:
            self.pieces.remove(old_piece)
        
        # Remove from piece_by_id mapping
        if old_piece.id in self.piece_by_id:
            del self.piece_by_id[old_piece.id]
        
        # Add new piece
        self.pieces.append(new_piece)
        self.piece_by_id[new_piece.id] = new_piece
        
        # Update position mapping
        self._update_cell2piece_map()
    
    def _on_pawn_promoted(self, event_data):
        """Handle pawn promotion events"""
        old_piece_id = event_data.old_piece_id
        new_piece_id = event_data.new_piece_id
        promoted_to = event_data.promoted_to
        
        logger.info(f"Pawn promotion completed: {old_piece_id} -> {new_piece_id} ({promoted_to})")