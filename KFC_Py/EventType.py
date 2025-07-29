"""
Event Types for Kung Fu Chess Game
סוגי אירועים למשחק שח קונג פו
"""

class EventType:
    """Constants for all game event types"""
    
    # Game lifecycle events
    GAME_STARTED = "GAME_STARTED"
    GAME_ENDED = "GAME_ENDED"
    
    # Piece movement events  
    PIECE_MOVED = "PIECE_MOVED"        # When piece starts moving
    PIECE_CAPTURED = "PIECE_CAPTURED"  # When piece is captured
    
    # Special events (for future use)
    PIECE_JUMPED = "PIECE_JUMPED"      # When piece jumps
    PAWN_PROMOTED = "PAWN_PROMOTED"    # When pawn is promoted to another piece
    
    @classmethod
    def get_all_events(cls):
        """Get all event types"""
        return [
            cls.GAME_STARTED,
            cls.GAME_ENDED, 
            cls.PIECE_MOVED,
            cls.PIECE_CAPTURED,
            cls.PIECE_JUMPED,
            cls.PAWN_PROMOTED
        ]


# Event data structures
class GameStartedData:
    """Data for GAME_STARTED event"""
    def __init__(self, player1_name: str = "Player 1", player2_name: str = "Player 2"):
        self.player1_name = player1_name
        self.player2_name = player2_name
        self.timestamp = None


class GameEndedData:
    """Data for GAME_ENDED event"""
    def __init__(self, winner: str = None, reason: str = "checkmate"):
        self.winner = winner
        self.reason = reason
        self.timestamp = None


class PieceMovedData:
    """Data for PIECE_MOVED event"""
    def __init__(self, piece_id: str, from_cell: tuple, to_cell: tuple, player_color: str):
        self.piece_id = piece_id
        self.piece_type = piece_id[:2] if len(piece_id) >= 2 else piece_id  # e.g., "RW" from "RW_(0,0)"
        self.from_cell = from_cell
        self.to_cell = to_cell
        self.player_color = player_color  # "W" or "B"
        self.timestamp = None


class PieceCapturedData:
    """Data for PIECE_CAPTURED event"""
    def __init__(self, captured_piece_id: str, capturing_piece_id: str, cell: tuple):
        self.captured_piece_id = captured_piece_id
        self.capturing_piece_id = capturing_piece_id
        self.captured_piece_type = captured_piece_id[:2] if len(captured_piece_id) >= 2 else captured_piece_id
        self.capturing_piece_type = capturing_piece_id[:2] if len(capturing_piece_id) >= 2 else capturing_piece_id
        self.cell = cell
        self.captured_by_color = capturing_piece_id[1] if len(capturing_piece_id) >= 2 else "?"  # "W" or "B"
        self.timestamp = None
        
        # Piece values for scoring
        self.piece_values = {
            'PW': 1, 'PB': 1,  # Pawns
            'NW': 3, 'NB': 3,  # Knights  
            'BW': 3, 'BB': 3,  # Bishops
            'RW': 5, 'RB': 5,  # Rooks
            'QW': 9, 'QB': 9,  # Queens
            'KW': 0, 'KB': 0   # Kings
        }
        
        self.points = self.piece_values.get(self.captured_piece_type, 0)


class PawnPromotedData:
    """Data for PAWN_PROMOTED event"""
    def __init__(self, old_piece_id: str, new_piece_id: str, cell: tuple, promoted_to: str):
        self.old_piece_id = old_piece_id      # Original pawn ID (e.g., "PW_1")
        self.new_piece_id = new_piece_id      # New piece ID (e.g., "QW_1") 
        self.cell = cell                      # Position where promotion occurred
        self.promoted_to = promoted_to        # Piece type promoted to ("Q", "R", "B", "N")
        self.player_color = old_piece_id[1] if len(old_piece_id) >= 2 else "W"  # "W" or "B"
        self.timestamp = None
