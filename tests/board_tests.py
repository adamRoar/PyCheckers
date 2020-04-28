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
        # Alternating foward moves
        self.assertEqual(MoveType.NORMAL, self.b.move_piece(Tile(2, 1), Tile(3, 2)))
        self.assertEqual(MoveType.NORMAL, self.b.move_piece(Tile(5, 0), Tile(4, 1)))
        self.assertEqual(MoveType.NORMAL, self.b.move_piece(Tile(2, 7), Tile(3, 6)))
        self.assertEqual(MoveType.NORMAL, self.b.move_piece(Tile(5, 6), Tile(4, 5)))

        # Red moving back: INVALID
        self.assertEqual(MoveType.INVALID, self.b.move_piece(Tile(3, 2), Tile(2, 1)))
        # INVALID RED move should not change turn so we change it manually to BLACK
        self.b.turn = Color.BLACK
        # Black moving back: INVALID
        self.assertEqual(MoveType.INVALID, self.b.move_piece(Tile(4, 1), Tile(5, 0)))

    def test_king_normal_moves(self):
        # default turn is BLACK so we change it to RED first
        self.b.turn = Color.RED
        piece = Piece(Color.RED)
        self.b.set_piece_at(Tile(4, 3), piece)
        piece.king()
        # red king moves backwards
        self.assertEqual(MoveType.NORMAL, self.b.move_piece(Tile(4, 3), Tile(3, 4)))
        # RED shouldn't be able to move 2 turns in a row so we set to RED
        self.b.turn = Color.RED
        # red king moves forwards
        self.assertEqual(MoveType.NORMAL, self.b.move_piece(Tile(3, 4), Tile(4, 3)))

    def test_red_jump_right(self):
        # default turn is BLACK so we change it to RED first
        self.b.turn = Color.RED
        # Set a black piece to a jumpable position
        self.b.set_piece_at(Tile(3, 4), Piece(Color.BLACK))
        self.assertEqual(MoveType.JUMP, self.b.move_piece(Tile(2, 3), Tile(4, 5)))
        self.assertIsNone(self.b.get_piece_at(Tile(3, 4)))

    def test_red_jump_left(self):
        # default turn is BLACK so we change it to RED first
        self.b.turn = Color.RED
        # Set a black piece to a jumpable position
        self.b.set_piece_at(Tile(3, 4), Piece(Color.BLACK))
        self.assertEqual(MoveType.JUMP, self.b.move_piece(Tile(2, 5), Tile(4, 3)))
        self.assertIsNone(self.b.get_piece_at(Tile(3, 4)))

    def test_black_jump_right(self):
        # Set a red piece to a jumpable position
        self.b.set_piece_at(Tile(4, 3), Piece(Color.RED))
        self.assertEqual(MoveType.JUMP, self.b.move_piece(Tile(5, 2), Tile(3, 4)))
        self.assertIsNone(self.b.get_piece_at(Tile(4, 3)))

    def test_black_jump_left(self):
        # Set a red piece to a jumpable position
        self.b.set_piece_at(Tile(4, 3), Piece(Color.RED))
        self.assertEqual(MoveType.JUMP, self.b.move_piece(Tile(5, 4), Tile(3, 2)))
        self.assertIsNone(self.b.get_piece_at(Tile(4, 3)))

    def test_king_jump_back_left(self):
        # default turn is BLACK so we change it to RED first
        self.b.turn = Color.RED
        # Set up the red king
        piece = Piece(Color.RED)
        self.b.set_piece_at(Tile(6, 5), piece)
        piece.king()
        # King jumping back is a valid JUMP move
        self.assertEqual(MoveType.JUMP, self.b.move_piece(Tile(6, 5), Tile(4, 3)))
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
        self.assertEqual(MoveType.JUMP, self.b.move_piece(Tile(6, 1), Tile(4, 3)))
        # Piece the king jumped is removed
        self.assertIsNone(self.b.get_piece_at(Tile(5, 2)))

    def test_same_color_jump_invalid(self):
        # default turn is BLACK so we change it to RED first
        self.b.turn = Color.RED
        # Red jumping red is INVALID and does not remove other red piece
        self.assertEqual(MoveType.INVALID, self.b.move_piece(Tile(1, 2), Tile(3, 4)))
        self.assertIsNotNone(self.b.get_piece_at(Tile(2, 3)))
        # INVALID RED move should not change turn so we change it manually to BLACK
        self.b.turn = Color.BLACK
        # Black jumping black is INVALID and does not remove other black piece
        self.assertEqual(MoveType.INVALID, self.b.move_piece(Tile(6, 1), Tile(4, 3)))
        self.assertIsNotNone(self.b.get_piece_at(Tile(5, 2)))

    def test_wrong_player_cannot_move(self):
        # Black goes first - red move here should be INVALID
        self.assertEqual(MoveType.WRONG_PLAYER, self.b.move_piece(Tile(2, 1), Tile(3, 2)))

    def test_turns_alternate(self):
        self.assertEqual(MoveType.NORMAL, self.b.move_piece(Tile(5, 0), Tile(4, 1)))
        self.assertEqual(MoveType.NORMAL, self.b.move_piece(Tile(2, 1), Tile(3, 2)))

    def test_can_jump(self):
        self.b.set_piece_at(Tile(4, 3), Piece(Color.RED))
        self.assertEqual(True, self.b.can_jump(Tile(5, 4)))

    def test_tile_addition(self):
        self.assertEqual(Tile(3, 4), Tile(1, 3) + Tile(2, 1))
        self.assertEqual(Tile(1, 1), Tile(4, 2) + Tile(-3, -1))

    def test_double_jump(self):
        self.b.set_piece_at(Tile(4, 3), Piece(Color.RED))
        self.b.set_piece_at(Tile(1, 0), None)
        self.assertEqual(MoveType.JUMP, self.b.move_piece(Tile(5, 4), Tile(3, 2)))
        self.assertEqual(self.b.turn, Color.BLACK)
        self.assertEqual(MoveType.JUMP, self.b.move_piece(Tile(3, 2), Tile(1, 0)))
        self.assertIsNone(self.b.target_tile)
        self.assertEqual(self.b.turn, Color.RED)

    def test_cannot_move_wrong_piece_after_jump(self):
        self.b.set_piece_at(Tile(4, 3), Piece(Color.RED))
        self.b.set_piece_at(Tile(1, 0), None)
        self.assertEqual(MoveType.JUMP, self.b.move_piece(Tile(5, 4), Tile(3, 2)))
        self.assertEqual(self.b.turn, Color.BLACK)
        self.assertEqual(MoveType.INVALID, self.b.move_piece(Tile(5, 0), Tile(4, 1)))

    def test_normal_move_after_jump_good(self):
        self.test_double_jump()
        self.assertEqual(MoveType.NORMAL, self.b.move_piece(Tile(2, 7), Tile(3, 6)))

    def test_triple_jump(self):
        self.b = Board(True)
        self.b.turn = Color.RED
        self.b.set_piece_at(Tile(0, 0), Piece(Color.RED))
        self.b.set_piece_at(Tile(1, 1), Piece(Color.BLACK))
        self.b.set_piece_at(Tile(3, 3), Piece(Color.BLACK))
        self.b.set_piece_at(Tile(5, 5), Piece(Color.BLACK))
        print(self.b)
        self.assertEqual(MoveType.JUMP, self.b.move_piece(Tile(0, 0), Tile(2, 2)))
        print(self.b)
        self.assertEqual(MoveType.JUMP, self.b.move_piece(Tile(2, 2), Tile(4, 4)))
        print(self.b)
        self.assertEqual(MoveType.JUMP, self.b.move_piece(Tile(4, 4), Tile(6, 6)))
        print(self.b)
        self.assertEqual(self.b.turn, Color.BLACK)

    def test_king_triple_jump_backwards(self):
        self.b = Board(True)
        king = Piece(Color.BLACK)
        king.king()
        self.b.set_piece_at(Tile(0, 0), king)
        self.b.set_piece_at(Tile(1, 1), Piece(Color.RED))
        self.b.set_piece_at(Tile(3, 3), Piece(Color.RED))
        self.b.set_piece_at(Tile(5, 5), Piece(Color.RED))
        print(self.b)
        self.assertEqual(MoveType.JUMP, self.b.move_piece(Tile(0, 0), Tile(2, 2)))
        print(self.b)
        self.assertEqual(MoveType.JUMP, self.b.move_piece(Tile(2, 2), Tile(4, 4)))
        print(self.b)
        self.assertEqual(MoveType.JUMP, self.b.move_piece(Tile(4, 4), Tile(6, 6)))
        print(self.b)
        self.assertEqual(self.b.turn, Color.RED)


if __name__ == '__main__':
    unittest.main()
