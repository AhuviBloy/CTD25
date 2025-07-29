"""
Comprehensive tests for the Event System (Pub/Sub Architecture)
בדיקות מקיפות למערכת האירועים (ארכיטקטורת Pub/Sub)
"""
import pytest
import time
from unittest.mock import Mock, patch, MagicMock
import threading
from typing import List, Any

import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent))

from MessageBroker import MessageBroker, game_message_broker
from EventType import EventType, GameStartedData, GameEndedData, PieceMovedData, PieceCapturedData
from GameEventPublisher import GameEventPublisher, game_event_publisher
from Subscriber import Subscriber


class TestMessageBroker:
    """Test the core message broker functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.broker = MessageBroker()
        self.received_events = []
        
    def test_message_broker_initialization(self):
        """Test broker initializes correctly"""
        assert isinstance(self.broker, MessageBroker)
        assert len(self.broker._subscribers) == 0
        
    def test_subscribe_single_handler(self):
        """Test subscribing a single event handler"""
        def handler(event_type: str, data: Any):
            self.received_events.append((event_type, data))
            
        self.broker.subscribe(EventType.GAME_STARTED, handler)
        assert len(self.broker._subscribers[EventType.GAME_STARTED]) == 1
        
    def test_subscribe_multiple_handlers(self):
        """Test subscribing multiple handlers to same event"""
        def handler1(event_type: str, data: Any):
            self.received_events.append(("handler1", event_type, data))
            
        def handler2(event_type: str, data: Any):
            self.received_events.append(("handler2", event_type, data))
            
        self.broker.subscribe(EventType.GAME_STARTED, handler1)
        self.broker.subscribe(EventType.GAME_STARTED, handler2)
        
        assert len(self.broker._subscribers[EventType.GAME_STARTED]) == 2
        
    def test_publish_single_event(self):
        """Test publishing event to single subscriber"""
        def handler(event_type: str, data: Any):
            self.received_events.append((event_type, data))
            
        self.broker.subscribe(EventType.PIECE_MOVED, handler)
        
        test_data = PieceMovedData("PW_1", (0, 0), (1, 1), "W")
        self.broker.publish(EventType.PIECE_MOVED, test_data)
        
        assert len(self.received_events) == 1
        assert self.received_events[0][0] == EventType.PIECE_MOVED
        assert self.received_events[0][1] == test_data
        
    def test_publish_multiple_subscribers(self):
        """Test publishing event to multiple subscribers"""
        def handler1(event_type: str, data: Any):
            self.received_events.append(("handler1", event_type))
            
        def handler2(event_type: str, data: Any):
            self.received_events.append(("handler2", event_type))
            
        self.broker.subscribe(EventType.PIECE_CAPTURED, handler1)
        self.broker.subscribe(EventType.PIECE_CAPTURED, handler2)
        
        test_data = PieceCapturedData("PB_1", "PW_1", (2, 2))
        self.broker.publish(EventType.PIECE_CAPTURED, test_data)
        
        assert len(self.received_events) == 2
        event_types = [event[1] for event in self.received_events]
        assert all(et == EventType.PIECE_CAPTURED for et in event_types)
        
    def test_publish_no_subscribers(self):
        """Test publishing event with no subscribers doesn't crash"""
        test_data = GameEndedData("W", "checkmate")
        # Should not raise exception
        self.broker.publish(EventType.GAME_ENDED, test_data)
        assert len(self.received_events) == 0
        
    def test_unsubscribe_handler(self):
        """Test unsubscribing event handlers"""
        def handler(event_type: str, data: Any):
            self.received_events.append((event_type, data))
            
        self.broker.subscribe(EventType.GAME_STARTED, handler)
        assert len(self.broker._subscribers[EventType.GAME_STARTED]) == 1
        
        self.broker.unsubscribe(EventType.GAME_STARTED, handler)
        assert len(self.broker._subscribers[EventType.GAME_STARTED]) == 0
        
    def test_error_handling_in_subscriber(self):
        """Test broker handles subscriber errors gracefully"""
        def good_handler(event_type: str, data: Any):
            self.received_events.append(("good", event_type))
            
        def bad_handler(event_type: str, data: Any):
            raise Exception("Test error")
            
        self.broker.subscribe(EventType.GAME_STARTED, good_handler)
        self.broker.subscribe(EventType.GAME_STARTED, bad_handler)
        
        test_data = GameStartedData("Player1", "Player2")
        # Should not crash despite bad handler
        self.broker.publish(EventType.GAME_STARTED, test_data)
        
        # Good handler should still receive event
        assert len(self.received_events) == 1
        assert self.received_events[0][0] == "good"


