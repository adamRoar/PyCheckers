import os
import logging
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

    def midpoint(self, other):
        return Tile((self.row + other.row) // 2, (self.column + other.column) // 2)

    def __eq__(self, other):
        return self.row == other.row and self.column == other.column

    def __str__(self):
        return "(" + str(self.row) + ", " + str(self.column) + ")"

    def is_valid(self):
        return Tile.is_valid_tile(self)

    @staticmethod
    def is_valid_tile(tile):
        return (0 <= tile.row <= 7) and (0 <= tile.column <= 7)

    def get_valid_diagonal_tiles(self, distance: int):
        diagonal_tiles = [Tile(-distance, -distance),
                          Tile(-distance, distance),
                          Tile(distance, -distance),
                          Tile(distance, distance)]
        return filter(Tile.is_valid_tile, [self + tile for tile in diagonal_tiles])

    def distance_from(self, other):
        row_dif = abs(other.row - self.row)
        col_dif = abs(other.column - self.column)
        if row_dif != col_dif:
            raise Exception("Invalid tile distance (not diagonal)")
        return row_dif

    def is_end_row(self):
        return self.row == 0 or self.row == 7


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

    def unking(self):
        self.is_king = False


class Board:
    def __init__(self, empty=False):
        self.red_checkers = None
        self.black_checkers = None
        self.row_multiplier = 1.05
        self.end_multiplier = 1.02
        self.king_value = 2
        self.tiles = self.initialize_tiles(empty)
        self.turn = Color.BLACK
        self.target_tile = None
        self.must_jump = None
        self.emptied_tiles = []
        self.end_tile = None

    def initialize_tiles(self, empty) -> List[List[Optional[Piece]]]:
        tiles = [[None for i in range(8)] for i in range(8)]
        if not empty:
            self.fill_tiles(tiles)
            self.black_checkers = 12
            self.red_checkers = 12
        return tiles

    @staticmethod
    def fill_tiles(tiles):
        for row in range(8):
            for col in range(8):
                if row <= 2 and (col + row) % 2 == 1:
                    tiles[row][col] = Piece(Color.RED)
                elif row >= 5 and (col + row) % 2 == 1:
                    tiles[row][col] = Piece(Color.BLACK)

    def get_value(self) -> float:
        value = 0.0
        for row in range(8):
            for col in range(8):
                piece = self.tiles[row][col]
                if piece is not None:
                    piece_value = piece.color.value
                    if self.black_checkers < 6 or self.red_checkers < 6:
                        if piece.is_king:
                            piece_value = self.king_value * piece.color.value
                        if piece.color == Color.BLACK:
                            piece_value *= pow(self.end_multiplier, row)
                        else:
                            piece_value *= pow(self.end_multiplier, 7 - row)
                    else:
                        if piece.color == Color.RED:
                            piece_value *= pow(self.row_multiplier, row)
                        else:
                            piece_value *= pow(self.row_multiplier, 7-row)
                        if piece.is_king:
                            piece_value = self.king_value * piece.color.value
                    value += piece_value
        return value

    def move_piece(self, start: Tile, end: Tile) -> (MoveType, Optional[Piece]):
        move_type = self.classify_move(start, end)
        jumped_piece = None
        if move_type != MoveType.INVALID:
            piece_to_move = self.get_piece_at(start)
            self.set_piece_at(end, piece_to_move)
            self.set_piece_at(start, None)
            self.check_for_promotion(end)
            if move_type == MoveType.JUMP:
                jumped_location = start.midpoint(end)
                jumped_piece = self.get_piece_at(jumped_location)
                if jumped_piece.color == Color.RED:
                    self.red_checkers -= 1
                else:
                    self.black_checkers -= 1
                self.set_piece_at(jumped_location, None)
                self.target_tile = end
                if not self.can_jump(end):
                    self.next_turn(end)
            if move_type == MoveType.NORMAL:
                self.next_turn(end)
        return move_type, jumped_piece

    def next_turn(self, end: Tile):
        self.target_tile = None
        self.switch_turn_color()
        self.must_jump = self.has_jump(end)

    def set_piece_at(self, tile: Tile, piece: Optional[Piece]):
        self.tiles[tile.row][tile.column] = piece
        if piece is None:
            self.emptied_tiles.append(tile)

    def get_piece_at(self, tile):
        return self.tiles[tile.row][tile.column]

    def classify_move(self, start: Tile, end: Tile, piece_at_start=None) -> MoveType:
        if self.target_tile is not None and self.target_tile != start:
            return MoveType.INVALID
        if piece_at_start is None:
            piece_at_start = self.get_piece_at(start)
        if piece_at_start is None:
            return MoveType.INVALID
        if piece_at_start.color != self.turn:
            return MoveType.INVALID
        piece_at_end = self.get_piece_at(end)
        if piece_at_end is not None:
            return MoveType.INVALID
        direction = piece_at_start.color.value
        move_type = self.check_move_type(start, end, piece_at_start, direction)
        if piece_at_start.is_king and move_type == MoveType.INVALID:
            move_type = self.check_move_type(start, end, piece_at_start, -direction)
        if self.must_jump and move_type is not MoveType.JUMP:
            move_type = MoveType.INVALID
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
        tiles_to_check = tile.get_valid_diagonal_tiles(2)
        for end in tiles_to_check:
            if end.is_valid():
                move_type = self.classify_move(tile, end)
                if move_type == MoveType.JUMP:
                    return True
        return False

    def has_jump(self, end_tile: Tile):
        emptied_made_jump = any([self.check_tiles_for_jump(tile, 2) for tile in self.emptied_tiles])
        end_made_jump = self.check_tiles_for_jump(end_tile, 1)
        self.emptied_tiles = []
        return emptied_made_jump or end_made_jump

    def check_tiles_for_jump(self, tile, distance):
        tiles_to_check = tile.get_valid_diagonal_tiles(distance)
        for tile in tiles_to_check:
            if self.can_jump(tile):
                return True
        return False

    def winner(self) -> Optional[Color]:
        if self.black_checkers == 0:
            return Color.RED
        elif self.red_checkers == 0:
            return Color.BLACK
        else:
            return None

    def check_for_promotion(self, end):
        if end.is_end_row():
            self.get_piece_at(end).king()

    def switch_turn_color(self):
        self.turn = Color(self.turn.value * -1)

    def __str__(self):
        result = ""
        for row in range(8):
            for col in range(8):
                piece = self.tiles[row][col]
                if piece is None:
                    result += "-"
                else:
                    result += str(piece)
            result += os.linesep
        result += str(self.get_value())
        return result
