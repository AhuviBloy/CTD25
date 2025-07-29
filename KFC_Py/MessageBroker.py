"""
Message Broker for Pub/Sub Pattern
מתווך הודעות למשחק Kung Fu Chess
"""
from typing import Dict, List, Callable, Any
import logging

logger = logging.getLogger(__name__)


class MessageBroker:
    """
    Message Broker that implements Pub/Sub pattern.
    Publishers don't know about subscribers - complete decoupling.
    """
    
    def __init__(self):
        # {event_type: [subscriber_function1, subscriber_function2, ...]}
        self._subscribers: Dict[str, List[Callable]] = {}
        
    def subscribe(self, event_type: str, handler: Callable[[str, Any], None]):
        """
        Subscribe to specific event type.
        
        Args:
            event_type: Type of event to listen for (e.g., "PIECE_MOVED")
            handler: Function that will handle the event - handler(event_type, data)
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
            
        self._subscribers[event_type].append(handler)
        logger.debug(f"Subscribed to {event_type}. Total subscribers: {len(self._subscribers[event_type])}")
    
    def unsubscribe(self, event_type: str, handler: Callable):
        """Remove a subscriber from an event type"""
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(handler)
                logger.debug(f"Unsubscribed from {event_type}")
            except ValueError:
                logger.warning(f"Handler not found for {event_type}")
    
    def publish(self, event_type: str, data: Any = None):
        """
        Publish an event to all subscribers.
        Publishers don't know who's listening - true Pub/Sub!
        
        Args:
            event_type: Type of event (e.g., "PIECE_MOVED", "PIECE_CAPTURED")
            data: Event data (can be dict, object, etc.)
        """
        if event_type not in self._subscribers:
            logger.debug(f"No subscribers for event: {event_type}")
            return
            
        subscribers = self._subscribers[event_type]
        logger.debug(f"Publishing {event_type} to {len(subscribers)} subscribers")
        
        for handler in subscribers:
            try:
                handler(event_type, data)
            except Exception as e:
                logger.error(f"Error in subscriber for {event_type}: {e}")
    
    def get_subscriber_count(self, event_type: str) -> int:
        """Get number of subscribers for an event type"""
        return len(self._subscribers.get(event_type, []))
    
    def get_all_event_types(self) -> List[str]:
        """Get all event types that have subscribers"""
        return list(self._subscribers.keys())
    
    def clear_all_subscribers(self):
        """Clear all subscribers (useful for testing)"""
        self._subscribers.clear()
        logger.debug("All subscribers cleared")


# Global message broker instance for the game
game_message_broker = MessageBroker()
