import unittest

from ai.ai import Ai, Move
from model.model import Board, Tile, Piece, Color


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.b = Board()
        self.ai = Ai(self.b, 1)

    def test_equal_moves_take_leftmost(self):
        # only works for certain with depth=1
        self.ai.set_depth(1)
        self.b.move_piece(Tile(5, 0), Tile(4, 1))
        self.ai.next_move()
        self.assertIsNone(self.b.get_piece_at(Tile(2, 1)))
        self.assertIsNotNone(self.b.get_piece_at(Tile(3, 0)))

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


if __name__ == '__main__':
    unittest.main()
