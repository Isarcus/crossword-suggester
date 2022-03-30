import pygame
from pathlib import Path
from enum import Enum

from gui.game_input import *
from gui.crossword import Crossword
from gui.vec import Vec

VEC_DOWN = Vec(0, 1)
VEC_UP = Vec(0, -1)
VEC_LEFT = Vec(-1, 0)
VEC_RIGHT = Vec(1, 0)

class InputMode(Enum):
    CROSSWORD = 0
    TEXT_ENTRY = 1

class Game:
    def __init__(self, disp_size: tuple[int], screen: pygame.Surface):
        # Important numbers
        self.disp_size = Vec(disp_size[0], disp_size[1])
        self.cw_offset = Vec(min(self.disp_size)) // 18
        self.cw_size = Vec(min(self.disp_size)) * 8 // 9
        self.cw_max = self.cw_offset + self.cw_size
        self.selected = Vec(0, 0)
        self.direction = VEC_RIGHT
        self.input_mode = InputMode.CROSSWORD

        # Paths
        this_dir = Path(__file__).parent
        images_dir = this_dir.joinpath("images")

        # Objects
        self.TILE_SELECTED = pygame.image.load(images_dir.joinpath("tile_selected.png"))
        self.TILE_SELECTED.set_colorkey((255, 255, 255))
        self.font = pygame.font.SysFont(None, 40)
        self.screen = screen
        self.cw = Crossword((20, 20), self.font, screen, self.cw_offset)
        self.inp = InputHandler()
    
    def tick(self):
        if not pygame.key.get_focused():
            return

        # Get fresh input
        self.inp.update()

        if self.input_mode == InputMode.CROSSWORD:
            self.handle_mode_crossword()
        elif self.input_mode == InputMode.TEXT_ENTRY:
            self.handle_mode_text_entry()

    # ------------------------ #
    # Input handling functions #
    # ------------------------ #

    def handle_mode_crossword(self):
        # CTRL+S initiates save script
        if self.inp.combo_pressed(pygame.K_LCTRL, pygame.K_s):
            self.begin_save()
        # LMB Selects a tile
        elif self.inp.get_state(LMB) == ButtonState.PRESSED:
            if self.selected is not None:
                self.cw.redraw_at(self.selected)
            tile_coord = self.get_tile_coord(self.inp.mpos)
            if (tile_coord >= Vec(0, 0) and tile_coord < self.cw.dimensions):
                self.selected = tile_coord
                self.draw_selected()
            else:
                self.selected = None
        # RMB Toggles darks and blanks
        elif self.inp.get_state(RMB) == ButtonState.PRESSED:
            tile_coord = self.get_tile_coord(self.inp.mpos)
            if self.cw.is_blank(tile_coord):
                self.cw.set_dark(tile_coord)
            elif self.cw.is_dark(tile_coord):
                self.cw.set_blank(tile_coord)
        else:
            for key, btn in self.inp.buttons.items():
                if btn.state == ButtonState.PRESSED:
                    # Letters should be typed into the crossword
                    if is_letter(key) and self.selected is not None:
                        self.cw.set_letter(pygame.key.name(key), self.selected)
                        self.select_next_typable(self.direction)
                    # Backspace deletes the selected tile. If the selected
                    # tile is blank then deletes the preceding tile.
                    elif key == pygame.K_BACKSPACE and self.selected is not None:
                        if self.cw.is_blank(self.selected):
                            self.select_next_typable(self.direction * -1)
                            if self.cw.is_letter(self.selected):
                                self.cw.del_letter(self.selected)
                                self.draw_selected()
                        else:
                            self.cw.del_letter(self.selected)
                        self.draw_selected()
                    # Tab changes typing direction
                    elif key == pygame.K_TAB:
                        if self.direction == VEC_DOWN:
                            self.direction = VEC_RIGHT
                        else:
                            self.direction = VEC_DOWN
                        self.draw_selected()
                    # Arrow keys select the next typable tile in a given direction
                    elif key == pygame.K_DOWN:
                        self.select_next_typable(VEC_DOWN)
                    elif key == pygame.K_UP:
                        self.select_next_typable(VEC_UP)
                    elif key == pygame.K_LEFT:
                        self.select_next_typable(VEC_LEFT)
                    elif key == pygame.K_RIGHT:
                        self.select_next_typable(VEC_RIGHT)
    
    def handle_mode_text_entry(self):
        self.input_mode = InputMode.CROSSWORD

    def begin_save(self):
        self.input_mode = InputMode.TEXT_ENTRY

    # ----------------- #
    # Utility functions #
    # ----------------- #

    def draw_selected(self):
        if self.selected is not None:
            self.cw.redraw_at(self.selected)
            if self.direction == VEC_RIGHT:
                tile = self.TILE_SELECTED
            else:
                tile = pygame.transform.rotate(self.TILE_SELECTED, -90)
                tile.set_colorkey((255, 255, 255))
            self.screen.blit(tile, self.get_screen_coord(self.selected).tp())

    def get_tile_coord(self, screen_coord: Vec) -> Vec:
        return (screen_coord - self.cw_offset) // 32
    
    def get_screen_coord(self, tile_coord: Vec) -> Vec:
        return (tile_coord * 32) + self.cw_offset
    
    def select_next_typable(self, direction: Vec):
        new_selected = self.selected
        last_typable = new_selected if self.cw.is_typable(new_selected) else None
        while True:
            new_selected += direction
            if self.cw.is_typable(new_selected):
                last_typable = new_selected
                break
            elif not self.cw.is_valid(new_selected):
                break
        if last_typable is not None:
            self.cw.redraw_at(self.selected)
            self.selected = last_typable
            self.draw_selected()

