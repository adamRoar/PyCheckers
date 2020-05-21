import copy
import unittest
from model.model import Board, Tile, MoveType, Color, Piece


class MyTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.b = Board()

    def tearDown(self) -> None:
        print()
        print(self._testMethodName)
        print(self.b)

    def test_normal_moves(self):
        # default turn is BLACK so we change it to RED first
        self.b.turn = Color.RED
        # Alternating forward moves
        self.assertMoveType(MoveType.NORMAL, self.b.move_piece(Tile(2, 1), Tile(3, 2)))
        self.assertMoveType(MoveType.NORMAL, self.b.move_piece(Tile(5, 6), Tile(4, 7)))
        self.assertMoveType(MoveType.NORMAL, self.b.move_piece(Tile(2, 7), Tile(3, 6)))
        self.assertMoveType(MoveType.NORMAL, self.b.move_piece(Tile(5, 2), Tile(4, 1)))

        # Red moving back: INVALID
        self.assertMoveType(MoveType.INVALID, self.b.move_piece(Tile(3, 2), Tile(2, 1)))
        # INVALID RED move should not change turn so we change it manually to BLACK
        self.b.turn = Color.BLACK
        # Black moving back: INVALID
        self.assertMoveType(MoveType.INVALID, self.b.move_piece(Tile(4, 1), Tile(5, 0)))

    def test_king_normal_moves(self):
        # default turn is BLACK so we change it to RED first
        self.b.turn = Color.RED
        piece = Piece(Color.RED)
        self.b.set_piece_at(Tile(4, 3), piece)
        piece.king()
        # red king moves backwards
        self.assertMoveType(MoveType.NORMAL, self.b.move_piece(Tile(4, 3), Tile(3, 4)))
        # RED shouldn't be able to move 2 turns in a row so we set to RED
        self.b.turn = Color.RED
        # red king moves forwards
        self.assertMoveType(MoveType.NORMAL, self.b.move_piece(Tile(3, 4), Tile(4, 3)))

    def test_red_jump_right(self):
        # default turn is BLACK so we change it to RED first
        self.b.turn = Color.RED
        # Set a black piece to a jumpable position
        self.b.set_piece_at(Tile(3, 4), Piece(Color.BLACK))
        self.assertMoveType(MoveType.JUMP, self.b.move_piece(Tile(2, 3), Tile(4, 5)))
        self.assertIsNone(self.b.get_piece_at(Tile(3, 4)))

    def test_red_jump_left(self):
        # default turn is BLACK so we change it to RED first
        self.b.turn = Color.RED
        # Set a black piece to a jumpable position
        self.b.set_piece_at(Tile(3, 4), Piece(Color.BLACK))
        self.assertMoveType(MoveType.JUMP, self.b.move_piece(Tile(2, 5), Tile(4, 3)))
        self.assertIsNone(self.b.get_piece_at(Tile(3, 4)))

    def test_black_jump_right(self):
        # Set a red piece to a jumpable position
        self.b.set_piece_at(Tile(4, 3), Piece(Color.RED))
        self.assertMoveType(MoveType.JUMP, self.b.move_piece(Tile(5, 2), Tile(3, 4)))
        self.assertIsNone(self.b.get_piece_at(Tile(4, 3)))

    def test_black_jump_left(self):
        # Set a red piece to a jumpable position
        self.b.set_piece_at(Tile(4, 3), Piece(Color.RED))
        self.assertMoveType(MoveType.JUMP, self.b.move_piece(Tile(5, 4), Tile(3, 2)))
        self.assertIsNone(self.b.get_piece_at(Tile(4, 3)))

    def test_king_jump_back_left(self):
        # default turn is BLACK so we change it to RED first
        self.b.turn = Color.RED
        # Set up the red king
        piece = Piece(Color.RED)
        self.b.set_piece_at(Tile(6, 5), piece)
        piece.king()
        # King jumping back is a valid JUMP move
        self.assertMoveType(MoveType.JUMP, self.b.move_piece(Tile(6, 5), Tile(4, 3)))
        # Piece the king jumped is removed
        self.assertIsNone(self.b.get_piece_at(Tile(5, 4)))

    def test_king_jump_back_right(self):
        # default turn is BLACK so we change it to RED first
        self.b.turn = Color.RED
        # Set up the red king
        piece = Piece(Color.RED)
        self.b.set_piece_at(Tile(6, 1), piece)
        piece.king()
        # King jumping back is a valid JUMP move
        self.assertMoveType(MoveType.JUMP, self.b.move_piece(Tile(6, 1), Tile(4, 3)))
        # Piece the king jumped is removed
        self.assertIsNone(self.b.get_piece_at(Tile(5, 2)))

    def test_same_color_jump_invalid(self):
        # default turn is BLACK so we change it to RED first
        self.b.turn = Color.RED
        # Red jumping red is INVALID and does not remove other red piece
        self.assertMoveType(MoveType.INVALID, self.b.move_piece(Tile(1, 2), Tile(3, 4)))
        self.assertIsNotNone(self.b.get_piece_at(Tile(2, 3)))
        # INVALID RED move should not change turn so we change it manually to BLACK
        self.b.turn = Color.BLACK
        # Black jumping black is INVALID and does not remove other black piece
        self.assertMoveType(MoveType.INVALID, self.b.move_piece(Tile(6, 1), Tile(4, 3)))
        self.assertIsNotNone(self.b.get_piece_at(Tile(5, 2)))

    def test_wrong_player_cannot_move(self):
        # Black goes first - red move here should be INVALID
        self.assertMoveType(MoveType.INVALID, self.b.move_piece(Tile(2, 1), Tile(3, 2)))

    def test_turns_alternate(self):
        self.assertMoveType(MoveType.NORMAL, self.b.move_piece(Tile(5, 0), Tile(4, 1)))
        self.assertMoveType(MoveType.NORMAL, self.b.move_piece(Tile(2, 1), Tile(3, 2)))

    def test_can_jump(self):
        self.b.set_piece_at(Tile(4, 3), Piece(Color.RED))
        self.assertEqual(True, self.b.can_jump(Tile(5, 4)))

    def test_tile_addition(self):
        self.assertEqual(Tile(3, 4), Tile(1, 3) + Tile(2, 1))
        self.assertEqual(Tile(1, 1), Tile(4, 2) + Tile(-3, -1))

    def test_double_jump(self):
        self.b.set_piece_at(Tile(4, 3), Piece(Color.RED))
        self.b.set_piece_at(Tile(1, 0), None)
        self.assertMoveType(MoveType.JUMP, self.b.move_piece(Tile(5, 4), Tile(3, 2)))
        # testing that pieces other than target_tile cannot move during a double jump
        self.assertMoveType(MoveType.INVALID, self.b.move_piece(Tile(5, 0), Tile(4, 1)))
        self.assertEqual(self.b.turn, Color.BLACK)
        self.assertMoveType(MoveType.JUMP, self.b.move_piece(Tile(3, 2), Tile(1, 0)))
        self.assertIsNone(self.b.target_tile)
        self.assertEqual(self.b.turn, Color.RED)

    def test_cannot_move_wrong_piece_after_jump(self):
        self.b.set_piece_at(Tile(4, 3), Piece(Color.RED))
        self.b.set_piece_at(Tile(1, 0), None)
        self.assertMoveType(MoveType.JUMP, self.b.move_piece(Tile(5, 4), Tile(3, 2)))
        self.assertEqual(self.b.turn, Color.BLACK)
        self.assertMoveType(MoveType.INVALID, self.b.move_piece(Tile(5, 0), Tile(4, 1)))

    def test_normal_move_after_jump_good(self):
        self.test_double_jump()
        self.assertMoveType(MoveType.NORMAL, self.b.move_piece(Tile(2, 7), Tile(3, 6)))

    def test_triple_jump(self):
        self.b = Board(True)
        self.b.turn = Color.RED
        self.b.red_checkers = 1
        self.b.black_checkers = 3
        self.b.set_piece_at(Tile(0, 0), Piece(Color.RED))
        self.b.set_piece_at(Tile(1, 1), Piece(Color.BLACK))
        self.b.set_piece_at(Tile(3, 3), Piece(Color.BLACK))
        self.b.set_piece_at(Tile(5, 5), Piece(Color.BLACK))
        print(self.b)
        self.assertMoveType(MoveType.JUMP, self.b.move_piece(Tile(0, 0), Tile(2, 2)))
        print(self.b)
        self.assertMoveType(MoveType.JUMP, self.b.move_piece(Tile(2, 2), Tile(4, 4)))
        print(self.b)
        self.assertMoveType(MoveType.JUMP, self.b.move_piece(Tile(4, 4), Tile(6, 6)))
        print(self.b)
        self.assertEqual(self.b.turn, Color.BLACK)

    def test_king_triple_jump_backwards(self):
        self.b = Board(True)
        king = Piece(Color.BLACK)
        king.king()
        self.b.red_checkers = 3
        self.b.black_checkers = 1
        self.b.set_piece_at(Tile(0, 0), king)
        self.b.set_piece_at(Tile(1, 1), Piece(Color.RED))
        self.b.set_piece_at(Tile(3, 3), Piece(Color.RED))
        self.b.set_piece_at(Tile(5, 5), Piece(Color.RED))
        print(self.b)
        self.assertMoveType(MoveType.JUMP, self.b.move_piece(Tile(0, 0), Tile(2, 2)))
        print(self.b)
        self.assertMoveType(MoveType.JUMP, self.b.move_piece(Tile(2, 2), Tile(4, 4)))
        print(self.b)
        self.assertMoveType(MoveType.JUMP, self.b.move_piece(Tile(4, 4), Tile(6, 6)))
        print(self.b)
        self.assertEqual(self.b.turn, Color.RED)

    def test_has_jump_after_normal_with_no_jump(self):
        self.b.turn = Color.RED
        self.assertMoveType(MoveType.NORMAL, self.b.move_piece(Tile(2, 1), Tile(3, 2)))
        self.assertFalse(self.b.must_jump)

    def test_has_jump_after_normal_with_jump(self):
        self.test_has_jump_after_normal_with_no_jump()
        self.assertMoveType(MoveType.NORMAL, self.b.move_piece(Tile(5, 4), Tile(4, 3)))
        self.assertTrue(self.b.must_jump)

    def test_has_jump_after_jump(self):
        self.test_has_jump_after_normal_with_jump()
        self.assertMoveType(MoveType.JUMP, self.b.move_piece(Tile(3, 2), Tile(5, 4)))
        self.assertTrue(self.b.must_jump)

    def test_cannot_move_piece_if_has_jump(self):
        self.test_has_jump_after_normal_with_jump()
        self.assertMoveType(MoveType.INVALID, self.b.move_piece(Tile(2, 7), Tile(3, 6)))

    def test_win_condition(self):
        self.b = Board(True)
        self.b.set_piece_at(Tile(4, 1), Piece(Color.RED))
        self.b.set_piece_at(Tile(5, 2), Piece(Color.BLACK))
        self.b.red_checkers = 1
        self.b.black_checkers = 1
        self.b.move_piece(Tile(5, 2), Tile(3, 0))
        self.assertEqual(Color.BLACK, self.b.winner())

    def test_wrong_player(self):
        self.assertMoveType(MoveType.INVALID, self.b.move_piece(Tile(2, 1), Tile(3, 2)))
        self.assertIsNone(self.b.get_piece_at(Tile(3, 2)))
        self.assertIsNotNone(self.b.get_piece_at(Tile(2, 1)))
        self.assertEqual(Color.BLACK, self.b.turn)

    def test_promotion(self):
        self.b = Board(True)
        self.b.set_piece_at(Tile(1, 0), Piece(Color.BLACK))
        self.b.move_piece(Tile(1, 0), Tile(0, 1))
        self.assertEqual(True, self.b.get_piece_at(Tile(0, 1)).is_king)

    def test_deep_copy_board(self):
        nb = copy.deepcopy(self.b)
        piece = self.b.get_piece_at(Tile(2, 1))
        piece.king()
        self.assertEqual(False, nb.get_piece_at(Tile(2, 1)).is_king)
        self.b.move_piece(Tile(2, 1), Tile(3, 0))
        self.assertEqual(None, nb.get_piece_at(Tile(3, 0)))
        
    def assertMoveType(self, expected: MoveType, actual: (MoveType, Piece)):
        actual_move, _ = actual
        self.assertEqual(expected, actual_move)


if __name__ == '__main__':
    unittest.main()
