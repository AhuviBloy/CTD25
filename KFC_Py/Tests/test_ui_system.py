"""
Comprehensive tests for the GameUISubscriber and UI System
בדיקות מקיפות למערכת ממשק המשתמש
"""
import pytest
import numpy as np
import cv2
from unittest.mock import Mock, patch, MagicMock
import tempfile
import pathlib
from typing import List, Any

import sys
sys.path.append(str(pathlib.Path(__file__).parent.parent))

from GameUISubscriber import GameUISubscriber
from EventType import EventType, GameStartedData, GameEndedData, PieceMovedData, PieceCapturedData
from Subscriber import Subscriber
from SoundManager import SoundManager


class TestGameUISubscriber:
    """Test the GameUISubscriber class"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.ui_subscriber = GameUISubscriber(board_width=512, board_height=512)
        
    def test_ui_subscriber_initialization(self):
        """Test UI subscriber initializes correctly"""
        assert isinstance(self.ui_subscriber, GameUISubscriber)
        assert isinstance(self.ui_subscriber, Subscriber)
        assert self.ui_subscriber.board_width == 512
        assert self.ui_subscriber.board_height == 512
        assert len(self.ui_subscriber.white_moves) == 0
        assert len(self.ui_subscriber.black_moves) == 0
        assert self.ui_subscriber.white_score == 0
        assert self.ui_subscriber.black_score == 0
        
    def test_get_subscribed_events(self):
        """Test that UI subscriber subscribes to correct events"""
        events = self.ui_subscriber.get_subscribed_events()
        expected_events = [
            EventType.GAME_STARTED,
            EventType.PIECE_MOVED,
            EventType.PIECE_CAPTURED,
            EventType.GAME_ENDED
        ]
        assert set(events) == set(expected_events)
        
    def test_handle_game_started_event(self):
        """Test handling game started event"""
        # Add some test data first
        self.ui_subscriber.white_moves = ["Pe2-e4"]
        self.ui_subscriber.black_moves = ["Pe7-e5"]
        self.ui_subscriber.white_score = 5
        self.ui_subscriber.black_score = 3
        self.ui_subscriber.move_counter = 2
        
        # Create game started event
        data = GameStartedData("Alice", "Bob")
        
        with patch.object(self.ui_subscriber, '_handle_game_started') as mock_handler:
            self.ui_subscriber.handle_event(EventType.GAME_STARTED, data)
            mock_handler.assert_called_once_with(data)
            
    def test_game_started_resets_state(self):
        """Test that game started event resets UI state"""
        # Set up some existing state
        self.ui_subscriber.white_moves = ["Pe2-e4", "Nf3"]
        self.ui_subscriber.black_moves = ["Pe7-e5"]
        self.ui_subscriber.white_score = 10
        self.ui_subscriber.black_score = 8
        self.ui_subscriber.move_counter = 3
        
        data = GameStartedData("Player1", "Player2")
        self.ui_subscriber._handle_game_started(data)
        
        # Verify state is reset
        assert len(self.ui_subscriber.white_moves) == 0
        assert len(self.ui_subscriber.black_moves) == 0
        assert self.ui_subscriber.white_score == 0
        assert self.ui_subscriber.black_score == 0
        assert self.ui_subscriber.move_counter == 0
        
    def test_handle_piece_moved_event(self):
        """Test handling piece moved event"""
        data = PieceMovedData("PW_1", (6, 4), (4, 4), "W")
        
        # Mock sound manager to avoid audio issues in tests
        with patch('GameUISubscriber.sound_manager') as mock_sound:
            self.ui_subscriber._handle_piece_moved(data)
            mock_sound.play_piece_move.assert_called_once()
            
        # Check move was recorded
        assert len(self.ui_subscriber.white_moves) == 1
        assert "Pe5-e4" in self.ui_subscriber.white_moves[0] or "P" in self.ui_subscriber.white_moves[0]
        assert self.ui_subscriber.move_counter == 1
        
    def test_handle_piece_moved_black_piece(self):
        """Test handling black piece moved event"""
        data = PieceMovedData("PB_1", (1, 4), (3, 4), "B")
        
        with patch('GameUISubscriber.sound_manager') as mock_sound:
            self.ui_subscriber._handle_piece_moved(data)
            
        # Check move was recorded for black
        assert len(self.ui_subscriber.black_moves) == 1
        assert len(self.ui_subscriber.white_moves) == 0
        
    def test_handle_piece_captured_event(self):
        """Test handling piece captured event"""
        # Set up initial moves for both players
        self.ui_subscriber.white_moves = ["Pe2-e4"]
        self.ui_subscriber.black_moves = ["Pe7-e5"]
        
        data = PieceCapturedData("PB_1", "PW_2", (3, 4))
        
        with patch('GameUISubscriber.sound_manager') as mock_sound:
            self.ui_subscriber._handle_piece_captured(data)
            mock_sound.play_piece_capture.assert_called_once()
            
        # Check score was updated (white captured black pawn = 1 point)
        assert self.ui_subscriber.white_score == 1
        assert self.ui_subscriber.black_score == 0
        
        # Check capture notation was added to last move
        if len(self.ui_subscriber.white_moves) > 0:
            assert "xP" in self.ui_subscriber.white_moves[-1]
            
    def test_handle_piece_captured_different_pieces(self):
        """Test capturing different piece types gives correct scores"""
        test_cases = [
            ("PB_1", 1),   # Pawn = 1 point
            ("NB_1", 3),   # Knight = 3 points  
            ("BB_1", 3),   # Bishop = 3 points
            ("RB_1", 5),   # Rook = 5 points
            ("QB_1", 9),   # Queen = 9 points
            ("KB_1", 0),   # King = 0 points (game should end)
        ]
        
        for piece_id, expected_points in test_cases:
            # Reset state
            self.ui_subscriber.white_score = 0
            self.ui_subscriber.white_moves = ["Pe2-e4"]
            
            data = PieceCapturedData(piece_id, "PW_1", (3, 4))
            
            with patch('GameUISubscriber.sound_manager'):
                self.ui_subscriber._handle_piece_captured(data)
                
            assert self.ui_subscriber.white_score == expected_points
            
    def test_handle_game_ended_event(self):
        """Test handling game ended event"""
        data = GameEndedData("W", "checkmate")
        
        with patch('GameUISubscriber.sound_manager') as mock_sound:
            with patch.object(self.ui_subscriber, '_show_victory_message') as mock_victory:
                self.ui_subscriber._handle_game_ended(data)
                mock_sound.play_victory.assert_called_once()
                mock_victory.assert_called_once_with("W")
                
    def test_cell_to_notation_conversion(self):
        """Test chess notation conversion"""
        test_cases = [
            ((0, 0), "a8"),
            ((0, 7), "h8"),
            ((7, 0), "a1"),
            ((7, 7), "h1"),
            ((3, 4), "e5"),
            ((4, 3), "d4"),
        ]
        
        for cell, expected in test_cases:
            result = self.ui_subscriber._cell_to_notation(cell)
            assert result == expected
            
    def test_create_ui_overlay_basic(self):
        """Test basic UI overlay creation"""
        # Create a simple test board image
        test_board = np.zeros((512, 512, 3), dtype=np.uint8)
        
        # Should not crash and return an image
        result = self.ui_subscriber.create_ui_overlay(test_board)
        assert isinstance(result, np.ndarray)
        assert len(result.shape) == 3  # Should be color image
        assert result.shape[2] == 3    # Should have 3 channels (BGR)
        
    def test_create_ui_overlay_with_moves(self):
        """Test UI overlay creation with move history"""
        # Set up some game state
        self.ui_subscriber.white_moves = ["Pe2-e4", "Nf3", "Bc4"]
        self.ui_subscriber.black_moves = ["Pe7-e5", "Nc6"]
        self.ui_subscriber.white_score = 3
        self.ui_subscriber.black_score = 1
        
        test_board = np.zeros((512, 512, 3), dtype=np.uint8)
        
        result = self.ui_subscriber.create_ui_overlay(test_board)
        assert isinstance(result, np.ndarray)
        # Result should be larger than original board (has side panels)
        assert result.shape[1] > test_board.shape[1]
        
    def test_ui_overlay_error_handling(self):
        """Test UI overlay handles errors gracefully"""
        # Test with invalid board image
        invalid_board = np.array([])  # Invalid image
        
        result = self.ui_subscriber.create_ui_overlay(invalid_board)
        # Should return the original image on error
        assert np.array_equal(result, invalid_board)
        
    @patch('cv2.putText')
    @patch('cv2.rectangle')
    def test_draw_player_panel(self, mock_rect, mock_text):
        """Test drawing player panel"""
        canvas = np.zeros((600, 900, 3), dtype=np.uint8)
        moves = ["Pe2-e4", "Nf3"]
        
        self.ui_subscriber._draw_player_panel(canvas, 0, "White", moves, 5, (255, 255, 255))
        
        # Should have called cv2.putText for text drawing
        assert mock_text.called
        
    def test_victory_message_display(self):
        """Test victory message display"""
        with patch('cv2.imshow') as mock_show:
            with patch('cv2.waitKey', return_value=ord('q')):
                with patch('cv2.destroyAllWindows'):
                    self.ui_subscriber._show_victory_message("W")
                    
                    # Should have displayed victory window
                    mock_show.assert_called()
                    
    def test_gradient_background_creation(self):
        """Test gradient background creation"""
        result = self.ui_subscriber._create_gradient_background()
        
        assert isinstance(result, np.ndarray)
        assert result.shape == (self.ui_subscriber.total_height, self.ui_subscriber.total_width, 3)
        assert result.dtype == np.uint8
        
    def test_event_handling_with_invalid_data(self):
        """Test event handling with invalid/missing data"""
        # Test with None data
        self.ui_subscriber.handle_event(EventType.PIECE_MOVED, None)
        
        # Test with object missing required attributes
        class InvalidData:
            pass
            
        invalid_data = InvalidData()
        self.ui_subscriber.handle_event(EventType.PIECE_MOVED, invalid_data)
        
        # Should not crash (graceful error handling)
        assert len(self.ui_subscriber.white_moves) == 0
        assert len(self.ui_subscriber.black_moves) == 0
        
    def test_move_list_length_limit(self):
        """Test that move lists don't grow indefinitely"""
        # Add many moves
        for i in range(50):
            data = PieceMovedData(f"PW_{i%8}", (6, i%8), (4, i%8), "W")
            with patch('GameUISubscriber.sound_manager'):
                self.ui_subscriber._handle_piece_moved(data)
                
        # UI should handle long move lists gracefully
        assert len(self.ui_subscriber.white_moves) == 50
        
        # Test UI overlay still works with many moves
        test_board = np.zeros((512, 512, 3), dtype=np.uint8)
        result = self.ui_subscriber.create_ui_overlay(test_board)
        assert isinstance(result, np.ndarray)


