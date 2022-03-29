import enum
import pygame

NOT_HELD = 0
PRESSED = 1
HELD = 2
RELEASED = 3

LMB = 0xFF00
MMB = 0xFF01
RMB = 0xFF02

MB_LIST = [
    LMB,
    MMB,
    RMB
]

KEY_LIST = [
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

def is_down(state: int):
    return state == HELD or state == PRESSED

def next_state(cur: int, down: bool) -> int:
    if (is_down(cur)):
        return HELD if down else RELEASED
    else:
        return PRESSED if down else NOT_HELD


class Button:
    def __init__(self, state: int = NOT_HELD):
        self.state = state

    def update(self, down: bool) -> int:
        self.state = next_state(self.state, down)
        return self.state

class InputHandler:
    def __init__(self):
        self.buttons = dict([(key, Button()) for key in KEY_LIST + MB_LIST])
        self.mpos = (0, 0)

    def update(self):
        # Get input
        mpos = pygame.mouse.get_pos()
        mbs = pygame.mouse.get_pressed()
        keys = pygame.key.get_pressed()

        # Update state based on input
        self.mpos = mpos
        for idx, mb in enumerate(MB_LIST):
            self.buttons[mb].update(mbs[idx])
        for key in KEY_LIST:
            self.buttons[key].update(keys[key])

    def get_state(self, key: int) -> int:
        return self.buttons.get(key, Button()).state
