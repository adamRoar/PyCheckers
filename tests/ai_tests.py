import unittest

from ai.ai import Ai, Move
from model.model import Board, Tile, Piece, Color


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.b = Board()
        self.ai = Ai(self.b, 1)

    def test_get_available_moves_with_no_jumps(self):
        self.b.turn = Color.RED
        self.assertEqual([Move([Tile(2, 1), Tile(3, 0)]),
                          Move([Tile(2, 1), Tile(3, 2)]),
                          Move([Tile(2, 3), Tile(3, 2)]),
                          Move([Tile(2, 3), Tile(3, 4)]),
                          Move([Tile(2, 5), Tile(3, 4)]),
                          Move([Tile(2, 5), Tile(3, 6)]),
                          Move([Tile(2, 7), Tile(3, 6)])],
                         self.ai.get_available_moves(self.b))

    def test_get_available_moves_with_jump(self):
        self.b.move_piece(Tile(5, 0), Tile(4, 1))
        self.b.move_piece(Tile(2, 1), Tile(3, 0))
        self.b.move_piece(Tile(5, 2), Tile(4, 3))
        print(self.b)
        print(", ".join([str(m) for m in self.ai.get_available_moves(self.b)]))

    def test_find_double_jump(self):
        self.b.move_piece(Tile(5, 0), Tile(4, 1))
        self.b.move_piece(Tile(2, 7), Tile(3, 6))
        self.b.move_piece(Tile(6, 1), Tile(5, 0))
        self.b.move_piece(Tile(1, 6), Tile(2, 7))
        self.b.move_piece(Tile(4, 1), Tile(3, 2))
        print(self.b)
        moves = self.ai.get_available_moves(self.b)
        print(", ".join([str(m) for m in moves]))
        self.assertEqual([Move([Tile(2, 1),
                                Tile(4, 3),
                                Tile(6, 1)]),
                          Move([Tile(2, 3),
                                Tile(4, 1)])],
                         moves)

    def test_undo_normal_move(self):
        move = Move([Tile(5, 2), Tile(4, 3)])
        self.ai.do_move(move, self.b)
        self.ai.undo_move(move, self.b)
        self.assertIsNone(self.b.get_piece_at(Tile(4, 3)))
        self.assertIsNotNone(self.b.get_piece_at(Tile(5, 2)))

    def test_undo_jump_move(self):
        self.test_get_available_moves_with_jump()
        move = Move([Tile(3, 0), Tile(5, 2)])
        jumped_pieces = self.ai.do_move(move, self.b)
        self.ai.undo_move(move, jumped_pieces, self.b)
        self.assertIsNone(self.b.get_piece_at(Tile(5, 2)))
        red_piece = self.b.get_piece_at(Tile(3, 0))
        self.assertIsNotNone(red_piece)
        self.assertEqual(jumped_pieces[0], red_piece)
        black_piece = self.b.get_piece_at(Tile(4, 1))
        self.assertIsNotNone(black_piece)
        self.assertEqual(Color.BLACK, black_piece.color)

    def test_undo_double_jump(self):
        piece = Piece(Color.RED)
        piece.king()
        self.b.set_piece_at(Tile(4, 3), piece)
        self.b.set_piece_at(Tile(1, 0), None)
        move = Move([Tile(5, 4), Tile(3, 2), Tile(1, 0)])
        jumped_pieces = self.ai.do_move(move, self.b)
        self.ai.undo_move(move, jumped_pieces, self.b)
        self.assertEqual(Color.RED, self.b.get_piece_at(Tile(2, 1)).color)
        # piece was added to array of jumped pieces by do_move and readded to the board by undo_move
        self.assertEqual(piece, self.b.get_piece_at(Tile(4, 3)))
        self.assertEqual(Color.BLACK, self.b.get_piece_at(Tile(5, 4)).color)
        self.assertIsNone(self.b.get_piece_at(Tile(1, 0)))
        self.assertIsNone(self.b.get_piece_at(Tile(3, 2)))


if __name__ == '__main__':
    unittest.main()
