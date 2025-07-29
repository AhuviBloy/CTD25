"""
Game Event Publisher for Kung Fu Chess
מפרסם אירועי משחק - שכבת עזר מעל MessageBroker
"""
from MessageBroker import game_message_broker
from EventType import EventType, GameStartedData, GameEndedData, PieceMovedData, PieceCapturedData
import logging
import time

logger = logging.getLogger(__name__)


class GameEventPublisher:
    """
    Publisher that provides convenient methods to publish game events.
    This is a helper layer over the MessageBroker for game-specific events.
    """
    
    def __init__(self, broker=None):
        self.broker = broker or game_message_broker
    
    def publish_game_started(self, player1_name: str = "Player 1", player2_name: str = "Player 2"):
        """Publish game started event"""
        data = GameStartedData(player1_name, player2_name)
        data.timestamp = time.time()
        
        logger.info(f"Publishing GAME_STARTED: {player1_name} vs {player2_name}")
        self.broker.publish(EventType.GAME_STARTED, data)
    
    def publish_game_ended(self, winner: str = None, reason: str = "checkmate"):
        """Publish game ended event"""
        data = GameEndedData(winner, reason)
        data.timestamp = time.time()
        
        logger.info(f"Publishing GAME_ENDED: winner={winner}, reason={reason}")
        self.broker.publish(EventType.GAME_ENDED, data)
    
    def publish_piece_moved(self, piece_id: str, from_cell: tuple, to_cell: tuple):
        """Publish piece moved event"""
        # Extract player color from piece_id (e.g., "RW_(0,0)" -> "W")
        player_color = piece_id[1] if len(piece_id) >= 2 else "?"
        
        data = PieceMovedData(piece_id, from_cell, to_cell, player_color)
        data.timestamp = time.time()
        
        logger.info(f"Publishing PIECE_MOVED: {piece_id} from {from_cell} to {to_cell}")
        self.broker.publish(EventType.PIECE_MOVED, data)
    
    def publish_piece_captured(self, captured_piece_id: str, capturing_piece_id: str, cell: tuple):
        """Publish piece captured event"""
        data = PieceCapturedData(captured_piece_id, capturing_piece_id, cell)
        data.timestamp = time.time()
        
        logger.info(f"Publishing PIECE_CAPTURED: {capturing_piece_id} captures {captured_piece_id} at {cell}")
        self.broker.publish(EventType.PIECE_CAPTURED, data)
    
    def publish_pawn_promoted(self, old_piece_id: str, new_piece_id: str, cell: tuple, promoted_to: str):
        """Publish pawn promotion event"""
        from EventType import PawnPromotedData
        
        data = PawnPromotedData(old_piece_id, new_piece_id, cell, promoted_to)
        data.timestamp = time.time()
        
        logger.info(f"Publishing PAWN_PROMOTED: {old_piece_id} promoted to {promoted_to} at {cell}")
        self.broker.publish(EventType.PAWN_PROMOTED, data)


# Global publisher instance for easy access
game_event_publisher = GameEventPublisher()
