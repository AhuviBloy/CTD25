"""
Shared types and constants for the chess client-server architecture
"""
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
import json

@dataclass
class GameState:
    """Represents the current state of the game"""
    pieces: Dict[str, Dict[str, Any]]  # piece_id -> piece_data
    pos_to_piece: Dict[str, str]  # "row,col" -> piece_id
    current_player: str  # "W" or "B"
    game_time_ms: int
    white_score: int
    black_score: int
    game_ended: bool
    winner: Optional[str]
    last_move: Optional[Dict[str, Any]]
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**data)

@dataclass
class MoveRequest:
    """Request to move a piece"""
    player: str  # "W" or "B"
    from_pos: str  # algebraic notation like "e2"
    to_pos: str    # algebraic notation like "e4"
    piece_id: str
    timestamp: int
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**data)

@dataclass
class ServerResponse:
    """Response from server"""
    success: bool
    message: str
    game_state: Optional[GameState] = None
    error_code: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**data)

@dataclass
class ClientMessage:
    """Message from client to server"""
    type: str  # "move", "join", "get_state", "disconnect"
    player_id: str
    data: Optional[Dict[str, Any]] = None
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**data)

# Message types
MESSAGE_TYPES = {
    "MOVE": "move",
    "JOIN": "join", 
    "GET_STATE": "get_state",
    "DISCONNECT": "disconnect",
    "GAME_UPDATE": "game_update",
    "ERROR": "error"
}

# Game constants
PLAYERS = {
    "WHITE": "W",
    "BLACK": "B"
}
