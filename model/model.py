import os
from enum import Enum
from typing import List, Optional


class Tile:
    def __init__(self, row: int, column: int):
        self.column = column
        self.row = row

    def __add__(self, other):
        row = self.row + other.row
        col = self.column + other.column
        return Tile(row, col)

    def __eq__(self, other):
        return self.row == other.row and self.column == other.column

    def __str__(self):
        return "(" + str(self.row) + ", " + str(self.column) + ")"

    def is_valid(self):
        return (0 <= self.row <= 7) and (0 <= self.column <= 7)


class Color(Enum):
    RED = 1
    BLACK = -1


class MoveType(Enum):
    JUMP = 2
    NORMAL = 1
    INVALID = 0
    WRONG_PLAYER = -1


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
    def __init__(self, empty=False):
        self.row_multiplier = 1.05
        self.king_multiplier = 2
        self.tiles = self.initialize_tiles(empty)
        self.turn = Color.BLACK
        self.target_tile = None

    def initialize_tiles(self, empty) -> List[List[Optional[Piece]]]:
        tiles = [[None for i in range(8)] for i in range(8)]
        if not empty:
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
            self.target_tile = end
            if not self.can_jump(end):
                self.next_turn()
        if move_type == MoveType.NORMAL:
            self.next_turn()
        return move_type

    def next_turn(self):
        self.target_tile = None
        self.turn = Color(self.turn.value * -1)

    def set_piece_at(self, position, piece):
        self.tiles[position.row][position.column] = piece

    def get_piece_at(self, position):
        return self.tiles[position.row][position.column]

    def classify_move(self, start: Tile, end: Tile) -> MoveType:
        if self.target_tile is not None and self.target_tile != start:
            return MoveType.INVALID
        piece_at_start = self.get_piece_at(start)
        if piece_at_start is None:
            return MoveType.INVALID
        if piece_at_start.color != self.turn:
            return MoveType.WRONG_PLAYER
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

    def can_jump(self, tile: Tile) -> bool:
        jump_directions = [Tile(-2, -2), Tile(-2, 2), Tile(2, -2), Tile(2, 2)]
        for i in jump_directions:
            tile_to_check = tile + i
            if tile_to_check.is_valid():
                move_type = self.classify_move(tile, tile_to_check)
                if move_type == MoveType.JUMP:
                    return True
        return False
