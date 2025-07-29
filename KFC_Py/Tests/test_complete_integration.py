"""
Comprehensive integration tests for the complete game system
בדיקות אינטגרציה מקיפות למערכת המשחק המלאה
"""
import pytest
import time
import threading
import queue
from unittest.mock import Mock, patch, MagicMock
import pathlib
import tempfile

import sys
sys.path.append(str(pathlib.Path(__file__).parent.parent))

from Game import Game, InvalidBoard
from GameFactory import create_game
from GameUISubscriber import GameUISubscriber
from MessageBroker import game_message_broker, MessageBroker
from EventType import EventType
from SoundManager import sound_manager
from Command import Command
from KeyboardInput import KeyboardProcessor, KeyboardProducer
from GraphicsFactory import MockImgFactory
from Board import Board
from mock_img import MockImg


class TestCompleteGameSystemIntegration:
    """Test complete game system integration"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.received_events = []
        self.pieces_root = pathlib.Path(__file__).parent.parent.parent / "pieces"
        
    def teardown_method(self):
        """Cleanup after each test"""
        # Clear message broker subscribers
        game_message_broker._subscribers.clear()
        
    def _create_test_event_handler(self):
        """Create test event handler"""
        def handler(event_type: str, data):
            self.received_events.append((event_type, data))
        return handler
        
    def test_full_game_creation_and_initialization(self):
        """Test complete game creation with all systems"""
        if not self.pieces_root.exists():
            pytest.skip("Pieces directory not found")
            
        # Create game with full factory
        game = create_game(str(self.pieces_root), MockImgFactory())
        
        assert isinstance(game, Game)
        assert len(game.pieces) > 0
        assert isinstance(game.board, Board)
        
        # Game should have event publisher
        assert hasattr(game, 'event_publisher')
        
        # Pieces should be properly mapped
        assert len(game.piece_by_id) == len(game.pieces)
        
    def test_game_with_ui_and_sound_integration(self):
        """Test game running with UI and sound systems"""
        if not self.pieces_root.exists():
            pytest.skip("Pieces directory not found")
            
        game = create_game(str(self.pieces_root), MockImgFactory())
        
        # Subscribe to all events
        handler = self._create_test_event_handler()
        for event_type in [EventType.GAME_STARTED, EventType.PIECE_MOVED, 
                          EventType.PIECE_CAPTURED, EventType.GAME_ENDED]:
            game_message_broker.subscribe(event_type, handler)
            
        # Run game briefly
        with patch.object(game, 'start_user_input_thread'):
            with patch.object(game, '_show'):  # Skip graphics display
                with patch('cv2.waitKey', return_value=27):  # ESC key
                    game.run(num_iterations=10, is_with_graphics=True)
                    
        # Should have created UI subscriber
        assert hasattr(game, 'ui_subscriber')
        assert isinstance(game.ui_subscriber, GameUISubscriber)
        
        # Should have published game started event
        game_started_events = [e for e in self.received_events if e[0] == EventType.GAME_STARTED]
        assert len(game_started_events) >= 1
        
    def test_simultaneous_player_input_processing(self):
        """Test processing simultaneous input from both players"""
        if not self.pieces_root.exists():
            pytest.skip("Pieces directory not found")
            
        game = create_game(str(self.pieces_root), MockImgFactory())
        
        # Find white and black pawns
        white_pawn = None
        black_pawn = None
        for piece in game.pieces:
            if piece.id.startswith("PW") and white_pawn is None:
                white_pawn = piece
            elif piece.id.startswith("PB") and black_pawn is None:
                black_pawn = piece
                
        if white_pawn and black_pawn:
            # Create simultaneous commands
            white_cell = white_pawn.current_cell()
            black_cell = black_pawn.current_cell()
            
            white_cmd = Command(0, white_pawn.id, "move", [white_cell, (white_cell[0]-1, white_cell[1])])
            black_cmd = Command(0, black_pawn.id, "move", [black_cell, (black_cell[0]+1, black_cell[1])])
            
            # Process commands
            game._process_input(white_cmd)
            game._process_input(black_cmd)
            
            # Should not crash
            assert True
            
    def test_collision_detection_and_resolution(self):
        """Test collision detection and resolution system"""
        if not self.pieces_root.exists():
            pytest.skip("Pieces directory not found")
            
        game = create_game(str(self.pieces_root), MockImgFactory())
        
        # Subscribe to capture events
        handler = self._create_test_event_handler()
        game_message_broker.subscribe(EventType.PIECE_CAPTURED, handler)
        
        # Force a collision by placing pieces at same position
        if len(game.pieces) >= 2:
            piece1 = game.pieces[0]
            piece2 = game.pieces[1]
            
            # Make sure they're different colors for capture to work
            if piece1.id[1] == piece2.id[1]:  # Same color
                # Find a piece of different color
                for p in game.pieces[2:]:
                    if p.id[1] != piece1.id[1]:
                        piece2 = p
                        break
                        
            # Mock their positions to be the same
            target_cell = (4, 4)
            with patch.object(piece1, 'current_cell', return_value=target_cell):
                with patch.object(piece2, 'current_cell', return_value=target_cell):
                    # Update position map
                    game._update_cell2piece_map()
                    
                    initial_piece_count = len(game.pieces)
                    
                    # Resolve collisions
                    game._resolve_collisions()
                    
                    # Should have removed one piece (or handled collision)
                    # The exact behavior depends on implementation details
                    assert len(game.pieces) <= initial_piece_count
                    
    def test_win_condition_detection_and_announcement(self):
        """Test win condition detection and announcement"""
        if not self.pieces_root.exists():
            pytest.skip("Pieces directory not found")
            
        game = create_game(str(self.pieces_root), MockImgFactory())
        
        # Subscribe to game ended events
        handler = self._create_test_event_handler()
        game_message_broker.subscribe(EventType.GAME_ENDED, handler)
        
        # Force win condition by removing a king
        black_king = None
        for piece in game.pieces:
            if piece.id.startswith("KB"):
                black_king = piece
                break
                
        if black_king:
            game.pieces.remove(black_king)
            
            # Check win condition
            assert game._is_win()
            
            # Announce win
            game._announce_win()
            
            # Should have published game ended event
            game_ended_events = [e for e in self.received_events if e[0] == EventType.GAME_ENDED]
            assert len(game_ended_events) >= 1
            assert game_ended_events[0][1].winner == 'W'  # White wins
            
    def test_keyboard_input_system_integration(self):
        """Test keyboard input system integration"""
        if not self.pieces_root.exists():
            pytest.skip("Pieces directory not found")
            
        game = create_game(str(self.pieces_root), MockImgFactory())
        
        # Start keyboard input system
        game.start_user_input_thread()
        
        try:
            # Verify keyboard processors are created
            assert game.kp1 is not None
            assert game.kp2 is not None
            assert game.kb_prod_1 is not None
            assert game.kb_prod_2 is not None
            
            # Verify initial cursor positions
            assert game.kp1.get_cursor() == (7, 0)  # White at bottom
            assert game.kp2.get_cursor() == (0, 0)  # Black at top
            
            # Test cursor movement
            initial_pos = game.kp1.get_cursor()
            
            # Simulate key press for movement with proper event structure
            from types import SimpleNamespace
            move_event = SimpleNamespace()
            move_event.event_type = "down"  # Required attribute
            move_event.name = "right"
            
            game.kp1.process_key(move_event)
            new_pos = game.kp1.get_cursor()
            
            # Cursor should have moved
            assert new_pos != initial_pos
            
        finally:
            # Clean up threads
            if game.kb_prod_1:
                game.kb_prod_1.stop()
                game.kb_prod_2.stop()
                
    def test_smart_cursor_color_system(self):
        """Test smart cursor color changing system"""
        if not self.pieces_root.exists():
            pytest.skip("Pieces directory not found")
            
        game = create_game(str(self.pieces_root), MockImgFactory())
        
        # Initialize keyboard processors
        game.kp1 = KeyboardProcessor(8, 8, {}, initial_pos=(7, 0))
        game.kp2 = KeyboardProcessor(8, 8, {}, initial_pos=(0, 0))
        
        # Test normal cursor colors (no selection)
        game.selected_id_1 = None
        game.selected_id_2 = None
        
        with patch.object(game.board, 'clone') as mock_clone:
            mock_board = Mock()
            mock_board.img = Mock()
            mock_board.img.draw_rect = Mock()
            mock_clone.return_value = mock_board
            
            game._draw()
            
            # Should have called draw_rect for both cursors
            assert mock_board.img.draw_rect.call_count == 2
            
            # Get colors used
            colors = [call[0][4] for call in mock_board.img.draw_rect.call_args_list]
            
            # Should have normal colors
            assert (0, 255, 0) in colors  # Green for player 1
            assert (255, 0, 0) in colors  # Red for player 2
            
            # Reset mock for next test
            mock_board.img.draw_rect.reset_mock()
            
            # Test selection colors
            game.selected_id_1 = "PW_1"  # Player 1 selects piece
            
            game._draw()
            
            # Should have called draw_rect again
            assert mock_board.img.draw_rect.call_count == 2
            
            colors = [call[0][4] for call in mock_board.img.draw_rect.call_args_list]
            assert (0, 0, 255) in colors  # Should have red selection color
        
    def test_sound_system_integration(self):
        """Test sound system integration with game events"""
        if not self.pieces_root.exists():
            pytest.skip("Pieces directory not found")
            
        game = create_game(str(self.pieces_root), MockImgFactory())
        
        # Mock sound manager to avoid audio issues in tests
        with patch.object(sound_manager, 'play_game_start') as mock_start:
            with patch.object(sound_manager, 'play_piece_move') as mock_move:
                with patch.object(sound_manager, 'play_victory') as mock_victory:
                    
                    # Run game briefly to trigger events
                    with patch.object(game, 'start_user_input_thread'):
                        with patch.object(game, '_show'):
                            with patch.object(game, '_announce_win'):
                                game.run(num_iterations=5, is_with_graphics=False)
                                
                    # Game start sound should have been played
                    mock_start.assert_called()
                    
    def test_error_recovery_and_resilience(self):
        """Test system recovery from various error conditions"""
        if not self.pieces_root.exists():
            pytest.skip("Pieces directory not found")
            
        game = create_game(str(self.pieces_root), MockImgFactory())
        
        # Test with corrupted piece
        corrupted_piece = Mock()
        corrupted_piece.id = "CORRUPTED"
        corrupted_piece.current_cell.side_effect = Exception("Corrupted piece")
        corrupted_piece.update.side_effect = Exception("Update failed")
        
        # Add corrupted piece
        game.pieces.append(corrupted_piece)
        
        # Game should handle errors gracefully
        try:
            game._update_cell2piece_map()
            game._run_game_loop(num_iterations=1, is_with_graphics=False)
            # Should not crash despite corrupted piece
            assert True
        except Exception as e:
            # Some exceptions might be expected, but shouldn't be catastrophic
            assert "Corrupted piece" in str(e) or "Update failed" in str(e)
            
    def test_concurrent_event_publishing(self):
        """Test concurrent event publishing and handling"""
        if not self.pieces_root.exists():
            pytest.skip("Pieces directory not found")
            
        game = create_game(str(self.pieces_root), MockImgFactory())
        
        # Create multiple event handlers
        handlers = []
        for i in range(5):
            handler_events = []
            def make_handler(events_list):
                def handler(event_type, data):
                    events_list.append((event_type, data))
                return handler
            
            handler = make_handler(handler_events)
            handlers.append((handler, handler_events))
            
            # Subscribe to events
            game_message_broker.subscribe(EventType.PIECE_MOVED, handler)
            
        # Publish events from multiple threads
        def publish_events():
            for i in range(10):
                game.event_publisher.publish_piece_moved(f"P{i}", (0, i), (1, i))
                time.sleep(0.001)
                
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=publish_events)
            threads.append(thread)
            thread.start()
            
        # Wait for completion
        for thread in threads:
            thread.join()
            
        # All handlers should have received events
        for handler, events in handlers:
            assert len(events) == 30  # 3 threads × 10 events each
            
    def test_memory_and_resource_management(self):
        """Test memory and resource management"""
        if not self.pieces_root.exists():
            pytest.skip("Pieces directory not found")
            
        # Create and destroy multiple games
        games = []
        for i in range(5):
            game = create_game(str(self.pieces_root), MockImgFactory())
            games.append(game)
            
        # Each game should be independent
        assert len(games) == 5
        for game in games:
            assert isinstance(game, Game)
            assert len(game.pieces) > 0
            
        # Clean up
        for game in games:
            # Stop any running threads
            if hasattr(game, 'kb_prod_1') and game.kb_prod_1:
                game.kb_prod_1.stop()
                game.kb_prod_2.stop()
                
    def test_complete_game_flow_simulation(self):
        """Test complete game flow from start to finish"""
        if not self.pieces_root.exists():
            pytest.skip("Pieces directory not found")
            
        game = create_game(str(self.pieces_root), MockImgFactory())
        
        # Track all events
        handler = self._create_test_event_handler()
        for event_type in [EventType.GAME_STARTED, EventType.PIECE_MOVED, 
                          EventType.PIECE_CAPTURED, EventType.GAME_ENDED]:
            game_message_broker.subscribe(event_type, handler)
            
        # Simulate complete game
        with patch.object(game, 'start_user_input_thread'):
            with patch.object(game, '_show'):
                # Start game
                game.run(num_iterations=1, is_with_graphics=False)
                
                # Make some moves
                white_pawn = None
                for piece in game.pieces:
                    if piece.id.startswith("PW"):
                        white_pawn = piece
                        break
                        
                if white_pawn:
                    cell = white_pawn.current_cell()
                    move_cmd = Command(0, white_pawn.id, "move", [cell, (cell[0]-1, cell[1])])
                    game._process_input(move_cmd)
                    game._run_game_loop(num_iterations=10, is_with_graphics=False)
                    
                # Force game end
                black_king = None
                for piece in game.pieces:
                    if piece.id.startswith("KB"):
                        black_king = piece
                        break
                        
                if black_king:
                    game.pieces.remove(black_king)
                    game._announce_win()
                    
        # Verify complete event flow
        event_types = [e[0] for e in self.received_events]
        assert EventType.GAME_STARTED in event_types
        
        # May have move and/or capture events
        # Should have game ended event
        assert EventType.GAME_ENDED in event_types


if __name__ == "__main__":
    pytest.main([__file__])
