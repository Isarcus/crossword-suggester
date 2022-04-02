import pygame
import numpy
from pathlib import Path
from typing import Union

from gui.vec import *

MAX_CROSSWORD_DIM = (20, 20)
TILE_BLANK = None
TILE_DARK = None
TILE_SELECTED = None
TILE_HIGHLIGHTED = None
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
        font: What font to use for rendering letters
        surface: The Surface object to render to
        offset: The distance, in pixels, to offset all rendering by
        """
        self.dimensions = Vec(dimensions)
        self.surface = surface
        self.offset = offset
        self.letters = numpy.array(numpy.zeros(shape=(MAX_CROSSWORD_DIM), dtype=str), dtype=str)
        self.highlighted = numpy.array(numpy.zeros(shape=MAX_CROSSWORD_DIM), dtype=bool)
        self.letters.fill(CHAR_BLANK)
        self.selected = None
        self.select_dir = VEC_RIGHT

        # Initialize globals for the first time
        global TILE_BLANK, TILE_DARK, TILE_SELECTED, TILE_HIGHLIGHTED, TILES_DICT
        if TILE_BLANK is None:
            this_dir = Path(__file__).parent
            images_dir = this_dir.joinpath("images")
            TILE_BLANK = pygame.image.load(images_dir.joinpath("tile_blank.png"))
            TILE_DARK = pygame.image.load(images_dir.joinpath("tile_dark.png"))
            TILE_SELECTED = pygame.image.load(images_dir.joinpath("tile_selected.png"))
            TILE_SELECTED.set_colorkey((255, 255, 255))
            TILE_HIGHLIGHTED = pygame.image.load(images_dir.joinpath("tile_highlighted.png"))
            TILES_DICT = dict([(l, font.render(l, True, (0, 0, 0))) for l in ALLOWED_LETTERS])

        # Draw image!
        self.redraw()
        self.select(Vec(0, 0), VEC_RIGHT)

    def is_valid(self, at: Vec) -> bool:
        """Returns whether `at` is a valid point on the crossword grid."""
        return at is not None and at >= Vec(0, 0) and at < self.dimensions

    def is_blank(self, at: Vec) -> bool:
        return self.is_valid(at) and self.letters[at.tp()] == CHAR_BLANK

    def is_dark(self, at: Vec) -> bool:
        return self.is_valid(at) and self.letters[at.tp()] == CHAR_DARK

    def is_letter(self, at: Vec) -> bool:
        return self.is_valid(at) and self.letters[at.tp()] in ALLOWED_LETTERS

    def is_typable(self, at: Vec) -> bool:
        if self.is_valid(at):
            let = self.letters[at.tp()]
            return let in ALLOWED_LETTERS or let == CHAR_BLANK
        else:
            return False

    def is_highlighted(self, at: Vec) -> bool:
        return self.is_valid(at) and self.highlighted[at.tp()]

    def is_obstructed(self, pos: Vec, direction: Vec, dist: int) -> bool:
        for _ in range(dist):
            if self.is_dark(pos):
                return True
            pos += direction
        return self.is_dark(pos)

    def is_obstructed_between(self, pos1: Vec, pos2: Vec) -> bool:
        """
        Returns whether any dark tiles lie between pos1 and pos2, inclusive.
        If pos1 and pos2 are not in the same row or column, returns True.
        If either pos1 or pos2 do not refer to valid positions, returns True.
        """
        if not self.is_valid(pos1) or not self.is_valid(pos2):
            return True

        match_x = pos1.X == pos2.X
        match_y = pos1.Y == pos2.Y
        if match_x:
            if match_y: return False
            dy = pos2.Y - pos1.Y
            direction = Vec(0, dy // abs(dy))
            return self.is_obstructed(pos1, direction, abs(dy))
        elif match_y:
            dx = pos2.X - pos1.X
            direction = Vec(dx // abs(dx), 0)
            return self.is_obstructed(pos1, direction, abs(dx))
        else:
            return True

    def dist_obstruction(self, pos: Vec, direction: Vec) -> int:
        """
        Returns the distance from the source tile to the first obstruction
        encountered while scanning in the direction indicated by `direction`.
        Obstructions are either dark tiles or the edge of the map. 
        """
        dist = 0
        while not self.is_dark(pos):
            if self.is_valid(pos):
                pos += direction
                dist += 1
            else:
                break
        return dist

    def get_letter(self, at: Vec) -> str:
        if self.is_valid(at):
            return self.letters[at.tp()]
        else:
            return None
    
    def get_highlighted_word(self) -> Union[str, None]:
        """
        Return the word currently highlighted in the crossword. If nothing is
        currently selected, returns None.
        """
        if self.selected is None:
            return None
        
        dist_back = self.dist_obstruction(self.selected, self.select_dir * -1) - 1
        length = dist_back + self.dist_obstruction(self.selected, self.select_dir)
        pos = self.selected + self.select_dir * -dist_back
        
        return ''.join([self.letters[v.tp()] for v in VecRange(pos, self.select_dir, length)])

    def set_letter(self, letter: str, at: Vec):
        if self.is_valid(at):
            self.letters[at.tp()] = letter.upper()
            self.redraw_at(at)

    def set_blank(self, at: Vec):
        if self.is_dark(at):
            self.letters[at.tp()] = CHAR_BLANK

            if self.is_obstructed_between(at, self.selected):
                self.redraw_at(at)
            else:
                direction = at - self.selected
                direction //= max(abs(direction))

                if abs(direction) == abs(self.select_dir):
                    dist = self.dist_obstruction(at, direction)
                    pos = at
                    for _ in range(dist):
                        self.highlighted[pos.tp()] = True
                        self.redraw_at(pos)
                        pos += direction

    def del_letter(self, at: Vec):
        if self.is_letter(at):
            self.letters[at.tp()] = CHAR_BLANK
            self.redraw_at(at)

    def set_dark(self, at: Vec):
        if self.is_valid(at):
            if self.selected == at:
                self.select(None)
            elif self.is_highlighted(at):
                direction = at - self.selected
                direction //= max(abs(direction))
                dist = self.dist_obstruction(at, direction)
                pos = at
                for _ in range(dist):
                    self.highlighted[pos.tp()] = False
                    self.redraw_at(pos)
                    pos += direction
            self.letters[at.tp()] = CHAR_DARK
            self.redraw_at(at)

    def select(self, at: Vec, direction: Union[Vec, None] = None):
        if direction is None:
            direction = self.select_dir
        if not self.is_typable(at):
            at = None

        prev_selected = self.selected
        
        rehighlight = self.selected is None or at is None or \
                      direction != self.select_dir or \
                      not self.is_highlighted(at)
        if rehighlight:
            # Erase highlights from previously selected tile
            if self.selected is not None:
                self.selected = None
                # Erase highlights in positive direction
                pos = prev_selected
                while self.is_highlighted(pos):
                    self.highlighted[pos.tp()] = False
                    self.redraw_at(pos)
                    pos += self.select_dir
                # Erase highlights in negative direction
                pos = prev_selected - self.select_dir
                while self.is_highlighted(pos):
                    self.highlighted[pos.tp()] = False
                    self.redraw_at(pos)
                    pos -= self.select_dir

            # Update selected before highlighting
            self.selected = at
            self.select_dir = direction

            if at is not None:
                # Highlight in positive direction
                pos = at
                while self.is_typable(pos):
                    self.highlighted[pos.tp()] = True
                    self.redraw_at(pos)
                    pos += direction
                # Highlight in negative direction
                pos = at - direction
                while self.is_typable(pos):
                    self.highlighted[pos.tp()] = True
                    self.redraw_at(pos)
                    pos -= direction
        else:
            self.selected = None
            self.redraw_at(prev_selected)
            self.selected = at
            self.select_dir = direction
            self.redraw_at(at)
    
    def select_next_typable(self, direction: Union[Vec, None] = None):
        if self.selected is None:
            return

        if direction is None:
            direction = self.select_dir

        new_selected = self.selected
        last_typable = new_selected if self.is_typable(new_selected) else None
        while True:
            new_selected += direction
            if self.is_typable(new_selected):
                last_typable = new_selected
                break
            elif not self.is_valid(new_selected):
                break
        if last_typable is not None:
            self.select(last_typable)

    def toggle_select_dir(self):
        if self.select_dir == VEC_RIGHT:
            self.select(self.selected, VEC_DOWN)
        else:
            self.select(self.selected, VEC_RIGHT)

    def recv_backspace(self):
        if self.is_blank(self.selected):
            self.select_next_typable(self.select_dir * -1)
        
        self.del_letter(self.selected)

    def recv_letter(self, letter: str):
        selected = self.selected
        self.select_next_typable()
        self.set_letter(letter, selected)

    def redraw_at(self, at: Vec):
        if not self.is_valid(at):
            return

        letter = self.letters[at.tp()]
        coord = self.offset + at * 32

        tile_back = TILE_HIGHLIGHTED if self.is_highlighted(at) else TILE_BLANK

        if letter[0] == CHAR_DARK:
            self.surface.blit(TILE_DARK, coord.tp())
        else:
            self.surface.blit(tile_back, coord.tp())
            if not letter[0] == CHAR_BLANK:
                tile_letter = TILES_DICT[letter]
                rect = tile_letter.get_rect()
                coord_letter = coord + Vec(16 - rect.centerx, 17 - rect.centery)
                self.surface.blit(tile_letter, coord_letter.tp())
            
            if self.selected == at:
                if self.select_dir == VEC_RIGHT:
                    self.surface.blit(TILE_SELECTED, coord.tp())
                elif self.select_dir == VEC_DOWN:
                    tile_selected = pygame.transform.rotate(TILE_SELECTED, -90)
                    tile_selected.set_colorkey((255, 255, 255))
                    self.surface.blit(tile_selected, coord.tp())

    def redraw(self):
        self.surface.fill((0, 0, 0))
        for x in range(self.dimensions.X):
            for y in range(self.dimensions.Y):
                self.redraw_at(Vec(x, y))

    def save(self, path: str, overwrite: bool) -> tuple[bool, str]:
        """
        Saves progress in a text file at the designated path, and returns True
        if successful.
        Will return False when `overwrite` is False and `path` references an
        existing file, or the specified filepath was invalid for the OS.
        """
        if overwrite:
            options = "w"
        else:
            options = "x"

        # Open file for writing
        try:
            f = open(path, options)
        except Exception as e:
            return False, str(e)

        f.write(f"{self.dimensions.X} {self.dimensions.Y}\n")
        for y in range(self.dimensions.Y):
            for x in range(self.dimensions.X):
                letter = (self.letters[x, y])
                if len(letter) == 0:
                    f.write(CHAR_BLANK)
                else:
                    f.write(letter[0])
            f.write('\n')
        
        return True, None

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
        except (ValueError, IndexError):
            return False, "Could not parse file header"

        # Clear current data
        self.dimensions = Vec(dim_x, dim_y)
        self.letters.fill(CHAR_BLANK)
        self.highlighted.fill(False)
        self.selected = None
        self.select_dir = VEC_RIGHT

        for idx_line, line in enumerate(lines[1:]):
            if (idx_line >= dim_y):
                break
            for idx_let, letter in enumerate(line.upper()):
                if (idx_let >= dim_x):
                    break

                if letter == CHAR_BLANK:
                    self.letters[idx_let, idx_line] = CHAR_BLANK
                elif letter in ALLOWED_LETTERS or letter == CHAR_DARK:
                    self.letters[idx_let, idx_line] = letter
                else:
                    return False, f"Unrecognized character: {letter}"
        
        # Redraw with the new data
        self.redraw()

        return True, None
