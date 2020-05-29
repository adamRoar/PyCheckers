import multiprocessing
import sys
import time
import logging
from concurrent.futures.process import ProcessPoolExecutor

import pygame
from pygame.event import Event
from pygame.surface import Surface

from ai.ai import Ai
from gui.settings import Settings
from model.model import Board, Color, Tile, MoveType


class PyCheckers:
    def __init__(self):
        if not pygame.get_init():
            pygame.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((self.settings.screen_width,
                                               self.settings.screen_height))  # type: Surface
        pygame.display.set_caption("PyCheckers")
        self.board = Board()
        self.selected_tile = None
        self.executor = ProcessPoolExecutor()
        self.red_ai = Ai(self.board, Color.RED, 6)
        self.black_ai = Ai(self.board, Color.BLACK, 6)
        self.first = True
        self.num_AIs = 0

    def run_game(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.executor.shutdown()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.num_AIs != 2:
                        self.handle_click()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_0:
                        self.num_AIs = 2
                    elif event.key == pygame.K_1:
                        self.num_AIs = 1
                    elif event.key == pygame.K_2:
                        self.num_AIs = 0
            if self.num_AIs == 2:
                self.black_ai.next_move(self.executor)
                self.draw_board()
                pygame.display.flip()
                self.red_ai.next_move(self.executor)
            self.draw_board()
            pygame.display.flip()

    def draw_board(self):
        if self.board.winner() is None:
            self.draw_tiles()
            self.draw_pieces()
            self.draw_text()
        else:
            self.draw_win_screen()

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

    def draw_text(self):
        font = pygame.font.SysFont(None, 20, bold=True, italic=False)
        small_font = pygame.font.SysFont(None, 14, bold=True, italic=False)
        color = self.settings.text_color
        player_text = font.render("{num_players} player".format(num_players=(2 - self.num_AIs)), True, color)
        instruction_text = small_font.render("0, 1, or 2 to change", True, color)
        turn_text = small_font.render("{turn}'s turn".format(turn=self.board.turn.name), True, color)
        counter_text = small_font.render("{turn_count} moves".format(turn_count=self.board.turn_counter), True, color)
        self.screen.blit(player_text, (5, 10))
        self.screen.blit(instruction_text, (5, 30))
        self.screen.blit(turn_text, (5, 44))
        self.screen.blit(counter_text, (5, 58))

    def draw_win_screen(self):
        if self.first:
            print(self.board)
            self.first = False
        font = pygame.font.SysFont(None, 72, bold=True, italic=False)
        color = self.settings.red_piece_color if self.board.winner() == Color.RED else self.settings.black_piece_color
        text = font.render("{winner} wins!".format(winner=self.board.winner().name), True, color)
        self.screen.fill(self.settings.white_tile_color)
        self.screen.blit(text, (400 - text.get_width() // 2, 400 - text.get_height() // 2))
        # self.executor.shutdown()

    def handle_click(self):
        (x, y) = pygame.mouse.get_pos()
        row = int((y - y % 100) / 100)
        column = int((x - x % 100) / 100)
        clicked_tile = Tile(row, column)
        piece = self.board.get_piece_at(clicked_tile)

        if self.selected_tile is None:
            if piece is None:
                return
            elif piece.color != self.board.turn:
                return
            elif self.board.must_jump and not self.board.can_jump(clicked_tile):
                return
            self.selected_tile = clicked_tile
        else:
            move_type = self.board.move_piece(self.selected_tile, clicked_tile)
            if move_type == MoveType.JUMP and self.board.can_jump(clicked_tile):
                self.selected_tile = clicked_tile
            else:
                self.selected_tile = None
        if self.board.turn == Color.RED and self.num_AIs == 1:
            self.draw_board()
            pygame.display.flip()
            self.red_ai.next_move(self.executor)


if __name__ == '__main__':
    pc = PyCheckers()
    pc.run_game()
