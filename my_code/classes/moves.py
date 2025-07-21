# import pathlib
# from typing import List, Tuple


# class Moves:
#     def __init__(self, rules: dict[str,list[tuple[int,int]]]):
#         self.rules = rules   # {"Knight":[(2,1),…]}
#     def valid_for(self, piece_type:str, x:int,y:int, W:int,H:int):
#         for dx,dy in self.rules.get(piece_type, []):
#             nx,ny = x+dx, y+dy
#             if 0<=nx<W and 0<=ny<H:
#                 yield nx,ny


# from typing import Dict, List, Tuple

# class Moves:
#     def __init__(self, rules: Dict[str, List[Tuple[int, int]]]):
#         self.rules = rules

#     def valid_for(self, piece_type: str, x: int, y: int, W: int, H: int):
#         for dx, dy in self.rules.get(piece_type, []):
#             nx, ny = x + dx, y + dy
#             if 0 <= nx < W and 0 <= ny < H:
#                 yield nx, ny


# Moves.py  – drop-in replacement
import pathlib
from typing import List, Tuple


class Moves:

    def __init__(self, txt_path: pathlib.Path, dims: Tuple[int, int]):
        """Initialize moves with rules from text file and board dimensions."""
        self.dims = dims  # Dimensions of the board (rows, cols)
        self.rules = self._load_rules(txt_path)  # Load movement rules from file

    def _load_rules(self, txt_path: pathlib.Path) -> List[Tuple[int, int]]:
        rules = []
        try:
            with txt_path.open('r') as file:
                for line in file:
                    # קח רק את שני הערכים הראשונים, התעלם משאר השורה
                    parts = line.strip().split(',')[:2]
                    if len(parts) != 2:
                        raise ValueError(f"Invalid format on line: {line}")
                    # אם יש נקודתיים, קח רק את המספר לפני הנקודתיים
                    dr = int(parts[0].split(':')[0])
                    dc = int(parts[1].split(':')[0])
                    rules.append((dr, dc))
        except Exception as e:
            raise ValueError(f"Error loading rules from {txt_path}: {e}")
        return rules

    def get_moves(self, r: int, c: int) -> List[Tuple[int, int]]:
        """Get all possible moves from a given position."""
        possible_moves = []
        for dr, dc in self.rules:
            new_r, new_c = r + dr, c + dc
            # Check if the new position is within board boundaries
            if 0 <= new_r < self.dims[0] and 0 <= new_c < self.dims[1]:
                possible_moves.append((new_r, new_c))
        return possible_moves



    # def _load_rules(self, txt_path: pathlib.Path) -> List[Tuple[int, int]]:
    #     """Load movement rules from a text file."""
    #     rules = []
    #     try:
    #         with txt_path.open('r') as file:
    #             for line in file:
    #                 # Parse each line as a tuple of integers (e.g., "1,2" -> (1, 2))
    #                 parts = line.strip().split(',')
    #                 if len(parts) != 2:
    #                     raise ValueError(f"Invalid format on line: {line}")
    #                 rules.append((int(parts[0]), int(parts[1])))
    #     except Exception as e:
    #         raise ValueError(f"Error loading rules from {txt_path}: {e}")
    #     return rules
