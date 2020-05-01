import sys
import pygame
from pygame.event import Event
from pygame.surface import Surface

from gui.settings import Settings
from model.model import Board, Color, Tile, MoveType


class PyCheckers:
    def __init__(self):
        pygame.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((self.settings.screen_width,
                                               self.settings.screen_height))  # type: Surface
        pygame.display.set_caption("PyCheckers")
        self.board = Board()
        self.selected_tile = None

    def run_game(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click()
            self.draw_board()
            pygame.display.flip()

    def draw_board(self):
        self.draw_tiles()
        self.draw_pieces()

    def draw_tiles(self):
        self.screen.fill(self.settings.white_tile_color)
        for row in range(8):
            for col in range(8):
                if (row + col) % 2 == 1:
                    pygame.draw.rect(self.screen, self.settings.black_tile_color, (row * 100, col * 100, 100, 100))
        if self.selected_tile is not None:
            pygame.draw.rect(self.screen, self.settings.selected_tile_color, (self.selected_tile.column * 100,
                                                                              self.selected_tile.row * 100,
                                                                              100, 100))

    def draw_pieces(self):
        y = 0
        for row in self.board.tiles:
            x = 0
            for piece in row:
                if piece is not None:
                    color = self.settings.red_piece_color if piece.color == Color.RED else self.settings.black_piece_color
                    pygame.draw.circle(self.screen, color, (x * 100 + 50, y * 100 + 50), self.settings.piece_radius, 0)
                    if piece.is_king:
                        pygame.draw.rect(self.screen, self.settings.white_tile_color, (x * 100 + 40, y * 100 + 40, 20, 20))
                x += 1
            y += 1

    def handle_click(self):
        (x, y) = pygame.mouse.get_pos()
        row = int((y - y % 100) / 100)
        column = int((x - x % 100) / 100)
        clicked_tile = Tile(row, column)
        if self.selected_tile is None:
            self.selected_tile = clicked_tile
        else:
            move_type = self.board.move_piece(self.selected_tile, clicked_tile)
            if move_type == MoveType.JUMP and self.board.can_jump(clicked_tile):
                self.selected_tile = clicked_tile
            else:
                self.selected_tile = None


if __name__ == '__main__':
    pc = PyCheckers()
    pc.run_game()
