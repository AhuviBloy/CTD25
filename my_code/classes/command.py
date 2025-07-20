from dataclasses import dataclass
from typing import List

@dataclass
class Command:
    timestamp: int       # ms
    piece_id: str
    type: str            # "Move" | "Jump" | …
    params: List[str]

    def __str__(self) -> str:
        return f"{self.timestamp}ms {self.type} {self.params} -> {self.piece_id}"
