import os
import random
import string
from typing import List, Optional

from model.model import Board, Tile, Piece, MoveType, Color


class Move:
    def __init__(self, path: List[Tile]):
        self.path = path

    def add_tile(self, tile: Tile):
        self.path.append(tile)

    def __eq__(self, other):
        return self.path == other.path

    def __str__(self):
        tile_str = ", ".join([str(tile) for tile in self.path])
        return "[" + tile_str + "]"

    def inverse(self):
        reverse_move = self.path.copy()
        reverse_move.reverse()
        return Move(reverse_move)


class MoveNode:
    def __init__(self, move: Move, parent):
        self.move = move
        self.parent = parent  # type: MoveNode


class Ai:
    def __init__(self, board: Board, depth: int = 10):
        self.board = board
        self.depth = depth

    def next_move(self):
        moves = self.get_available_moves(self.board)
        move = self.get_best_move(moves)
        if move is not None:
            self.do_move(move, self.board)

    def get_available_moves(self, board) -> List[Move]:
        moves = []
        for row in range(8):
            for col in range(8):
                if (col + row) % 2 == 1:
                    moves += self.get_moves(Tile(row, col), board)
        return moves

    def do_move(self, move: Move, board):
        start, *rest = move.path
        for tile in rest:
            board.move_piece(start, tile)
            start = tile

    def undo_move(self, move: Move, board):
        inverse_move = move.inverse()
        start = inverse_move.path[0]
        end = inverse_move.path[-1]
        piece = board.get_piece_at(start)
        if piece is None:
            raise Exception("Cannot undo a move with no piece at the end")
        board.set_piece_at(end, piece)
        board.set_piece_at(start, None)
        if start.distance_from(end) == 2:
            board.set_piece_at(start.midpoint(end), Piece(Color(piece.color.value * -1)))

    def set_depth(self, depth):
        self.depth = depth

    def get_moves(self, start: Tile, board, only_jumps=False, first_move=None) -> List[Move]:
        moves = []
        tiles_to_check = list(start.get_valid_diagonal_tiles(2))
        if not only_jumps:
            tiles_to_check += list(start.get_valid_diagonal_tiles(1))
        for end in tiles_to_check:
            if first_move is not None:
                if Move([start, end]) == first_move.inverse():
                    continue
            move_type = board.classify_move(start, end)
            if move_type == MoveType.INVALID:
                continue
            if move_type == MoveType.NORMAL:
                moves.append(Move([start, end]))
            if move_type == MoveType.JUMP:
                piece =  board.get_piece_at(start)
                move = Move([start, end]) if first_move is None else first_move
                board.set_piece_at(start, None)
                board.set_piece_at(end, Piece(Color.RED))
                extra_jumps = self.get_moves(end, board, only_jumps=True, first_move=move)
                board.set_piece_at(start, piece)
                board.set_piece_at(end, None)
                if extra_jumps:
                    moves += [Move([start] + m.path) for m in extra_jumps]
                else:
                    moves.append(Move([start, end]))
        return moves

    def get_best_move(self, moves: List[Move]) -> Optional[Move]:
        if moves:
            index = random.randint(0, len(moves) - 1)
            return moves[index]
        return None
