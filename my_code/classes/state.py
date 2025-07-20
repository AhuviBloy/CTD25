class State:
    def __init__(self, graphics:'Graphics', physics:'Physics'):
        self.graphics = graphics
        self.physics  = physics
        self.transitions: dict[str,"State"] = {}
    def add_transition(self, cmd_type:str, state:'State'):
        self.transitions[cmd_type] = state
    def on_command(self, cmd_type:str) -> "State":
        return self.transitions.get(cmd_type, self)
    def update(self, dt): self.physics.update(dt)
    def draw(self, canvas:'Img', x:int,y:int):
        sprite = self.graphics.current()
        sprite.draw_on(canvas, x, y)
