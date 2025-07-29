"""
Subscriber Interface for Pub/Sub Pattern
ממשק למנויים במערכת הודעות
"""
from abc import ABC, abstractmethod
from typing import Any


class Subscriber(ABC):
    """
    Abstract base class for all subscribers in the Pub/Sub system.
    Each subscriber must implement handle_event method.
    """
    
    @abstractmethod
    def handle_event(self, event_type: str, data: Any):
        """
        Handle an event that was published.
        
        Args:
            event_type: The type of event (e.g., "PIECE_MOVED")
            data: The event data (can be dict, object, etc.)
        """
        pass
    
    def get_subscribed_events(self):
        """
        Optional: Return list of event types this subscriber is interested in.
        Subclasses can override this for documentation/introspection.
        """
        return []


class FunctionSubscriber:
    """
    Wrapper to make regular functions work as subscribers.
    This allows using simple functions as event handlers.
    """
    
    def __init__(self, handler_function):
        self.handler_function = handler_function
    
    def handle_event(self, event_type: str, data: Any):
        """Delegate to the wrapped function"""
        self.handler_function(event_type, data)
