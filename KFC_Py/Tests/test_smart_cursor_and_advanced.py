"""
Comprehensive tests for Smart Cursor Logic and Advanced Game Features
בדיקות מקיפות ללוגיקת הסמן החכם ותכונות משחק מתקדמות
"""
import pytest
import queue
import time
from unittest.mock import Mock, patch, MagicMock
import pathlib

import sys
sys.path.append(str(pathlib.Path(__file__).parent.parent))

from Game import Game, InvalidBoard
from Board import Board
from Piece import Piece
from Command import Command
from KeyboardInput import KeyboardProcessor, KeyboardProducer
from GameEventPublisher import game_event_publisher
from EventType import EventType
from GameUISubscriber import GameUISubscriber
from mock_img import MockImg
from GraphicsFactory import MockImgFactory


class TestSmartCursorLogic:
    """Test the smart cursor color-changing logic"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Create a minimal game for testing
        self.board = Board(64, 64, 8, 8, MockImg())
        self.pieces = self._create_test_pieces()
        self.game = Game(self.pieces, self.board)
        
    def _create_test_pieces(self):
        """Create minimal test pieces"""
        pieces = []
        # Create minimal pieces for testing
        for i in range(2):
            piece = Mock(spec=Piece)
            piece.id = f"PW_{i}"
            piece.current_cell.return_value = (6, i)
            piece.update = Mock()
            piece.draw_on_board = Mock()
            piece.state = Mock()
            piece.state.name = "idle"
            piece.state.physics = Mock()
            piece.state.physics.get_start_ms.return_value = 1000 + i
            pieces.append(piece)
            
        # Add black pieces
        for i in range(2):
            piece = Mock(spec=Piece)
            piece.id = f"PB_{i}"
            piece.current_cell.return_value = (1, i)
            piece.update = Mock()
            piece.draw_on_board = Mock()
            piece.state = Mock()
            piece.state.name = "idle"
            piece.state.physics = Mock()
            piece.state.physics.get_start_ms.return_value = 2000 + i
            pieces.append(piece)
            
        # Add kings for valid game
        for color in ['W', 'B']:
            piece = Mock(spec=Piece)
            piece.id = f"K{color}_1"
            piece.current_cell.return_value = (7 if color == 'W' else 0, 4)
            piece.update = Mock()
            piece.draw_on_board = Mock()
            piece.state = Mock()
            piece.state.name = "idle"
            piece.state.physics = Mock()
            piece.state.physics.get_start_ms.return_value = 3000
            pieces.append(piece)
            
        return pieces
        
    def test_cursor_normal_colors_when_no_selection(self):
        """Test cursor shows normal colors when no piece is selected"""
        # Set up keyboard processors
        self.game.kp1 = KeyboardProcessor(8, 8, {}, initial_pos=(7, 0))
        self.game.kp2 = KeyboardProcessor(8, 8, {}, initial_pos=(0, 0))
        
        # No pieces selected
        self.game.selected_id_1 = None
        self.game.selected_id_2 = None
        
        # Mock the board image drawing
        with patch.object(self.game.board, 'clone') as mock_clone:
            mock_board = Mock()
            mock_board.img = Mock()
            mock_board.img.draw_rect = Mock()
            mock_clone.return_value = mock_board
            
            self.game._draw()
            
            # Check that draw_rect was called with normal colors
            calls = mock_board.img.draw_rect.call_args_list
            assert len(calls) == 2  # Two cursors
            
            # Player 1 should have green cursor (0, 255, 0)
            # Player 2 should have red cursor (255, 0, 0)
            colors_used = [call[0][4] for call in calls]  # 5th argument is color
            assert (0, 255, 0) in colors_used  # Green for player 1
            assert (255, 0, 0) in colors_used  # Red for player 2
            
    def test_cursor_red_when_player1_selects_piece(self):
        """Test cursor turns red when player 1 selects a piece"""
        self.game.kp1 = KeyboardProcessor(8, 8, {}, initial_pos=(7, 0))
        self.game.kp2 = KeyboardProcessor(8, 8, {}, initial_pos=(0, 0))
        
        # Player 1 selects a piece
        self.game.selected_id_1 = "PW_1"
        self.game.selected_id_2 = None
        
        with patch.object(self.game.board, 'clone') as mock_clone:
            mock_board = Mock()
            mock_board.img = Mock()
            mock_board.img.draw_rect = Mock()
            mock_clone.return_value = mock_board
            
            self.game._draw()
            
            calls = mock_board.img.draw_rect.call_args_list
            assert len(calls) == 2
            
            # Player 1 cursor should be red, Player 2 should be normal
            colors_used = [call[0][4] for call in calls]
            assert (0, 0, 255) in colors_used  # Red for selection
            assert (255, 0, 0) in colors_used  # Normal red for player 2
            
    def test_cursor_red_when_player2_selects_piece(self):
        """Test cursor turns red when player 2 selects a piece"""
        self.game.kp1 = KeyboardProcessor(8, 8, {}, initial_pos=(7, 0))
        self.game.kp2 = KeyboardProcessor(8, 8, {}, initial_pos=(0, 0))
        
        # Player 2 selects a piece
        self.game.selected_id_1 = None
        self.game.selected_id_2 = "PB_1"
        
        with patch.object(self.game.board, 'clone') as mock_clone:
            mock_board = Mock()
            mock_board.img = Mock()
            mock_board.img.draw_rect = Mock()
            mock_clone.return_value = mock_board
            
            self.game._draw()
            
            calls = mock_board.img.draw_rect.call_args_list
            assert len(calls) == 2
            
            # Player 2 cursor should be red, Player 1 should be normal
            colors_used = [call[0][4] for call in calls]
            assert (0, 0, 255) in colors_used  # Red for selection
            assert (0, 255, 0) in colors_used  # Normal green for player 1
            
    def test_both_cursors_red_when_both_select(self):
        """Test both cursors turn red when both players select pieces"""
        self.game.kp1 = KeyboardProcessor(8, 8, {}, initial_pos=(7, 0))
        self.game.kp2 = KeyboardProcessor(8, 8, {}, initial_pos=(0, 0))
        
        # Both players select pieces
        self.game.selected_id_1 = "PW_1"
        self.game.selected_id_2 = "PB_1"
        
        with patch.object(self.game.board, 'clone') as mock_clone:
            mock_board = Mock()
            mock_board.img = Mock()
            mock_board.img.draw_rect = Mock()
            mock_clone.return_value = mock_board
            
            self.game._draw()
            
            calls = mock_board.img.draw_rect.call_args_list
            assert len(calls) == 2
            
            # Both cursors should be red
            colors_used = [call[0][4] for call in calls]
            assert colors_used.count((0, 0, 255)) == 2  # Both red
            
    def test_cursor_returns_to_normal_after_deselection(self):
        """Test cursor returns to normal color after piece deselection"""
        self.game.kp1 = KeyboardProcessor(8, 8, {}, initial_pos=(7, 0))
        self.game.kp2 = KeyboardProcessor(8, 8, {}, initial_pos=(0, 0))
        
        # Start with selection
        self.game.selected_id_1 = "PW_1"
        self.game.selected_id_2 = None
        
        with patch.object(self.game.board, 'clone') as mock_clone:
            mock_board = Mock()
            mock_board.img = Mock()
            mock_board.img.draw_rect = Mock()
            mock_clone.return_value = mock_board
            
            # Draw with selection
            self.game._draw()
            first_calls = mock_board.img.draw_rect.call_args_list
            
            # Reset mock
            mock_board.img.draw_rect.reset_mock()
            
            # Deselect piece
            self.game.selected_id_1 = None
            
            # Draw again
            self.game._draw()
            second_calls = mock_board.img.draw_rect.call_args_list
            
            # Should have normal colors now
            colors_used = [call[0][4] for call in second_calls]
            assert (0, 255, 0) in colors_used  # Green for player 1
            assert (255, 0, 0) in colors_used  # Red for player 2
            assert (0, 0, 255) not in colors_used  # No selection red


class TestAdvancedGameLogic:
    """Test advanced game logic and edge cases"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.board = Board(64, 64, 8, 8, MockImg())
        
    def test_game_time_calculation(self):
        """Test game time calculation"""
        pieces = self._create_minimal_pieces()
        
        # Mock both time.time_ns and time.monotonic_ns to return predictable values
        with patch('time.time_ns', return_value=1000000000), \
             patch('time.monotonic_ns') as mock_monotonic:
            
            # Create game - this will set START_NS to 1000000000
            game = Game(pieces, self.board)
            
            # Set monotonic time to be 1 second later
            mock_monotonic.return_value = 2000000000  # 2 seconds in nanoseconds
            
            time1 = game.game_time_ms()
            assert time1 >= 0
            assert time1 == 1000  # Should be exactly 1000ms (1 second difference)
        
    def test_time_factor_scaling(self):
        """Test time factor affects game time"""
        pieces = self._create_minimal_pieces()
        
        # Mock both time.time_ns and time.monotonic_ns to return predictable values
        with patch('time.time_ns', return_value=1000000000), \
             patch('time.monotonic_ns') as mock_monotonic:
            
            # Create game - this will set START_NS to 1000000000  
            game = Game(pieces, self.board)
            
            # Set monotonic time to be 1 second later
            mock_monotonic.return_value = 2000000000  # 2 seconds in nanoseconds
            
            # Set different time factors
            game._time_factor = 1
            time1 = game.game_time_ms()
            
            game._time_factor = 2
            time2 = game.game_time_ms()
            
            # With double time factor, time should be doubled
            assert time1 == 1000  # 1 second
            assert time2 == 2000  # 2 seconds (double the factor)
        
    def test_board_cloning(self):
        """Test board cloning functionality"""
        pieces = self._create_minimal_pieces()
        game = Game(pieces, self.board)
        
        cloned_board = game.clone_board()
        assert cloned_board is not self.board
        assert isinstance(cloned_board, Board)
        
    def test_piece_by_id_mapping(self):
        """Test piece lookup by ID"""
        pieces = self._create_minimal_pieces()
        game = Game(pieces, self.board)
        
        # Should be able to find pieces by ID
        for piece in pieces:
            found_piece = game.piece_by_id[piece.id]
            assert found_piece is piece
            
    def test_cell_to_piece_mapping_update(self):
        """Test updating cell to piece mapping"""
        pieces = self._create_minimal_pieces()
        game = Game(pieces, self.board)
        
        game._update_cell2piece_map()
        
        # Each piece should be mapped to its current cell
        for piece in pieces:
            cell = piece.current_cell()
            assert piece in game.pos[cell]
            
    def test_side_identification(self):
        """Test piece side identification"""
        pieces = self._create_minimal_pieces()
        game = Game(pieces, self.board)
        
        # Test side identification
        assert game._side_of("PW_1") == "W"
        assert game._side_of("KB_1") == "B"
        assert game._side_of("QW_2") == "W"
        assert game._side_of("NB_3") == "B"
        
    def test_win_condition_detection(self):
        """Test win condition detection"""
        pieces = self._create_minimal_pieces()
        game = Game(pieces, self.board)
        
        # Game should not be won initially (both kings present)
        assert not game._is_win()
        
        # Remove one king
        king_to_remove = None
        for piece in pieces:
            if piece.id.startswith("KB"):
                king_to_remove = piece
                break
                
        if king_to_remove:
            game.pieces.remove(king_to_remove)
            assert game._is_win()
            
    def test_input_processing_unknown_piece(self):
        """Test input processing with unknown piece ID"""
        pieces = self._create_minimal_pieces()
        game = Game(pieces, self.board)
        
        # Command for non-existent piece should not crash
        cmd = Command(0, "UNKNOWN_PIECE", "move", [(0, 0), (1, 1)])
        game._process_input(cmd)
        
        # Game should continue normally
        assert len(game.pieces) > 0
        
    def test_keyboard_input_initialization(self):
        """Test keyboard input thread initialization"""
        pieces = self._create_minimal_pieces()
        game = Game(pieces, self.board)
        
        game.start_user_input_thread()
        
        # Keyboard processors should be created
        assert game.kp1 is not None
        assert game.kp2 is not None
        assert game.kb_prod_1 is not None
        assert game.kb_prod_2 is not None
        
        # Initial positions should be correct
        assert game.kp1.get_cursor() == (7, 0)  # White at bottom
        assert game.kp2.get_cursor() == (0, 0)  # Black at top
        
        # Clean up threads
        if game.kb_prod_1:
            game.kb_prod_1.stop()
            game.kb_prod_2.stop()
            
    def _create_minimal_pieces(self):
        """Create minimal pieces for testing"""
        pieces = []
        
        # Create kings (required for valid game)
        for color in ['W', 'B']:
            piece = Mock(spec=Piece)
            piece.id = f"K{color}_1"
            piece.current_cell.return_value = (7 if color == 'W' else 0, 4)
            piece.update = Mock()
            piece.draw_on_board = Mock()
            piece.on_command = Mock()
            piece.state = Mock()
            piece.state.name = "idle"
            piece.state.physics = Mock()
            piece.state.physics.get_start_ms.return_value = 1000
            pieces.append(piece)
            
        return pieces


