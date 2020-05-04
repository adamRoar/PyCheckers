import copy
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
        return Move(self.path[::-1])


class MoveNode:
    def __init__(self, move: Optional[Move], parent, board):
        self.move = move
        self.parent = parent  # type: MoveNode
        self.children = []  # type: List[MoveNode]
        self.jumped_pieces = []
        self.value = 0.0
        self.board = board

    def get_node_value(self) -> float:
        if not self.children:
            return self.board.get_value()
        else:
            if self.board.turn == Color.RED:
                return max([child.get_node_value() for child in self.children])
            else:
                return min([child.get_node_value() for child in self.children])


class Ai:
    def __init__(self, board: Board, depth: int = 10):
        self.board = board
        self.depth = depth

    def next_move(self):
        move = self.get_best_move()
        if move is not None:
            self.do_move(move, self.board)

    def get_available_moves(self, board) -> List[Move]:
        moves = []
        for row in range(8):
            for col in range(8):
                if (col + row) % 2 == 1:
                    moves += self.get_moves(Tile(row, col), board)
        return moves

    def do_move(self, move: Move, board) -> List[Piece]:
        start, *rest = move.path
        jumped_pieces = []
        for tile in rest:
            move_type, jumped_piece = board.move_piece(start, tile)
            if move_type == MoveType.INVALID:
                raise Exception("Invalid move type")
            if jumped_piece is not None:
                jumped_pieces.append(jumped_piece)
            start = tile
        return jumped_pieces

    def undo_move(self, move: Move, jumped_pieces: List[Piece], must_jump: bool, board):
        inverse_move = move.inverse()
        self.undo_path(inverse_move.path, jumped_pieces, board)
        board.switch_turn_color()
        board.must_jump = must_jump

    def undo_path(self, path, jumped_pieces, board):
        start, *tail = path
        end = tail[0]
        piece = board.get_piece_at(start)
        if piece is None:
            raise Exception("Cannot undo a move with no piece at the end")
        if start.row == 0 or start.row == 7:
            piece.unking()
        board.set_piece_at(end, piece)
        board.set_piece_at(start, None)
        if start.distance_from(end) == 2:
            if not jumped_pieces:
                raise Exception("Attempting to undo a jump with no jumped pieces")
            jumped_piece = jumped_pieces.pop()
            board.set_piece_at(start.midpoint(end), jumped_piece)
            if jumped_piece.color == Color.RED:
                board.red_checkers += 1
            else:
                board.black_checkers += 1
        if len(tail) >= 2:
            self.undo_path(tail, jumped_pieces, board)

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
                piece = board.get_piece_at(start)
                move = Move([start, end]) if first_move is None else first_move
                board.set_piece_at(start, None)
                board.set_piece_at(end, piece)
                extra_jumps = self.get_moves(end, board, only_jumps=True, first_move=move)
                board.set_piece_at(start, piece)
                board.set_piece_at(end, None)
                if extra_jumps:
                    moves += [Move([start] + m.path) for m in extra_jumps]
                else:
                    moves.append(Move([start, end]))
        return moves

    def get_best_move(self) -> Optional[Move]:
        _, move = self.evaluate_tree(None, self.board, 1)
        return move

    def evaluate_tree(self, parent_move, board, depth) -> (float, Move):
        moves = self.get_available_moves(board)
        if not moves or depth > self.depth:
            return board.get_value(), parent_move
        children = []
        for move in moves:
            must_jump = board.must_jump
            jumped_pieces = self.do_move(move, board)
            child = self.evaluate_tree(move, board, depth + 1)
            children.append(child)
            self.undo_move(move, jumped_pieces, must_jump, board)
        if board.turn == Color.RED:
            max_value, child_move = max(children, key=self.get_value_from_child)
            if parent_move is not None:
                return max_value, parent_move
            else:
                return max_value, child_move
        else:
            min_value, child_move = min(children, key=self.get_value_from_child)
            if parent_move is not None:
                return min_value, parent_move
            else:
                return min_value, child_move

    def get_value_from_child(self, child):
        value, _ = child
        return value

    # def evaluate_tree(self, root_node) -> Move:
    #     best_move = None
    #     best_value = float("-inf")
    #     for child in root_node.children:
    #         value = child.get_node_value()
    #         if value > best_value:
    #             best_value = value
    #             best_move = child.move
    #     return best_move
