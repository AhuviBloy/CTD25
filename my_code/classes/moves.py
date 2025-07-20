class Moves:
    def __init__(self, rules: dict[str,list[tuple[int,int]]]):
        self.rules = rules   # {"Knight":[(2,1),…]}
    def valid_for(self, piece_type:str, x:int,y:int, W:int,H:int):
        for dx,dy in self.rules.get(piece_type, []):
            nx,ny = x+dx, y+dy
            if 0<=nx<W and 0<=ny<H:
                yield nx,ny
