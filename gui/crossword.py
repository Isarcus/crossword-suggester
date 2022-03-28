import pygame
import numpy
from pathlib import Path

MAX_CROSSWORD_DIM = (30, 30)
TILE_WHITE = None
TILE_BLACK = None
TILES_DICT = None
ALLOWED_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

class Crossword:
    
    def __init__(self, dimensions: tuple[int], size: tuple[int], font: pygame.font.Font):
        """
        Parameters
        ----------
        dimensions: How many letters long and wide the crossword should be
        size: How much space, in pixels, the crossword should take up
        font: What font to use for rendering letters
        """
        self.dimensions = dimensions
        self.size = size
        self.image = pygame.Surface(size)
        self.letters = numpy.array(numpy.zeros(shape=(MAX_CROSSWORD_DIM)), dtype=str)

        # Initialize globals for the first time
        global TILE_WHITE, TILE_BLACK, TILES_DICT
        if TILE_WHITE is None:
            this_dir = Path(__file__).parent
            images_dir = this_dir.joinpath("images")
            TILE_WHITE = pygame.image.load(images_dir.joinpath("tile_white.png"))
            TILE_BLACK = pygame.image.load(images_dir.joinpath("tile_black.png"))
            TILES_DICT = dict([(l, font.render(l, True, (0, 0, 0))) for l in ALLOWED_LETTERS])

        # Create tiled background
        for x in range(dimensions[0]):
            for y in range(dimensions[1]):
                self.image.blit(TILE_WHITE, (x*32, y*32))

    def set_letter(self, letter: str, at: tuple[int]):
        self.letters[at] = letter
        self.update_at(at)
    
    def del_letter(self, at: tuple[int]):
        self.letters[at] = str()
        self.update_at(at)

    def update_at(self, at: tuple[int]):
        letter = self.letters[at]
        cx = at[0] * 32
        cy = at[1] * 32

        if len(letter) == 0:
            self.image.blit(TILE_WHITE, (cx, cy))
        elif letter[0] == '-':
            self.image.blit(TILE_BLACK, (cx, cy))
        else:
            tile = TILES_DICT[letter]
            rect = tile.get_rect()
            cx += 16 - rect.centerx
            cy += 17 - rect.centery # 17 looks better for Y
            self.image.blit(tile, (cx, cy))
