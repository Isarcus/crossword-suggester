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

SPECIAL_KEY_LIST = [
    pygame.K_SPACE,
    pygame.K_TAB,
    pygame.K_RETURN,
    pygame.K_BACKSPACE,
    pygame.K_LCTRL,
    pygame.K_RCTRL,
    pygame.K_LSHIFT,
    pygame.K_RSHIFT,
    pygame.K_CAPSLOCK,
    pygame.K_DOWN,
    pygame.K_UP,
    pygame.K_LEFT,
    pygame.K_RIGHT,
]

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

def is_letter(key: int) -> bool:
    return key >= pygame.K_a and key <= pygame.K_z

def is_special(key: int) -> bool:
    return key in SPECIAL_KEY_LIST

def is_mouse(key: int) -> bool:
    return key in MB_LIST

class Button:
    def __init__(self, state: int = ButtonState.NOT_HELD):
        self.state = state

    def update(self, down: bool) -> int:
        self.state = next_state(self.state, down)
        return self.state

class InputHandler:
    def __init__(self):
        all_buttons = LETTER_KEY_LIST + SPECIAL_KEY_LIST + MB_LIST
        self.buttons = dict([(key, Button()) for key in all_buttons])
        self.mpos = Vec(0, 0)

    def update(self):
        # Get input
        mpos = pygame.mouse.get_pos()
        mbs = pygame.mouse.get_pressed()
        keys = pygame.key.get_pressed()

        # Update state based on input
        self.mpos = Vec(mpos)
        for idx, mb in enumerate(MB_LIST):
            self.buttons[mb].update(mbs[idx])
        for key in LETTER_KEY_LIST:
            self.buttons[key].update(keys[key])
        for key in SPECIAL_KEY_LIST:
            self.buttons[key].update(keys[key])

    def get_state(self, key: int) -> int:
        return self.buttons.get(key, Button()).state

    def is_down(self, key: int) -> bool:
        return is_down(self.get_state(key))

    def is_caps(self) -> bool:
        return self.is_down(pygame.K_CAPSLOCK) != \
              (self.is_down(pygame.K_LSHIFT) or self.is_down(pygame.K_RSHIFT))

    def combo_pressed(self, *keys: int) -> bool:
        press = False
        down = True
        for key in keys:
            state = self.get_state(key)
            if state == ButtonState.PRESSED:
                press = True
            elif state != ButtonState.HELD:
                down = False
                break
        return press and down
