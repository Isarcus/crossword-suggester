import pygame
from enum import Enum

from gui.vec import Vec

LMB = 0xFF00
MMB = 0xFF01
RMB = 0xFF02

MB_LIST = [
    LMB,
    MMB,
    RMB
]

LETTER_KEY_LIST = [
    pygame.K_a,
    pygame.K_b,
    pygame.K_c,
    pygame.K_d,
    pygame.K_e,
    pygame.K_f,
    pygame.K_g,
    pygame.K_h,
    pygame.K_i,
    pygame.K_j,
    pygame.K_k,
    pygame.K_l,
    pygame.K_m,
    pygame.K_n,
    pygame.K_o,
    pygame.K_p,
    pygame.K_q,
    pygame.K_r,
    pygame.K_s,
    pygame.K_t,
    pygame.K_u,
    pygame.K_v,
    pygame.K_w,
    pygame.K_x,
    pygame.K_y,
    pygame.K_z,
]

KEY_TO_LETTER = dict([(k, l) for k, l in zip(LETTER_KEY_LIST, "ABCDEFGHIJKLMNOPQRSTUVWXYZ")])
LETTER_TO_KEY = dict([(l, k) for k, l in zip(LETTER_KEY_LIST, "ABCDEFGHIJKLMNOPQRSTUVWXYZ")])

class ButtonState(Enum):
    NOT_HELD = 0
    PRESSED = 1
    HELD = 2
    RELEASED = 3

def is_down(state: int):
    return state == ButtonState.HELD or state == ButtonState.PRESSED

def next_state(cur: int, down: bool) -> int:
    if (is_down(cur)):
        return ButtonState.HELD if down else ButtonState.RELEASED
    else:
        return ButtonState.PRESSED if down else ButtonState.NOT_HELD


class Button:
    def __init__(self, state: int = ButtonState.NOT_HELD):
        self.state = state

    def update(self, down: bool) -> int:
        self.state = next_state(self.state, down)
        return self.state

class InputHandler:
    def __init__(self):
        self.letter_keys = dict([(key, Button()) for key in LETTER_KEY_LIST + MB_LIST])
        self.mpos = Vec()

    def update(self):
        # Get input
        mpos = pygame.mouse.get_pos()
        mbs = pygame.mouse.get_pressed()
        keys = pygame.key.get_pressed()

        # Update state based on input
        self.mpos = Vec(mpos)
        for idx, mb in enumerate(MB_LIST):
            self.letter_keys[mb].update(mbs[idx])
        for key in LETTER_KEY_LIST:
            self.letter_keys[key].update(keys[key])

    def get_state(self, key: int) -> int:
        return self.letter_keys.get(key, Button()).state
