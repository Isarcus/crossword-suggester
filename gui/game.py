import pygame
from pathlib import Path

from gui.game_input import *
from gui.crossword import Crossword
from gui.vec import Vec

VEC_RIGHT = Vec(1, 0)
VEC_DOWN = Vec(0, 1)

class Game:
    def __init__(self, disp_size: tuple[int], screen: pygame.Surface):
        # Important numbers
        self.disp_size = Vec(disp_size[0], disp_size[1])
        self.cw_offset = Vec(min(self.disp_size)) // 18
        self.cw_size = Vec(min(self.disp_size)) * 8 // 9
        self.cw_max = self.cw_offset + self.cw_size
        self.selected = Vec(0, 0)
        self.direction = VEC_RIGHT

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

        if self.inp.get_state(LMB) == ButtonState.PRESSED:
            if self.selected is not None:
                self.cw.redraw_at(self.selected)
            tile_coord = self.get_tile_coord(self.inp.mpos)
            if (tile_coord >= Vec(0, 0) and tile_coord < self.cw.dimensions):
                self.selected = tile_coord
                self.draw_selected()
            else:
                self.selected = None
        else:
            for key, btn in self.inp.buttons.items():
                if btn.state == ButtonState.PRESSED:
                    # Letters should be typed into the crossword
                    if is_letter(key) and self.selected is not None:
                        self.cw.set_letter(KEY_TO_LETTER[key], self.selected)
                        next_selected = self.selected + self.direction
                        if self.cw.is_typable(next_selected):
                            print(self.selected)
                            print(next_selected)
                            self.cw.redraw_at(self.selected)
                            self.selected = next_selected
                        self.draw_selected()
                    # Backspace deletes the selected tile. If the selected
                    # tile is blank then deletes the preceding tile.
                    elif key == pygame.K_BACKSPACE and self.selected is not None:
                        if self.cw.is_blank(self.selected):
                            next_selected = self.selected - self.direction
                            if self.cw.is_typable(next_selected):
                                self.cw.del_letter(next_selected)
                                self.cw.redraw_at(self.selected)
                                self.selected = next_selected
                        else:
                            self.cw.del_letter(self.selected)
                        self.draw_selected()
                    # Tab changes typing direction
                    elif key == pygame.K_TAB:
                        if self.direction == VEC_DOWN:
                            self.direction = VEC_RIGHT
                        else:
                            self.direction = VEC_DOWN

    def draw_selected(self):
        if self.selected is not None:
            self.screen.blit(self.TILE_SELECTED, self.get_screen_coord(self.selected).tp())

    def get_tile_coord(self, screen_coord: Vec) -> Vec:
        return (screen_coord - self.cw_offset) // 32
    
    def get_screen_coord(self, tile_coord: Vec) -> Vec:
        return (tile_coord * 32) + self.cw_offset
