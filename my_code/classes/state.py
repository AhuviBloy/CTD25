# class State:
#     def __init__(self, graphics, physics, moves):
#         self.graphics = graphics
#         self.physics = physics
#         self.moves = moves
#         self.transitions: dict[str,"State"] = {}
#     def add_transition(self, cmd_type:str, state:'State'):
#         self.transitions[cmd_type] = state
#     def on_command(self, cmd_type:str) -> "State":
#         return self.transitions.get(cmd_type, self)
#     def update(self, dt): self.physics.update(dt)
#     def draw(self, canvas:'Img', x:int,y:int):
#         sprite = self.graphics.current()
#         sprite.draw_on(canvas, x, y)

from .command import Command
from .moves import Moves
from .graphics import Graphics
from .physics import Physics
from typing import Dict

class State:
    def __init__(self, moves: Moves, graphics: Graphics, physics: Physics):
        """Initialize state with moves, graphics, and physics components."""
        self.moves = moves
        self.graphics = graphics
        self.physics = physics
        self.transitions: Dict[str, State] = {}
        self.current_cmd: Command | None = None

    def set_transition(self, event: str, target: "State"):
        """Set a transition from this state to another state on an event."""
        self.transitions[event] = target

    def reset(self, cmd: Command):
        self.current_cmd = cmd
        self.graphics.reset(cmd)
    
        # אם הפקודה לא כוללת target_cell, שמרי על התא הנוכחי
        if not hasattr(cmd, "target_cell") or cmd.target_cell is None:
            cmd.target_cell = self.physics.cell

        self.physics.reset(cmd)
        # """Reset the state with a new command."""
        # self.current_cmd = cmd
        # self.graphics.reset(cmd)
        # self.physics.reset(cmd)

    def can_transition(self, now_ms: int) -> bool:
        """Check if the state can transition."""
        # ברירת מחדל – תמיד אפשר, ניתן לשנות לפי סוג מצב
        return True

    def get_state_after_command(self, cmd: Command, now_ms: int) -> "State":
        """Get the next state after processing a command."""
        if cmd.type in self.transitions:
            return self.transitions[cmd.type]
        return None

    def update(self, now_ms: int) -> "State":
        """Update the state based on current time."""
        self.graphics.update(now_ms)
        self.physics.update(now_ms)
        return self

    def get_command(self) -> Command:
        """Get the current command for this state."""
        return self.current_cmd
