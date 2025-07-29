"""
Simple test for Pub/Sub integration with Game
בדיקה פשוטה לחיבור Pub/Sub למשחק
"""
from MessageBroker import game_message_broker
from EventType import EventType

def test_event_handler(event_type: str, data):
    """Simple event handler for testing"""
    print(f"🎯 Received event: {event_type}")
    if hasattr(data, 'piece_id'):
        print(f"   Piece: {data.piece_id}")
    if hasattr(data, 'from_cell') and hasattr(data, 'to_cell'):
        print(f"   Move: {data.from_cell} → {data.to_cell}")
    if hasattr(data, 'winner'):
        print(f"   Winner: {data.winner}")
    print()

# Subscribe to all events
game_message_broker.subscribe(EventType.GAME_STARTED, test_event_handler)
game_message_broker.subscribe(EventType.PIECE_MOVED, test_event_handler)
game_message_broker.subscribe(EventType.PIECE_CAPTURED, test_event_handler)
game_message_broker.subscribe(EventType.GAME_ENDED, test_event_handler)

print("Event handlers registered! Run the game to see events:")
print("python main.py")
