import pygame
from pathlib import Path

from gui.crossword import Crossword
from gui.game_input import InputHandler, ButtonState, LMB, MMB, RMB, LETTER_TO_KEY, KEY_TO_LETTER
from gui.vec import Vec

class Game:
    def __init__(self, disp_size: tuple[int], screen: pygame.Surface):
        # Important numbers
        self.disp_size = Vec(disp_size[0], disp_size[1])
        self.cw_offset = Vec(min(self.disp_size)) // 18
        self.cw_size = Vec(min(self.disp_size)) * 8 // 9
        self.cw_max = self.cw_offset + self.cw_size
        self.selected = Vec()

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
                self.screen.blit(self.TILE_SELECTED,
                                 self.get_screen_coord(tile_coord).tp())
            else:
                self.selected = None
        else:
            for key, btn in self.inp.letter_keys.items():
                if btn.state == ButtonState.PRESSED:
                    self.cw.set_letter(KEY_TO_LETTER[key], self.selected)
                    break

    def get_tile_coord(self, screen_coord: Vec) -> Vec:
        return (screen_coord - self.cw_offset) // 32
    
    def get_screen_coord(self, tile_coord: Vec) -> Vec:
        return (tile_coord * 32) + self.cw_offset
