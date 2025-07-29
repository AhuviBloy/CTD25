"""
Game UI Coordinator for the game board and UI elements
מתאם ממשק המשתמש של המשחק ללוח ואלמנטי UI
"""
import cv2
import numpy as np
import time
import logging
from typing import Dict, List, Any, Tuple

# Import game components
from EventType import EventType
from SoundManager import sound_manager

logger = logging.getLogger(__name__)


class GameUISubscriber:
    """
    Coordinates UI elements and creates board overlay with panels
    מתאם אלמנטי ממשק המשתמש ויוצר שכבת-על ללוח עם פאנלים
    """
    
    def __init__(self, board_width: int = 640, board_height: int = 640):
        # Board dimensions - Made larger for better visibility
        self.board_width = board_width
        self.board_height = board_height
        
        # UI Panel dimensions
        self.panel_width = 250  # Made panels wider too
        self.panel_height = board_height
        
        # Total canvas dimensions - Add space for title and bottom margin
        self.title_height = 80                 # Taller title area for centered board
        self.bottom_margin = 40                # Bottom margin for centered board
        self.total_width = self.panel_width + board_width + self.panel_width  # Left + Board + Right  
        self.total_height = board_height + self.title_height + self.bottom_margin
        
        # Window name for OpenCV
        self.window_name = "KungFu Chess"
        
        # Game state
        self.white_moves: List[str] = []
        self.black_moves: List[str] = []
        self.white_score: int = 0
        self.black_score: int = 0
        self.move_counter: int = 0
        
        # Piece values for scoring
        self.piece_values = {
            'P': 1,  # Pawn
            'N': 3,  # Knight
            'B': 3,  # Bishop
            'R': 5,  # Rook
            'Q': 9,  # Queen
            'K': 0   # King
        }
        
        # Elegant gold and brown color scheme - Luxurious chess theme
        self.bg_color = (245, 235, 215)        # Antique white with gold tint
        self.panel_bg_color = (250, 240, 220)  # Light cream panels
        self.text_color = (101, 67, 33)        # Dark brown text
        self.white_color = (139, 69, 19)       # Saddle brown for white player
        self.black_color = (160, 82, 45)       # Light brown for black player  
        self.accent_color = (218, 165, 32)     # Golden rod accent
        self.highlight_color = (255, 215, 0)   # Gold highlights
        self.success_color = (184, 134, 11)    # Dark golden for captures
        self.border_color = (205, 133, 63)     # Peru brown borders
        
        # Font settings - Better readability with larger board
        self.font = cv2.FONT_HERSHEY_DUPLEX    # More elegant font
        self.font_scale = 0.8                  # Increased for larger panels
        self.font_thickness = 2                # Slightly thicker for better visibility
        self.header_font_scale = 1.0           # Larger headers
        self.header_font_thickness = 2
        
        logger.info("GameUISubscriber initialized")
    
    def handle_event(self, event_type: str, data: Any):
        """Handle game events and update UI state"""
        try:
            if event_type == EventType.GAME_STARTED:
                self._handle_game_started(data)
            elif event_type == EventType.PIECE_MOVED:
                self._handle_piece_moved(data)
            elif event_type == EventType.PIECE_CAPTURED:
                self._handle_piece_captured(data)
            elif event_type == EventType.GAME_ENDED:
                self._handle_game_ended(data)
            elif event_type == EventType.PAWN_PROMOTED:
                self._handle_pawn_promoted(data)
                
        except Exception as e:
            logger.error(f"Error handling event {event_type}: {e}")
    
    def _handle_game_started(self, data):
        """Reset game state for new game"""
        self.white_moves.clear()
        self.black_moves.clear()
        self.white_score = 0
        self.black_score = 0
        self.move_counter = 0
        
        # Play pleasant game start sound
        sound_manager.play_game_start()
        
        logger.info("Game UI reset for new game")
    
    def _handle_piece_moved(self, data):
        """Record a move in the appropriate player's move list"""
        if not hasattr(data, 'piece_id') or not hasattr(data, 'from_cell') or not hasattr(data, 'to_cell'):
            return
            
        # Extract piece info
        piece_type = data.piece_id[0] if len(data.piece_id) >= 1 else 'P'  # P, R, N, B, Q, K
        player_color = data.piece_id[1] if len(data.piece_id) >= 2 else 'W'  # W or B
        
        # Convert cell coordinates to chess notation
        from_notation = self._cell_to_notation(data.from_cell)
        to_notation = self._cell_to_notation(data.to_cell)
        
        # Create move string in new format: "pw a2 -> b2" (lowercase)
        move_str = f"{piece_type.lower()}{player_color.lower()} {from_notation} -> {to_notation}"
        
        # Add to appropriate player's move list
        if player_color == 'W':
            self.white_moves.append(move_str)
        else:
            self.black_moves.append(move_str)
            
        self.move_counter += 1
        
        # Play soft movement sound
        sound_manager.play_piece_move()
        
        logger.info(f"Recorded move: {move_str} for {player_color}")
    
    def _needs_promotion(self, cell: Tuple[int, int], player_color: str) -> bool:
        """Check if a pawn needs promotion based on its position"""
        if not isinstance(cell, (list, tuple)) or len(cell) != 2:
            return False
            
        row, col = cell
        # White pawns promote at row 0 (top), Black pawns promote at row 7 (bottom)
        if player_color == 'W' and row == 0:
            return True
        elif player_color == 'B' and row == 7:
            return True
        return False
    
    def _handle_pawn_promotion(self, move_data):
        """Handle pawn promotion by showing selection dialog"""
        piece_id = move_data.piece_id
        to_cell = move_data.to_cell
        player_color = piece_id[1] if len(piece_id) >= 2 else 'W'
        
        # Show promotion selection dialog
        selected_piece = self._show_promotion_dialog(player_color)
        
        if selected_piece:
            # Create new piece ID with selected piece type
            new_piece_id = f"{selected_piece}{player_color}"
            
            # Update the move notation to include promotion
            if player_color == 'W' and self.white_moves:
                self.white_moves[-1] += f"={selected_piece}"
            elif player_color == 'B' and self.black_moves:
                self.black_moves[-1] += f"={selected_piece}"
            
            # Log the promotion
            logger.info(f"Pawn promoted to {selected_piece} at {self._cell_to_notation(to_cell)}")
            
            # Here you would normally update the game board with the new piece
            # This depends on your game's architecture for piece management
    
    def _show_promotion_dialog(self, player_color: str) -> str:
        """Show promotion selection dialog and return selected piece"""
        # Create promotion dialog window
        dialog_width = 400
        dialog_height = 300
        dialog_x = (self.total_width - dialog_width) // 2
        dialog_y = (self.total_height - dialog_height) // 2
        
        # Create dialog overlay
        dialog_overlay = np.zeros((self.total_height, self.total_width, 3), dtype=np.uint8)
        
        # Semi-transparent background
        dialog_overlay[:] = (20, 15, 10)  # Dark background
        
        # Dialog box background
        cv2.rectangle(dialog_overlay,
                     (dialog_x, dialog_y),
                     (dialog_x + dialog_width, dialog_y + dialog_height),
                     (240, 230, 210), -1)  # Cream background
        
        # Dialog border
        cv2.rectangle(dialog_overlay,
                     (dialog_x - 5, dialog_y - 5),
                     (dialog_x + dialog_width + 5, dialog_y + dialog_height + 5),
                     self.accent_color, 4)  # Golden border
        
        # Title
        title_text = "Choose Promotion Piece"
        title_y = dialog_y + 40
        title_size = cv2.getTextSize(title_text, self.font, 1.0, 2)[0]
        title_x = dialog_x + (dialog_width - title_size[0]) // 2
        cv2.putText(dialog_overlay, title_text, (title_x, title_y),
                   self.font, 1.0, self.text_color, 2)
        
        # Piece options with boxes
        pieces = [
            ('Q', 'Queen'),
            ('R', 'Rook'), 
            ('B', 'Bishop'),
            ('N', 'Knight')
        ]
        
        button_width = 80
        button_height = 60
        button_spacing = 10
        start_x = dialog_x + (dialog_width - (4 * button_width + 3 * button_spacing)) // 2
        button_y = dialog_y + 80
        
        # Draw piece selection buttons
        for i, (piece_code, piece_name) in enumerate(pieces):
            button_x = start_x + i * (button_width + button_spacing)
            
            # Button background
            cv2.rectangle(dialog_overlay,
                         (button_x, button_y),
                         (button_x + button_width, button_y + button_height),
                         self.panel_bg_color, -1)
            
            # Button border
            cv2.rectangle(dialog_overlay,
                         (button_x, button_y),
                         (button_x + button_width, button_y + button_height),
                         self.border_color, 2)
            
            # Piece symbol
            symbol_size = cv2.getTextSize(piece_code, self.font, 1.5, 3)[0]
            symbol_x = button_x + (button_width - symbol_size[0]) // 2
            symbol_y = button_y + 35
            cv2.putText(dialog_overlay, piece_code, (symbol_x, symbol_y),
                       self.font, 1.5, self.accent_color, 3)
            
            # Piece name
            name_size = cv2.getTextSize(piece_name, self.font, 0.5, 1)[0]
            name_x = button_x + (button_width - name_size[0]) // 2
            name_y = button_y + button_height - 10
            cv2.putText(dialog_overlay, piece_name, (name_x, name_y),
                       self.font, 0.5, self.text_color, 1)
        
        # Instructions
        instruction_text = "Press Q, R, B, or N to select"
        instruction_y = dialog_y + 200
        instruction_size = cv2.getTextSize(instruction_text, self.font, 0.7, 1)[0]
        instruction_x = dialog_x + (dialog_width - instruction_size[0]) // 2
        cv2.putText(dialog_overlay, instruction_text, (instruction_x, instruction_y),
                   self.font, 0.7, self.text_color, 1)
        
        # Show dialog in a separate window
        dialog_window_name = "Pawn Promotion"
        cv2.namedWindow(dialog_window_name, cv2.WINDOW_AUTOSIZE)
        cv2.imshow(dialog_window_name, dialog_overlay)
        
        # Wait for key press
        selected_piece = None
        while True:
            key = cv2.waitKey(0) & 0xFF
            
            if key == ord('q') or key == ord('Q'):
                selected_piece = 'Q'
                break
            elif key == ord('r') or key == ord('R'):
                selected_piece = 'R'
                break
            elif key == ord('b') or key == ord('B'):
                selected_piece = 'B'
                break
            elif key == ord('n') or key == ord('N'):
                selected_piece = 'N'
                break
            elif key == 27:  # ESC - default to Queen
                selected_piece = 'Q'
                break
        
        # Close the dialog window only (keep main game window)
        cv2.destroyWindow("Pawn Promotion")
        
        return selected_piece
    
    def _handle_piece_captured(self, data):
        """Update score based on captured piece"""
        if not hasattr(data, 'captured_piece_id') or not hasattr(data, 'capturing_piece_id'):
            return
            
        # Extract captured piece info
        captured_piece_type = data.captured_piece_id[0] if len(data.captured_piece_id) >= 1 else 'P'
        capturing_player = data.capturing_piece_id[1] if len(data.capturing_piece_id) >= 2 else 'W'
        
        # Add points to capturing player
        points = self.piece_values.get(captured_piece_type, 0)
        if capturing_player == 'W':
            self.white_score += points
        else:
            self.black_score += points
            
        # Add capture notation to last move with compact format
        if capturing_player == 'W' and self.white_moves:
            # Get the captured piece color (opposite of capturing player)
            captured_color = 'b' if capturing_player == 'W' else 'w'
            self.white_moves[-1] += f" x{captured_piece_type.lower()}{captured_color}"
        elif capturing_player == 'B' and self.black_moves:
            # Get the captured piece color (opposite of capturing player)  
            captured_color = 'w' if capturing_player == 'B' else 'b'
            self.black_moves[-1] += f" x{captured_piece_type.lower()}{captured_color}"
        
        # Play pleasant capture sound
        sound_manager.play_piece_capture()
            
        logger.info(f"Capture: {capturing_player} gains {points} points (total: {self.white_score if capturing_player == 'W' else self.black_score})")
    
    def _handle_game_ended(self, data):
        """Handle game end with victory announcement"""
        winner = getattr(data, 'winner', 'Unknown')
        
        # Play triumphant victory fanfare
        sound_manager.play_victory()
        
        # Show victory message
        self._show_victory_message(winner)
        
        logger.info(f"Game ended - Winner: {winner}")
    
    def _handle_pawn_promoted(self, data):
        """Handle pawn promotion events by updating move notation"""
        if not hasattr(data, 'old_piece_id') or not hasattr(data, 'promoted_to'):
            return
            
        old_piece_id = data.old_piece_id
        promoted_to = data.promoted_to
        player_color = data.player_color if hasattr(data, 'player_color') else 'W'
        
        # Update the last move in the appropriate player's move list to show promotion
        if player_color == 'W' and self.white_moves:
            # Add promotion notation to the last white move
            self.white_moves[-1] += f"={promoted_to}"
        elif player_color == 'B' and self.black_moves:
            # Add promotion notation to the last black move  
            self.black_moves[-1] += f"={promoted_to}"
        
        # Play special promotion sound
        sound_manager.play_piece_capture()  # Use capture sound for now
        
        logger.info(f"Pawn promotion recorded: {old_piece_id} -> {promoted_to}")
    
    def _show_victory_message(self, winner: str):
        """Display elegant victory message with gold and brown theme"""
        # Determine winner color and name
        if winner == 'W':
            winner_name = "WHITE PLAYER"
            winner_color = self.white_color
        elif winner == 'B':
            winner_name = "BLACK PLAYER" 
            winner_color = self.black_color
        elif winner == 'Draw':
            winner_name = "DRAW"
            winner_color = self.accent_color
        else:
            winner_name = "UNKNOWN"
            winner_color = self.text_color
        
        # Create larger victory window - taking more space
        victory_height = int(self.total_height * 0.7)  # 70% of screen height
        victory_width = int(self.total_width * 0.8)    # 80% of screen width
        victory_x = (self.total_width - victory_width) // 2
        victory_y = (self.total_height - victory_height) // 2
        
        # Create victory overlay with gradient background
        overlay = np.zeros((self.total_height, self.total_width, 3), dtype=np.uint8)
        
        # Create beautiful gradient background for the overlay
        for y in range(self.total_height):
            gradient_factor = y / self.total_height
            gold_factor = 1 - gradient_factor * 0.6
            brown_factor = gradient_factor * 0.4
            
            gradient_color = (
                int(30 * gold_factor + 10 * brown_factor),   # Dark background
                int(25 * gold_factor + 8 * brown_factor),    
                int(20 * gold_factor + 5 * brown_factor)     
            )
            overlay[y, :] = gradient_color
        
        # Create elegant victory box with gold and brown styling
        # Outer golden border
        cv2.rectangle(overlay, 
                     (victory_x - 15, victory_y - 15), 
                     (victory_x + victory_width + 15, victory_y + victory_height + 15), 
                     self.accent_color, 8)  # Thick golden border
        
        # Inner brown border for depth
        cv2.rectangle(overlay, 
                     (victory_x - 8, victory_y - 8), 
                     (victory_x + victory_width + 8, victory_y + victory_height + 8), 
                     self.border_color, 4)
        
        # Victory box background - warm cream color
        victory_bg_color = (240, 230, 210)  # Warm cream background
        cv2.rectangle(overlay, 
                     (victory_x, victory_y), 
                     (victory_x + victory_width, victory_y + victory_height), 
                     victory_bg_color, -1)
        
        # Add decorative corner elements
        corner_size = 40
        corner_margin = 25
        
        # Top corners
        cv2.line(overlay, (victory_x + corner_margin, victory_y + corner_margin), 
                (victory_x + corner_margin + corner_size, victory_y + corner_margin), self.accent_color, 4)
        cv2.line(overlay, (victory_x + corner_margin, victory_y + corner_margin), 
                (victory_x + corner_margin, victory_y + corner_margin + corner_size), self.accent_color, 4)
        
        cv2.line(overlay, (victory_x + victory_width - corner_margin, victory_y + corner_margin), 
                (victory_x + victory_width - corner_margin - corner_size, victory_y + corner_margin), self.accent_color, 4)
        cv2.line(overlay, (victory_x + victory_width - corner_margin, victory_y + corner_margin), 
                (victory_x + victory_width - corner_margin, victory_y + corner_margin + corner_size), self.accent_color, 4)
        
        # Victory text with elegant styling
        font_large = cv2.FONT_HERSHEY_TRIPLEX
        font_medium = cv2.FONT_HERSHEY_DUPLEX
        
        # Large "VICTORY!" title
        title_text = "VICTORY!"
        title_scale = 3.0  # Much larger
        title_thickness = 8
        title_size = cv2.getTextSize(title_text, font_large, title_scale, title_thickness)[0]
        title_x = victory_x + (victory_width - title_size[0]) // 2
        title_y = victory_y + int(victory_height * 0.25)
        
        # Add shadow effect for title
        cv2.putText(overlay, title_text, (title_x + 4, title_y + 4), 
                   font_large, title_scale, (50, 30, 10), title_thickness)  # Dark shadow
        cv2.putText(overlay, title_text, (title_x, title_y), 
                   font_large, title_scale, self.accent_color, title_thickness)  # Golden title
        
        # Winner announcement - larger
        winner_text = f"{winner_name} WINS!"
        winner_scale = 2.0  # Larger winner text
        winner_thickness = 6
        winner_size = cv2.getTextSize(winner_text, font_medium, winner_scale, winner_thickness)[0]
        winner_x = victory_x + (victory_width - winner_size[0]) // 2
        winner_y = victory_y + int(victory_height * 0.45)
        
        # Add shadow for winner text
        cv2.putText(overlay, winner_text, (winner_x + 3, winner_y + 3), 
                   font_medium, winner_scale, (50, 30, 10), winner_thickness)  # Shadow
        cv2.putText(overlay, winner_text, (winner_x, winner_y), 
                   font_medium, winner_scale, winner_color, winner_thickness)  # Winner text
        
        # Decorative line separator
        line_y = victory_y + int(victory_height * 0.55)
        line_margin = 80
        cv2.line(overlay, (victory_x + line_margin, line_y), 
                (victory_x + victory_width - line_margin, line_y), self.accent_color, 4)
        
        # Add decorative elements on the line
        cv2.circle(overlay, (victory_x + victory_width // 2, line_y), 8, self.accent_color, -1)
        cv2.circle(overlay, (victory_x + line_margin, line_y), 6, self.border_color, -1)
        cv2.circle(overlay, (victory_x + victory_width - line_margin, line_y), 6, self.border_color, -1)
        
        # Score display with elegant styling
        score_text = f"Final Score: White {self.white_score} - {self.black_score} Black"
        score_scale = 1.2  # Larger score text
        score_thickness = 3
        score_size = cv2.getTextSize(score_text, font_medium, score_scale, score_thickness)[0]
        score_x = victory_x + (victory_width - score_size[0]) // 2
        score_y = victory_y + int(victory_height * 0.7)
        
        cv2.putText(overlay, score_text, (score_x + 2, score_y + 2), 
                   font_medium, score_scale, (50, 30, 10), score_thickness)  # Shadow
        cv2.putText(overlay, score_text, (score_x, score_y), 
                   font_medium, score_scale, self.text_color, score_thickness)  # Score text
        
        # Exit instruction - elegant styling
        exit_text = "Press any key to continue..."
        exit_scale = 0.9
        exit_thickness = 2
        exit_size = cv2.getTextSize(exit_text, font_medium, exit_scale, exit_thickness)[0]
        exit_x = victory_x + (victory_width - exit_size[0]) // 2
        exit_y = victory_y + int(victory_height * 0.85)
        
        cv2.putText(overlay, exit_text, (exit_x + 1, exit_y + 1), 
                   font_medium, exit_scale, (100, 60, 30), exit_thickness)  # Shadow
        cv2.putText(overlay, exit_text, (exit_x, exit_y), 
                   font_medium, exit_scale, self.border_color, exit_thickness)  # Exit text
        
        # Show victory screen
        cv2.imshow(self.window_name, overlay)
        
        # Wait for any key press before closing
        print(f"🎉 VICTORY! {winner_name} WINS! 🎉")
        print(f"📊 Final Score - White: {self.white_score} | Black: {self.black_score}")
        print("Press any key to exit...")
        
        cv2.waitKey(0)  # Wait for key press
        cv2.destroyAllWindows()  # Close window after key press
    
    def _cell_to_notation(self, cell: Tuple[int, int]) -> str:
        """Convert (row, col) to chess notation like 'e4'"""
        if not isinstance(cell, (list, tuple)) or len(cell) != 2:
            return "??"
            
        row, col = cell
        if 0 <= row <= 7 and 0 <= col <= 7:
            file_letter = chr(ord('a') + col)  # a-h
            rank_number = str(8 - row)         # 8-1 (chess ranks are numbered from white's perspective)
            return f"{file_letter}{rank_number}"
        return "??"
    
    def create_ui_overlay(self, board_img: np.ndarray) -> np.ndarray:
        """
        Create extended UI with board in center and move lists on sides
        Returns new image with board centered and UI panels on left and right
        """
        try:
            # Convert RGBA to RGB if needed
            if board_img.shape[2] == 4:  # RGBA
                board_img = cv2.cvtColor(board_img, cv2.COLOR_RGBA2RGB)
            
            # Create canvas with gradient background - full screen
            canvas = self._create_gradient_background()
            
            # Add game title centered above board
            self._draw_game_title(canvas)
            
            # Resize board image to fit our board area
            if board_img.shape[:2] != (self.board_height, self.board_width):
                board_resized = cv2.resize(board_img, (self.board_width, self.board_height))
            else:
                board_resized = board_img.copy()
            
            # Add subtle border around subtle border around board
            board_y_offset = self.title_height
            self._add_board_border(canvas, self.panel_width, board_y_offset)
            
            # Add board
            board_y_offset = self.title_height
            self._add_board_border(canvas, self.panel_width, board_y_offset)
            
            # Place board in center (with title offset)
            board_x = self.panel_width
            board_y = board_y_offset
            canvas[board_y:board_y + self.board_height, board_x:board_x + self.board_width] = board_resized
            
            # Draw left panel (Black player) with styling
            self._draw_styled_player_panel(canvas, 0, "Black", self.black_moves, self.black_score, "black")
            
            # Draw right panel (White player) with styling
            right_x = self.panel_width + self.board_width
            self._draw_styled_player_panel(canvas, right_x, "White", self.white_moves, self.white_score, "white")
            
            return canvas
            
        except Exception as e:
            logger.error(f"Error creating UI overlay: {e}")
            return board_img
    
    def _draw_player_panel(self, canvas: np.ndarray, x_offset: int, player_name: str, 
                          moves: List[str], score: int, player_color: Tuple[int, int, int]):
        """Draw a player's panel with score and move list"""
        try:
            y = 20
            
            # Player name and score
            score_text = f"{player_name}: {score}"
            cv2.putText(canvas, score_text, (x_offset + 10, y), 
                       self.font, self.font_scale, self.text_color, self.font_thickness)
            y += 30
            
            # Underline
            cv2.line(canvas, (x_offset + 10, y), (x_offset + self.panel_width - 10, y), 
                    self.text_color, 1)
            y += 20
            
            # Move list
            move_text = "Moves:"
            cv2.putText(canvas, move_text, (x_offset + 10, y), 
                       self.font, self.font_scale - 0.1, self.text_color, self.font_thickness)
            y += 25
            
            # Display last 15 moves (to fit in panel)
            visible_moves = moves[-15:] if len(moves) > 15 else moves
            for i, move in enumerate(visible_moves):
                move_num = len(moves) - len(visible_moves) + i + 1
                move_display = f"{move_num}. {move}"
                
                # Truncate long moves
                if len(move_display) > 18:
                    move_display = move_display[:15] + "..."
                    
                cv2.putText(canvas, move_display, (x_offset + 10, y), 
                           self.font, self.font_scale - 0.1, self.text_color, self.font_thickness)
                y += 20
                
                # Don't exceed panel height
                if y > self.panel_height - 30:
                    break
                    
        except Exception as e:
            logger.error(f"Error drawing player panel: {e}")

    def _create_gradient_background(self) -> np.ndarray:
        """Create a beautiful gold and brown gradient background"""
        canvas = np.zeros((self.total_height, self.total_width, 3), dtype=np.uint8)
        
        # Create warm gold to brown gradient
        for y in range(self.total_height):
            # Calculate gradient factor (0 to 1)
            gradient_factor = y / self.total_height
            
            # Create warm gold to brown gradient
            gold_factor = 1 - gradient_factor * 0.4
            brown_factor = gradient_factor * 0.3
            
            gradient_color = (
                int(245 * gold_factor + 139 * brown_factor),  # Blue channel - gold to brown
                int(235 * gold_factor + 69 * brown_factor),   # Green channel
                int(215 * gold_factor + 19 * brown_factor)    # Red channel - warm tones
            )
            canvas[y, :] = gradient_color
            
        return canvas
    
    def _add_board_border(self, canvas: np.ndarray, x: int, y: int):
        """Add simple border around the game board"""
        border_thickness = 2
        
        # Simple single border
        cv2.rectangle(canvas, 
                     (x - border_thickness, y - border_thickness),
                     (x + self.board_width + border_thickness, y + self.board_height + border_thickness),
                     self.accent_color, border_thickness)
    
    def _draw_styled_player_panel(self, canvas: np.ndarray, x_offset: int, player_name: str,
                                 moves: List[str], score: int, player_type: str):
        """Draw clean player panel directly on background"""
        try:
            # No panel background - draw directly on gradient background
            # Start lower to give more space around the board
            y = self.title_height + 20
            
            # Simple player header
            self._draw_player_header(canvas, x_offset, y, player_name, score, player_type)
            y += 80
            
            # Simple moves section
            cv2.putText(canvas, "Moves", (x_offset + 20, y),
                       self.font, self.font_scale, self.accent_color, self.font_thickness)
            y += 30
            
            # Simple move list
            self._draw_enhanced_move_list(canvas, x_offset, y, moves, player_type)
            
        except Exception as e:
            logger.error(f"Error drawing styled player panel: {e}")
    
    def _draw_panel_background(self, canvas: np.ndarray, x_offset: int):
        """Draw styled panel background"""
        panel_start_y = self.title_height + 5
        panel_end_y = self.total_height - 5
        
        # Main panel background
        cv2.rectangle(canvas,
                     (x_offset + 5, panel_start_y),
                     (x_offset + self.panel_width - 5, panel_end_y),
                     self.panel_bg_color, -1)
        
        # Subtle border
        cv2.rectangle(canvas,
                     (x_offset + 5, panel_start_y), 
                     (x_offset + self.panel_width - 5, panel_end_y),
                     self.border_color, 1)
        
        # Corner accent lines
        cv2.line(canvas, 
                (x_offset + 5, panel_start_y), (x_offset + 25, panel_start_y),
                self.accent_color, 2)
        cv2.line(canvas,
                (x_offset + 5, panel_start_y), (x_offset + 5, panel_start_y + 20), 
                self.accent_color, 2)
    
    def _draw_game_title(self, canvas: np.ndarray):
        """Draw title centered above the board"""
        title_text = "KungFu Chess"
        
        # Calculate center position above the board
        board_center_x = self.panel_width + (self.board_width // 2)
        title_y = self.title_height - 25  # Position above the board
        
        # Calculate text width for perfect centering
        text_size = cv2.getTextSize(title_text, self.font, 1.3, 3)[0]
        title_x = board_center_x - (text_size[0] // 2)
        
        # Draw title centered above board
        cv2.putText(canvas, title_text, (title_x, title_y),
                   self.font, 1.3, self.accent_color, 3)
    
    def _draw_player_header(self, canvas: np.ndarray, x_offset: int, y: int, 
                          player_name: str, score: int, player_type: str):
        """Draw clean and simple player header"""
        # Simple player name only
        name_color = self.text_color
        cv2.putText(canvas, player_name, (x_offset + 20, y),
                   self.font, self.header_font_scale, name_color, self.header_font_thickness)
        
        # Score below name - simple text only
        score_text = f"Score: {score}"
        cv2.putText(canvas, score_text, (x_offset + 20, y + 35),
                   self.font, self.font_scale, self.text_color, self.font_thickness)
    
    def _draw_section_header(self, canvas: np.ndarray, x_offset: int, y: int, title: str):
        """Draw section header with underline"""
        cv2.putText(canvas, title, (x_offset + 15, y),
                   self.font, self.font_scale + 0.1, self.accent_color, self.font_thickness + 1)
        
        # Decorative underline
        cv2.line(canvas,
                (x_offset + 15, y + 5),
                (x_offset + self.panel_width - 15, y + 5),
                self.accent_color, 2)
    
    def _draw_enhanced_move_list(self, canvas: np.ndarray, x_offset: int, y: int,
                                moves: List[str], player_type: str):
        """Draw clean and simple move list"""
        visible_moves = moves[-8:] if len(moves) > 8 else moves  # Show fewer moves
        
        for i, move in enumerate(visible_moves):
            move_num = len(moves) - len(visible_moves) + i + 1
            
            # Simple move display - just number and move
            move_display = f"{move_num}. {move}"
            
            # Truncate long moves more aggressively
            if len(move_display) > 18:
                move_display = move_display[:15] + "..."
            
            # Simple text color - highlight captures with "x" symbol  
            text_color = self.success_color if ' x' in move else self.text_color
            
            # Draw the move text simply with smaller font
            cv2.putText(canvas, move_display, (x_offset + 20, y),
                       self.font, self.font_scale - 0.3, text_color, self.font_thickness)
            
            y += 25  # Compact spacing for more moves
            
            # Don't exceed panel height
            if y > self.total_height - 80:
                break
    
    def get_subscribed_events(self):
        """Return list of events this subscriber listens to"""
        return [
            EventType.GAME_STARTED,
            EventType.PIECE_MOVED, 
            EventType.PIECE_CAPTURED,
            EventType.GAME_ENDED,
            EventType.PAWN_PROMOTED
        ]
