from .command import Command
class Piece:
    def __init__(self, piece_id:str, start_state:'State'):
        self.id   = piece_id
        self.state= start_state
    def on_command(self, cmd:Command):
        self.state = self.state.on_command(cmd.type)
    def update(self, dt): self.state.update(dt)
    def draw(self, board:'Board'):
        x,y = self.state.physics.get_cell()
        self.state.draw(board.img, x*board.cell_W_pix, y*board.cell_H_pix)
