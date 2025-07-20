class Physics:
    def __init__(self, board:'Board', speed:float=1.0):
        self.board = board
        self.speed = speed
        self.x = self.y = 0
    def reset(self, cell:tuple[int,int]): self.x,self.y = cell
    def update(self, dt_ms:int): pass   # add interpolation if תרצי
    def get_cell(self): return int(self.x), int(self.y)
