import pygame
import numpy
from typing import Union
from pathlib import Path

from gui.vec import Vec

MAX_CROSSWORD_DIM = (20, 20)
TILE_BLANK = None
TILE_DARK = None
TILES_DICT = None
ALLOWED_LETTERS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
CHAR_BLANK = "*"
CHAR_DARK = "#"

class Crossword:
    def __init__(self, dimensions: Vec, font: pygame.font.Font,
                 surface: pygame.Surface, offset: Vec):
        """
        Parameters
        ----------
        dimensions: How many letters long and wide the crossword should be
        size: How much space, in pixels, the crossword should take up
        font: What font to use for rendering letters
        """
        self.dimensions = Vec(dimensions)
        self.surface = surface
        self.offset = offset
        self.letters = numpy.array(numpy.zeros(shape=(MAX_CROSSWORD_DIM), dtype=str), dtype=str)

        # Initialize globals for the first time
        global TILE_BLANK, TILE_DARK, TILES_DICT
        if TILE_BLANK is None:
            this_dir = Path(__file__).parent
            images_dir = this_dir.joinpath("images")
            TILE_BLANK = pygame.image.load(images_dir.joinpath("tile_blank.png"))
            TILE_DARK = pygame.image.load(images_dir.joinpath("tile_dark.png"))
            TILES_DICT = dict([(l, font.render(l, True, (0, 0, 0))) for l in ALLOWED_LETTERS])

        # Draw image!
        self.redraw()

    def set_letter(self, letter: str, at: Vec):
        self.letters[at.tp()] = letter
        self.redraw_at(at)
    
    def del_letter(self, at: Vec):
        self.letters[at.tp()] = str()
        self.redraw_at(at)

    def set_dark(self, at: Vec):
        self.letters[at.tp()] = CHAR_DARK
        self.redraw_at(at)

    def redraw_at(self, at: Vec):
        letter = self.letters[at.tp()]
        coord = (self.offset + at * 32).tp()

        if len(letter) == 0:
            self.surface.blit(TILE_BLANK, coord)
        elif letter[0] == CHAR_DARK:
            self.surface.blit(TILE_DARK, coord)
        else:
            self.surface.blit(TILE_BLANK, coord)
            tile = TILES_DICT[letter]
            rect = tile.get_rect()
            cx += 16 - rect.centerx
            cy += 17 - rect.centery # 17 looks better for Y
            self.surface.blit(tile, coord)
    
    def redraw(self):
        self.surface.fill((0, 0, 0))
        for x in range(self.dimensions.X):
            for y in range(self.dimensions.Y):
                self.redraw_at(Vec(x, y))
    
    def save(self, path: str, overwrite: bool) -> bool:
        """
        Saves progress in a text file at the designated path, and returns True
        if successful.
        Will only return False when `overwrite` False and `path` references an
        existing file.
        """
        if overwrite:
            options = "w"
        else:
            options = "x"

        # Open file for writing
        try:
            f = open(path, options)
        except FileExistsError:
            return False

        f.write(f"{self.dimensions.X} {self.dimensions.Y}\n")
        for y in range(self.dimensions.Y):
            for x in range(self.dimensions.X):
                letter = (self.letters[x, y])
                if len(letter) == 0:
                    f.write(CHAR_BLANK)
                else:
                    f.write(letter[0])
            f.write('\n')
        
        return True

    def load(self, path: str, blank=CHAR_BLANK, dark = CHAR_DARK) -> tuple[bool, str]:
        """
        Attempts to load a crossword from the specified path.
        If any errors are encountered while attempting to load and parse the
        specified file, returns (False, `reason`), where `reason` is a string
        explaining what went wrong. Returns (True, None) if everything was ok.
        """
        # Attempt to open file and read contents
        try:
            f = open(path, "r")
        except FileNotFoundError:
            return False, "File not found"
        lines = f.readlines()

        # Parse file header
        try:
            dims = lines[0].split()
            dim_x = int(dims[0])
            dim_y = int(dims[1])
        except Union[ValueError, IndexError]:
            return False, "Could not parse file header"

        # Clear current data
        self.dimensions = Vec(dim_x, dim_y)
        self.letters.fill(str())

        for idx_line, line in enumerate(lines[1:]):
            if (idx_line >= dim_y):
                break
            for idx_let, letter in enumerate(line):
                if (idx_let >= dim_x):
                    break

                if letter == CHAR_BLANK:
                    self.letters[idx_let, idx_line] = str()
                elif letter in ALLOWED_LETTERS or letter == CHAR_DARK:
                    self.letters[idx_let, idx_line] = letter
                else:
                    return False, f"Unrecognized character: {letter}"
        
        # Redraw with the new data
        self.redraw()

        return True, None