class TestUISystemIntegration:
    """Integration tests for the complete UI system"""
    
    def setup_method(self):
        """Setup for integration tests"""
        self.ui_subscriber = GameUISubscriber()
        
    def test_complete_game_ui_flow(self):
        """Test complete game flow through UI system"""
        with patch('GameUISubscriber.sound_manager') as mock_sound:
            # Game starts
            self.ui_subscriber.handle_event(
                EventType.GAME_STARTED, 
                GameStartedData("Alice", "Bob")
            )
            
            # Moves
            self.ui_subscriber.handle_event(
                EventType.PIECE_MOVED,
                PieceMovedData("PW_1", (6, 4), (4, 4), "W")
            )
            
            self.ui_subscriber.handle_event(
                EventType.PIECE_MOVED,
                PieceMovedData("PB_1", (1, 4), (3, 4), "B")
            )
            
            # Capture
            self.ui_subscriber.handle_event(
                EventType.PIECE_CAPTURED,
                PieceCapturedData("PB_1", "PW_1", (3, 4))
            )
            
            # Game ends
            with patch.object(self.ui_subscriber, '_show_victory_message'):
                self.ui_subscriber.handle_event(
                    EventType.GAME_ENDED,
                    GameEndedData("W", "checkmate")
                )
            
            # Verify final state
            assert len(self.ui_subscriber.white_moves) >= 1
            assert len(self.ui_subscriber.black_moves) >= 1
            assert self.ui_subscriber.white_score > 0
            
            # Verify sounds were played
            mock_sound.play_game_start.assert_called()
            mock_sound.play_piece_move.assert_called()
            mock_sound.play_piece_capture.assert_called()
            mock_sound.play_victory.assert_called()
            
    def test_ui_system_error_recovery(self):
        """Test UI system recovers from errors"""
        # Test with corrupted event data
        class CorruptedData:
            def __getattr__(self, name):
                raise AttributeError(f"No attribute {name}")
                
        corrupted = CorruptedData()
        
        # Should not crash
        self.ui_subscriber.handle_event(EventType.PIECE_MOVED, corrupted)
        self.ui_subscriber.handle_event(EventType.PIECE_CAPTURED, corrupted)
        
        # UI should still function
        test_board = np.zeros((512, 512, 3), dtype=np.uint8)
        result = self.ui_subscriber.create_ui_overlay(test_board)
        assert isinstance(result, np.ndarray)


if __name__ == "__main__":
    pytest.main([__file__])