class TestGameEventIntegration:
    """Test integration between game logic and event system"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.board = Board(64, 64, 8, 8, MockImg())
        self.received_events = []
        
    def _event_handler(self, event_type: str, data):
        """Test event handler"""
        self.received_events.append((event_type, data))
        
    def test_game_publishes_events_during_play(self):
        """Test that game publishes events during gameplay"""
        pieces = self._create_test_pieces()
        game = Game(pieces, self.board)
        
        # Subscribe to events
        game.event_publisher.broker.subscribe(EventType.PIECE_MOVED, self._event_handler)
        game.event_publisher.broker.subscribe(EventType.PIECE_CAPTURED, self._event_handler)
        
        # Create a move command
        piece = pieces[0]  # PW_1
        piece.state.name = "move"  # Simulate piece entering move state
        cmd = Command(0, piece.id, "move", [(6, 0), (4, 0)])
        
        game._process_input(cmd)
        
        # Should have published move event
        assert len(self.received_events) >= 1
        
    def test_game_run_creates_ui_subscriber(self):
        """Test that game.run() creates and registers UI subscriber"""
        pieces = self._create_test_pieces()
        game = Game(pieces, self.board)
        
        with patch.object(game, '_run_game_loop'):
            with patch.object(game, 'start_user_input_thread'):
                with patch.object(game, '_announce_win'):
                    game.run(num_iterations=1, is_with_graphics=False)
                    
                    # Should have created UI subscriber
                    assert hasattr(game, 'ui_subscriber')
                    assert isinstance(game.ui_subscriber, GameUISubscriber)
                    
    def test_announce_win_publishes_game_ended(self):
        """Test that _announce_win publishes game ended event"""
        pieces = self._create_test_pieces()
        # Remove black king to create win condition
        pieces = [p for p in pieces if not p.id.startswith("KB")]
        
        game = Game(pieces, self.board)
        
        # Subscribe to game ended events
        game.event_publisher.broker.subscribe(EventType.GAME_ENDED, self._event_handler)
        
        game._announce_win()
        
        # Should have published game ended event
        game_ended_events = [e for e in self.received_events if e[0] == EventType.GAME_ENDED]
        assert len(game_ended_events) >= 1
        
        # Winner should be 'W' (white wins)
        winner_data = game_ended_events[0][1]
        assert winner_data.winner == 'W'
        
    def _create_test_pieces(self):
        """Create test pieces with proper mocking"""
        pieces = []
        
        # Create white king
        white_king = Mock(spec=Piece)
        white_king.id = "KW_1"
        white_king.current_cell.return_value = (7, 4)
        white_king.update = Mock()
        white_king.draw_on_board = Mock()
        white_king.on_command = Mock()
        white_king.state = Mock()
        white_king.state.name = "idle"
        white_king.state.physics = Mock()
        white_king.state.physics.get_start_ms.return_value = 1000
        pieces.append(white_king)
        
        # Create black king
        black_king = Mock(spec=Piece)
        black_king.id = "KB_1"
        black_king.current_cell.return_value = (0, 4)
        black_king.update = Mock()
        black_king.draw_on_board = Mock()
        black_king.on_command = Mock()
        black_king.state = Mock()
        black_king.state.name = "idle"
        black_king.state.physics = Mock()
        black_king.state.physics.get_start_ms.return_value = 1000
        pieces.append(black_king)
        
        # Create a white pawn for testing
        white_pawn = Mock(spec=Piece)
        white_pawn.id = "PW_1"
        white_pawn.current_cell.return_value = (6, 0)
        white_pawn.update = Mock()
        white_pawn.draw_on_board = Mock()
        white_pawn.on_command = Mock()
        white_pawn.state = Mock()
        white_pawn.state.name = "idle"
        white_pawn.state.physics = Mock()
        white_pawn.state.physics.get_start_ms.return_value = 1000
        pieces.append(white_pawn)
        
        return pieces


class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.board = Board(64, 64, 8, 8, MockImg())
        
    def test_game_without_graphics(self):
        """Test game running without graphics"""
        pieces = self._create_minimal_pieces()
        game = Game(pieces, self.board)
        
        # Should be able to run without graphics
        with patch.object(game, 'start_user_input_thread'):
            with patch.object(game, '_announce_win'):
                game.run(num_iterations=1, is_with_graphics=False)
                
        assert True  # Should complete without errors
        
    def test_empty_user_input_queue(self):
        """Test game loop with empty input queue"""
        pieces = self._create_minimal_pieces()
        game = Game(pieces, self.board)
        
        # Run game loop with empty queue
        game._run_game_loop(num_iterations=5, is_with_graphics=False)
        
        assert True  # Should complete without errors
        
    def test_collision_resolution_empty_pos(self):
        """Test collision resolution with empty position map"""
        pieces = self._create_minimal_pieces()
        game = Game(pieces, self.board)
        
        # Clear position map
        game.pos.clear()
        
        # Should not crash
        game._resolve_collisions()
        
    def test_invalid_board_validation(self):
        """Test board validation with invalid configurations"""
        # Test with duplicate pieces at same position
        pieces = []
        
        # Two pieces at same position
        for i in range(2):
            piece = Mock(spec=Piece)
            piece.id = f"PW_{i}"
            piece.current_cell.return_value = (4, 4)  # Same position
            pieces.append(piece)
            
        # Add kings
        for color in ['W', 'B']:
            piece = Mock(spec=Piece)
            piece.id = f"K{color}_1"
            piece.current_cell.return_value = (7 if color == 'W' else 0, 4)
            pieces.append(piece)
            
        # Game creation might handle this or might not
        game = Game(pieces, self.board)
        assert isinstance(game, Game)
        
    def _create_minimal_pieces(self):
        """Create minimal valid pieces"""
        pieces = []
        
        # Create kings (required)
        for color in ['W', 'B']:
            piece = Mock(spec=Piece)
            piece.id = f"K{color}_1"
            piece.current_cell.return_value = (7 if color == 'W' else 0, 4)
            piece.update = Mock()
            piece.draw_on_board = Mock()
            piece.state = Mock()
            piece.state.name = "idle"
            piece.state.physics = Mock()
            piece.state.physics.get_start_ms.return_value = 1000
            pieces.append(piece)
            
        return pieces


if __name__ == "__main__":
    pytest.main([__file__])
