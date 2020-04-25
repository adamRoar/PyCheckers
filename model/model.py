import os
from enum import Enum
from typing import List, Optional


class Point:
    def __init__(self, row: int, column: int):
        self.column = column
        self.row = row


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
        self.row_multiplier = 1.05
        self.king_multiplier = 2
        self.tiles = self.initialize_tiles()

    def initialize_tiles(self) -> List[List[Optional[Piece]]]:
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
        result += str(self.get_value())
        return result

    def get_value(self) -> float:
        value = 0.0
        for row in range(8):
            for col in range(8):
                piece = self.tiles[row][col]
                if piece is not None:
                    piece_value = piece.color.value
                    if piece.is_king:
                        piece_value *= self.king_multiplier
                    if piece.color == Color.RED:
                        piece_value *= pow(self.row_multiplier, row)
                    else:
                        piece_value *= pow(self.row_multiplier, 7-row)
                    value += piece_value
        return value

    def move_piece(self, start: Point, end: Point):
        piece_to_move = self.tiles[start.row][start.column]
        self.tiles[end.row][end.column] = piece_to_move
        self.tiles[start.row][start.column] = None
