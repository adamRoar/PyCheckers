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
        # Red pieces
        self.assertEqual(MoveType.NORMAL, self.b.move_piece(Tile(2, 1), Tile(3, 2)))
        self.assertEqual(MoveType.NORMAL, self.b.move_piece(Tile(2, 7), Tile(3, 6)))

        # Red moving back: INVALID
        self.assertEqual(MoveType.INVALID, self.b.move_piece(Tile(3, 2), Tile(2, 1)))

        # Black pieces
        self.assertEqual(MoveType.NORMAL, self.b.move_piece(Tile(5, 0), Tile(4, 1)))
        self.assertEqual(MoveType.NORMAL, self.b.move_piece(Tile(5, 6), Tile(4, 5)))

        # Black moving back: INVALID
        self.assertEqual(MoveType.INVALID, self.b.move_piece(Tile(4, 1), Tile(5, 0)))

    def test_king_normal_moves(self):
        piece = Piece(Color.RED)
        self.b.set_piece_at(Tile(4, 3), piece)
        piece.king()
        # red king moves backwards
        self.assertEqual(MoveType.NORMAL, self.b.move_piece(Tile(4, 3), Tile(3, 4)))
        # red king moves forwards
        self.assertEqual(MoveType.NORMAL, self.b.move_piece(Tile(3, 4), Tile(4, 3)))

    def test_red_jump_right(self):
        # Set a black piece to a jumpable position
        self.b.set_piece_at(Tile(3, 4), Piece(Color.BLACK))
        self.assertEqual(MoveType.JUMP, self.b.move_piece(Tile(2, 3), Tile(4, 5)))
        self.assertIsNone(self.b.get_piece_at(Tile(3, 4)))

    def test_red_jump_left(self):
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
        # Set up the red king
        piece = Piece(Color.RED)
        self.b.set_piece_at(Tile(6, 5), piece)
        piece.king()
        # King jumping back is a valid JUMP move
        self.assertEqual(MoveType.JUMP, self.b.move_piece(Tile(6, 5), Tile(4, 3)))
        # Piece the king jumped is removed
        self.assertIsNone(self.b.get_piece_at(Tile(5, 4)))

    def test_king_jump_back_right(self):
        # Set up the red king
        piece = Piece(Color.RED)
        self.b.set_piece_at(Tile(6, 1), piece)
        piece.king()
        # King jumping back is a valid JUMP move
        self.assertEqual(MoveType.JUMP, self.b.move_piece(Tile(6, 1), Tile(4, 3)))
        # Piece the king jumped is removed
        self.assertIsNone(self.b.get_piece_at(Tile(5, 2)))

    def test_same_color_jump_invalid(self):
        # Red jumping red is INVALID and does not remove other red piece
        self.assertEqual(MoveType.INVALID, self.b.move_piece(Tile(1, 2), Tile(3, 4)))
        self.assertIsNotNone(self.b.get_piece_at(Tile(2, 3)))

        # Black jumping black is INVALID and does not remove other black piece
        self.assertEqual(MoveType.INVALID, self.b.move_piece(Tile(6, 1), Tile(4, 3)))
        self.assertIsNotNone(self.b.get_piece_at(Tile(5, 2)))


if __name__ == '__main__':
    unittest.main()
