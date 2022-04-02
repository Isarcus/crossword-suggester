import pygame
from pathlib import Path
from typing import Union

from gui.vec import Vec

class Clickable:
    def __init__(self, corner_1: Vec, corner_2: Vec, exec_func):
        self.min, self.max = Vec.minmax(corner_1, corner_2)
        self.exec_func = exec_func

    def click(self):
        self.exec_func()

    def click_if_in_range(self, pos: Vec):
        if self.in_range(pos):
            self.click()

    def in_range(self, pos: Vec) -> bool:
        return pos >= self.min and pos <= self.max

    def set_exec_func(self, exec_func):
        self.exec_func = exec_func

class ClickIcon(Clickable):
    def __init__(self, corner_1: Vec, corner_2: Vec, exec_func,
                 surface: pygame.Surface, icon: Union[Path, pygame.Surface]):
        super().__init__(corner_1, corner_2, exec_func)
        self.surface = surface

        if type(icon) == pygame.Surface:
            self.icon = icon
        else:
            self.icon = pygame.image.load(icon)

        self.draw()
        
    def draw(self):
        self.surface.blit(self.icon, self.min.tp())
