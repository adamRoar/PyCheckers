import os
from enum import Enum
from typing import List, Optional


class Tile:
    def __init__(self, row: int, column: int):
        self.column = column
        self.row = row


class Color(Enum):
    RED = 1
    BLACK = -1


class MoveType(Enum):
    JUMP = 2
    NORMAL = 1
    INVALID = 0


class Piece:
    def __init__(self, color: Color):
        self.color = color
        self.is_king = False

    def __str__(self):
        result = "b" if self.color == Color.BLACK else "r"

        if self.is_king:
            result = result.upper()

        return result

    def king(self):
        self.is_king = True


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
                    if piece.color == Color.RED:
                        piece_value *= pow(self.row_multiplier, row)
                    else:
                        piece_value *= pow(self.row_multiplier, 7-row)
                    if piece.is_king:
                        piece_value *= self.king_multiplier
                    value += piece_value
        return value

    def move_piece(self, start: Tile, end: Tile) -> MoveType:
        move_type = self.classify_move(start, end)
        if move_type != MoveType.INVALID:
            piece_to_move = self.get_piece_at(start)
            self.set_piece_at(end, piece_to_move)
            self.set_piece_at(start, None)
        if move_type == MoveType.JUMP:
            jumped_location = Tile((start.row + end.row) // 2, (start.column + end.column) // 2)
            self.set_piece_at(jumped_location, None)
        return move_type

    def set_piece_at(self, position, piece):
        self.tiles[position.row][position.column] = piece

    def get_piece_at(self, position):
        return self.tiles[position.row][position.column]

    def classify_move(self, start: Tile, end: Tile) -> MoveType:
        piece_at_start = self.get_piece_at(start)
        if piece_at_start is None:
            return MoveType.INVALID
        piece_at_end = self.get_piece_at(end)
        if piece_at_end is not None:
            return MoveType.INVALID
        direction = piece_at_start.color.value
        move_type = self.check_move_type(start, end, piece_at_start, direction)
        if piece_at_start.is_king and move_type == MoveType.INVALID:
            move_type = self.check_move_type(start, end, piece_at_start, -direction)
        return move_type

    def check_move_type(self, start, end, piece_at_start, direction):
        move_type = MoveType.INVALID
        if end.row - start.row == 1 * direction:
            if end.column - start.column == 1 * direction or end.column - start.column == -1 * direction:
                move_type = MoveType.NORMAL
        if end.row - start.row == 2 * direction:
            if end.column - start.column == 2:
                jumped_piece = self.get_piece_at(Tile(start.row + 1 * direction, start.column + 1))
                if jumped_piece is not None and jumped_piece.color != piece_at_start.color:
                    move_type = MoveType.JUMP
            elif end.column - start.column == -2:
                jumped_piece = self.get_piece_at(Tile(start.row + 1 * direction, start.column - 1))
                if jumped_piece is not None and jumped_piece.color != piece_at_start.color:
                    move_type = MoveType.JUMP
        return move_type