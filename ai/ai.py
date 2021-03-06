import copy
import logging
import multiprocessing
import pdb
from concurrent.futures.thread import ThreadPoolExecutor
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


class Ai:
    def __init__(self, board: Board,  color: Color, depth: int = 4):
        self.board = board
        self.depth = depth
        self.color = color
        self.last_move = None
        logger = multiprocessing.log_to_stderr()
        logger.setLevel(5)

    def next_move(self, executor):
        move = self.get_best_move(executor)
        if move is not None:
            self.do_move(move, self.board)
            self.last_move = move

    def get_available_moves(self, board) -> List[Move]:
        moves = []
        for row in range(8):
            for col in range(8):
                if (col + row) % 2 == 1:
                    piece = board.get_piece_at(Tile(row, col))
                    if piece is not None and piece.color == board.turn:
                        moves += self.get_moves(Tile(row, col), board)
        return moves

    @staticmethod
    def do_move(move: Move, board) -> (List[Piece], bool):
        start, *rest = move.path
        initial_turn = board.turn
        piece_at_start = board.get_piece_at(start)
        was_king = piece_at_start.is_king
        jumped_pieces = []
        for tile in rest:
            move_type, jumped_piece = board.move_piece(start, tile)
            if move_type == MoveType.INVALID:
                raise Exception("Invalid move type")
            if jumped_piece is not None:
                jumped_pieces.append(jumped_piece)
            start = tile
        end_turn = board.turn
        if initial_turn == end_turn:
            raise Exception("Turn should change after a move")
        return jumped_pieces, was_king

    def undo_move(self, move: Move, jumped_pieces: List[Piece], must_jump: bool, was_king: bool, board):
        inverse_move = move.inverse()
        self.undo_path(inverse_move.path, jumped_pieces, was_king, board)
        board.switch_turn_color()
        board.must_jump = must_jump

    def undo_path(self, path, jumped_pieces, was_king: bool, board):
        start, *tail = path
        end = tail[0]
        piece = board.get_piece_at(start)
        if piece is None:
            raise Exception("Cannot undo a move with no piece at the end")
        if was_king:
            piece.king()
        else:
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
            self.undo_path(tail, jumped_pieces, was_king, board)

    def set_depth(self, depth):
        self.depth = depth

    def get_moves(self, start: Tile, board, only_jumps=False, previous_moves=None, counter=0) -> List[Move]:
        if previous_moves is None:
            previous_moves = []
        moves = []
        tiles_to_check = list(start.get_valid_diagonal_tiles(2))
        if not only_jumps:
            tiles_to_check += list(start.get_valid_diagonal_tiles(1))
        for end in tiles_to_check:
            current_move = Move([start, end])
            redid_move = False
            for move in previous_moves:
                if current_move == move.inverse() or current_move == move:
                    redid_move = True
                    break
            if redid_move:
                continue
            move_type = board.classify_move(start, end)
            if move_type == MoveType.INVALID:
                continue
            if move_type == MoveType.NORMAL:
                moves.append(current_move)
            if move_type == MoveType.JUMP:
                piece = board.get_piece_at(start)
                was_king = piece.is_king
                if end.is_end_row():
                    piece.king()
                board.set_piece_at(start, None)
                board.set_piece_at(end, piece)
                extra_jumps = self.get_moves(end, board, only_jumps=True,
                                             previous_moves=previous_moves + [current_move], counter=counter + 1)
                piece.king() if was_king else piece.unking()
                board.set_piece_at(start, piece)
                board.set_piece_at(end, None)
                if extra_jumps:
                    moves += [Move([start] + m.path) for m in extra_jumps]
                else:
                    moves.append(Move([start, end]))
        return moves

    def get_best_move(self, executor) -> Optional[Move]:
        _, move = self.evaluate_tree(None, self.board, 1, executor)
        return move

    def evaluate_tree(self, parent_move, board, depth, thread_pool: ThreadPoolExecutor) -> (float, Move):
        moves = self.get_available_moves(board)
        if not moves or depth > self.depth:
            return board.get_value(), parent_move
        if thread_pool is not None:
            children = thread_pool.map(self.evaluate_move, [(move, copy.deepcopy(board), depth, None, len(moves))
                                                            for move in moves])
        else:
            children = map(self.evaluate_move, [(move, board, depth, None, len(moves)) for move in moves])
        children = filter(lambda item: item is not None, children)
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

    def evaluate_move(self, params):
        move, board, depth, thread_pool, move_count = params
        if self.last_move is not None and move == self.last_move.inverse():
            if move_count == 1:
                return 0, move
            return None
        must_jump = board.must_jump
        jumped_pieces, was_king = self.do_move(move, board)
        val, child_move = self.evaluate_tree(move, board, depth + 1, thread_pool)
        self.undo_move(move, jumped_pieces, must_jump, was_king, board)
        return val, child_move

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