class TestEventTypes:
    """Test event data classes"""
    
    def test_game_started_data(self):
        """Test GameStartedData creation and attributes"""
        data = GameStartedData("White Player", "Black Player")
        assert data.player1_name == "White Player"
        assert data.player2_name == "Black Player"
        
    def test_piece_moved_data(self):
        """Test PieceMovedData creation and attributes"""
        data = PieceMovedData("QW_1", (0, 3), (4, 7), "W")
        assert data.piece_id == "QW_1"
        assert data.from_cell == (0, 3)
        assert data.to_cell == (4, 7)
        assert data.player_color == "W"
        
    def test_piece_captured_data(self):
        """Test PieceCapturedData creation and attributes"""
        data = PieceCapturedData("PB_1", "RW_1", (3, 4))
        assert data.captured_piece_id == "PB_1"
        assert data.capturing_piece_id == "RW_1"
        assert data.cell == (3, 4)
        
    def test_game_ended_data(self):
        """Test GameEndedData creation and attributes"""
        data = GameEndedData("B", "checkmate")
        assert data.winner == "B"
        assert data.reason == "checkmate"


class TestGameEventPublisher:
    """Test the game event publisher"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.received_events = []
        self.publisher = GameEventPublisher()
        
        # Subscribe to all events for testing
        game_message_broker.subscribe(EventType.GAME_STARTED, self._event_handler)
        game_message_broker.subscribe(EventType.PIECE_MOVED, self._event_handler)
        game_message_broker.subscribe(EventType.PIECE_CAPTURED, self._event_handler)
        game_message_broker.subscribe(EventType.GAME_ENDED, self._event_handler)
        
    def teardown_method(self):
        """Cleanup after each test"""
        # Clear subscribers to avoid interference between tests
        game_message_broker._subscribers.clear()
        
    def _event_handler(self, event_type: str, data: Any):
        """Test event handler"""
        self.received_events.append((event_type, data))
        
    def test_publish_game_started(self):
        """Test publishing game started event"""
        self.publisher.publish_game_started("Alice", "Bob")
        
        assert len(self.received_events) == 1
        event_type, data = self.received_events[0]
        assert event_type == EventType.GAME_STARTED
        assert data.player1_name == "Alice"
        assert data.player2_name == "Bob"
        
    def test_publish_piece_moved(self):
        """Test publishing piece moved event"""
        self.publisher.publish_piece_moved("NB_1", (0, 1), (2, 0))
        
        assert len(self.received_events) == 1
        event_type, data = self.received_events[0]
        assert event_type == EventType.PIECE_MOVED
        assert data.piece_id == "NB_1"
        assert data.from_cell == (0, 1)
        assert data.to_cell == (2, 0)
        assert data.player_color == "B"
        
    def test_publish_piece_captured(self):
        """Test publishing piece captured event"""
        self.publisher.publish_piece_captured("PW_1", "QB_1", (4, 4))
        
        assert len(self.received_events) == 1
        event_type, data = self.received_events[0]
        assert event_type == EventType.PIECE_CAPTURED
        assert data.captured_piece_id == "PW_1"
        assert data.capturing_piece_id == "QB_1"
        assert data.cell == (4, 4)
        
    def test_publish_game_ended(self):
        """Test publishing game ended event"""
        self.publisher.publish_game_ended("W", "checkmate")
        
        assert len(self.received_events) == 1
        event_type, data = self.received_events[0]
        assert event_type == EventType.GAME_ENDED
        assert data.winner == "W"
        assert data.reason == "checkmate"
        
    def test_multiple_events_sequence(self):
        """Test publishing sequence of events"""
        self.publisher.publish_game_started("Player1", "Player2")
        self.publisher.publish_piece_moved("PW_1", (6, 0), (4, 0))
        self.publisher.publish_piece_captured("PB_1", "PW_1", (4, 1))
        self.publisher.publish_game_ended("W", "checkmate")
        
        assert len(self.received_events) == 4
        
        # Check event sequence
        event_types = [event[0] for event in self.received_events]
        expected_types = [
            EventType.GAME_STARTED,
            EventType.PIECE_MOVED,
            EventType.PIECE_CAPTURED,
            EventType.GAME_ENDED
        ]
        assert event_types == expected_types


class TestSubscriberBase:
    """Test the base Subscriber class"""
    
    def test_subscriber_abstract_methods(self):
        """Test that Subscriber defines required abstract methods"""
        # Should be able to create subscriber instances for testing
        class TestSubscriber(Subscriber):
            def handle_event(self, event_type: str, data: Any):
                pass
                
            def get_subscribed_events(self) -> List[str]:
                return [EventType.GAME_STARTED]
                
        subscriber = TestSubscriber()
        assert hasattr(subscriber, 'handle_event')
        assert hasattr(subscriber, 'get_subscribed_events')
        assert subscriber.get_subscribed_events() == [EventType.GAME_STARTED]


class TestEventSystemIntegration:
    """Integration tests for the complete event system"""
    
    def setup_method(self):
        """Setup for integration tests"""
        self.received_events = []
        self.broker = MessageBroker()
        self.publisher = GameEventPublisher()
        
    def test_full_game_event_flow(self):
        """Test complete game event flow from start to end"""
        # Create a test subscriber
        class GameFlowSubscriber(Subscriber):
            def __init__(self, test_instance):
                self.test = test_instance
                
            def handle_event(self, event_type: str, data: Any):
                self.test.received_events.append((event_type, data))
                
            def get_subscribed_events(self):
                return [EventType.GAME_STARTED, EventType.PIECE_MOVED, 
                       EventType.PIECE_CAPTURED, EventType.GAME_ENDED]
        
        subscriber = GameFlowSubscriber(self)
        
        # Subscribe to all events
        for event_type in subscriber.get_subscribed_events():
            game_message_broker.subscribe(event_type, subscriber.handle_event)
        
        # Simulate a complete game flow
        self.publisher.publish_game_started("White", "Black")
        self.publisher.publish_piece_moved("PW_1", (6, 4), (4, 4))
        self.publisher.publish_piece_moved("PB_1", (1, 4), (3, 4))
        self.publisher.publish_piece_captured("PB_1", "PW_1", (3, 4))
        self.publisher.publish_game_ended("W", "checkmate")
        
        # Verify all events were received
        assert len(self.received_events) == 5
        
        # Verify event data
        game_start = self.received_events[0][1]
        assert game_start.player1_name == "White"
        assert game_start.player2_name == "Black"
        
        first_move = self.received_events[1][1]
        assert first_move.piece_id == "PW_1"
        assert first_move.from_cell == (6, 4)
        assert first_move.to_cell == (4, 4)
        assert first_move.player_color == "W"
        
        capture = self.received_events[3][1]
        assert capture.captured_piece_id == "PB_1"
        assert capture.capturing_piece_id == "PW_1"
        
        game_end = self.received_events[4][1]
        assert game_end.winner == "W"
        assert game_end.reason == "checkmate"
        
        # Cleanup
        game_message_broker._subscribers.clear()
        
    def test_concurrent_event_publishing(self):
        """Test thread safety of event system"""
        import threading
        import time
        
        def event_handler(event_type: str, data: Any):
            self.received_events.append((event_type, data))
            
        game_message_broker.subscribe(EventType.PIECE_MOVED, event_handler)
        
        def publish_events():
            for i in range(10):
                self.publisher.publish_piece_moved(f"P{i}", (0, i), (1, i))
                time.sleep(0.01)  # Small delay to simulate real timing
        
        # Start multiple threads publishing events
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=publish_events)
            threads.append(thread)
            thread.start()
            
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
            
        # Should have received 30 events (3 threads × 10 events each)
        assert len(self.received_events) == 30
        
        # Cleanup
        game_message_broker._subscribers.clear()


if __name__ == "__main__":
    pytest.main([__file__])
