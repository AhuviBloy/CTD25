from .board import Board
from .physics import Physics

class PhysicsFactory:
    def __init__(self, board: Board):
        """Initialize physics factory with board."""
        self.board = board

    def create(self, start_cell, cfg) -> Physics:
        """Create a physics object with the given configuration."""
        return Physics(self.board, start_cell, cfg)
