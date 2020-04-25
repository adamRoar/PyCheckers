import os
from enum import Enum
from typing import List


class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y


class Color(Enum):
    RED = 1
    BLACK = -1


class Piece:
    def __init__(self, color: Color):
        self.color = color
        self.is_king = False

    def __str__(self):
        result = "b" if self.color == Color.BLACK else "r"

        if self.is_king:
            result = result.upper()

        return result


class Board:
    def __init__(self):
        self.tiles = self.initialize_tiles()

    def initialize_tiles(self) -> List[List[Piece]]:
        tiles = [[None for i in range(8)] for i in range(8)]
        self.fill_tiles(tiles)
        return tiles

    @staticmethod
    def fill_tiles(tiles):
        for row in range(8):
            for col in range(8):
                if row <= 2 and (col + row) % 2 == 1:
                    tiles[row][col] = Piece(Color.RED)
                elif row >= 5 and (col + row) % 2 == 1:
                    tiles[row][col] = Piece(Color.BLACK)

    def __str__(self):
        result = ""
        for row in range(8):
            for col in range(8):
                piece = self.tiles[row][col]
                if piece is None:
                    result += " "
                else:
                    result += str(piece)
            result += os.linesep
        return result
