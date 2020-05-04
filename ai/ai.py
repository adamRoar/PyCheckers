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
            _, jumped_piece = board.move_piece(start, tile)
            if jumped_piece is not None:
                jumped_pieces.append(jumped_piece)
            start = tile
        return jumped_pieces

    def undo_move(self, move: Move, jumped_pieces: List[Piece], board):
        inverse_move = move.inverse()
        self.undo_path(inverse_move.path, jumped_pieces, board)

    def undo_path(self, path, jumped_pieces, board):
        start, *tail = path
        end = tail[0]
        piece = board.get_piece_at(start)
        if piece is None:
            raise Exception("Cannot undo a move with no piece at the end")
        board.set_piece_at(end, piece)
        board.set_piece_at(start, None)
        if start.distance_from(end) == 2:
            board.set_piece_at(start.midpoint(end), jumped_pieces.pop())
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
                board.set_piece_at(end, Piece(Color.RED))
                extra_jumps = self.get_moves(end, board, only_jumps=True, first_move=move)
                board.set_piece_at(start, piece)
                board.set_piece_at(end, None)
                if extra_jumps:
                    moves += [Move([start] + m.path) for m in extra_jumps]
                else:
                    moves.append(Move([start, end]))
        return moves

    def get_best_move(self) -> Optional[Move]:
        root_node = MoveNode(None, None, self.board)
        self.build_tree(root_node, self.board, 1)
        return self.evaluate_tree(root_node)

    def build_tree(self, root_node, board, depth):
        if depth > self.depth:
            return
        moves = self.get_available_moves(board)
        if not moves:
            return None
        for move in moves:
            copy_board = copy.deepcopy(board)
            self.do_move(move, copy_board)
            node = MoveNode(move, root_node, copy_board)
            root_node.children.append(node)
            self.build_tree(node, copy_board, depth + 1)

    def evaluate_tree(self, root_node) -> Move:
        best_move = None
        best_value = float("-inf")
        for child in root_node.children:
            value = child.get_node_value()
            if value > best_value:
                best_value = value
                best_move = child.move
        return best_move
