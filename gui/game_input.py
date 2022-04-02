import pygame
from enum import Enum

from gui.vec import Vec

LMB = 0xFF00
MMB = 0xFF01
RMB = 0xFF02

MB_SET = [
    LMB,
    MMB,
    RMB
]

LETTER_KEY_SET = set([
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
])

PUNCT_KEY_SET = set([
    pygame.K_SPACE,
    pygame.K_PERIOD,
    pygame.K_COMMA,
    pygame.K_LEFTBRACKET,
    pygame.K_RIGHTBRACKET,
    pygame.K_LEFTPAREN,
    pygame.K_RIGHTPAREN,
    pygame.K_SEMICOLON,
    pygame.K_COLON,
    pygame.K_QUOTE,
    pygame.K_QUOTEDBL
])

PUNCT_KEY_DICT = dict([
    (pygame.K_SPACE,  " "),
    (pygame.K_PERIOD, "."),
    (pygame.K_COMMA,  ","),
    (pygame.K_LEFTBRACKET, "["),
    (pygame.K_RIGHTBRACKET, "]"),
    (pygame.K_LEFTPAREN, "("),
    (pygame.K_RIGHTPAREN, ")"),
    (pygame.K_SEMICOLON, ";"),
    (pygame.K_COLON, ":"),
    (pygame.K_QUOTE, "'"),
    (pygame.K_QUOTEDBL, '"'),
])

SPECIAL_KEY_SET = set([
    pygame.K_TAB,
    pygame.K_RETURN,
    pygame.K_BACKSPACE,
    pygame.K_ESCAPE,
    pygame.K_LCTRL,
    pygame.K_RCTRL,
    pygame.K_LSHIFT,
    pygame.K_RSHIFT,
    pygame.K_CAPSLOCK,
])

ARROW_KEY_SET = set([
    pygame.K_DOWN,
    pygame.K_UP,
    pygame.K_LEFT,
    pygame.K_RIGHT,
])

ALL_KEYS_SET = LETTER_KEY_SET.union(PUNCT_KEY_SET, SPECIAL_KEY_SET, ARROW_KEY_SET)

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

def is_punct(key: int) -> bool:
    return key in PUNCT_KEY_SET

def is_special(key: int) -> bool:
    return key in SPECIAL_KEY_SET

def is_mouse(key: int) -> bool:
    return key in MB_SET

def get_key_char(key: int) -> str:
    if is_letter(key):
        return pygame.key.name(key)
    elif is_punct(key):
        return PUNCT_KEY_DICT[key]
    else:
        raise ValueError(f"Unrecognized key code: {key}")


class Button:
    def __init__(self):
        self.state = ButtonState.NOT_HELD

    def update(self, down: bool) -> int:
        self.state = next_state(self.state, down)
        return self.state

class RepeatableButton(Button):
    def __init__(self, initial_delay: int, repeat_delay: int):
        super().__init__()
        self.initial_delay = initial_delay
        self.repeat_delay = repeat_delay
        self.time_last_press = 0
        self.repeating = False

    def update(self, down: bool, time: int) -> int:
        if down:
            if is_down(self.state):
                self.repeat_if_time(time)
            else:
                self.state = ButtonState.PRESSED
                self.time_last_press = time
        else:
            if is_down(self.state):
                self.state = ButtonState.RELEASED
                self.repeating = False
            else:
                self.state = ButtonState.NOT_HELD

    def repeat_if_time(self, time: int):
        dt = time - self.time_last_press
        if self.repeating:
            if dt > self.repeat_delay:
                self.state = ButtonState.PRESSED
                self.time_last_press = time
            else:
                self.state = ButtonState.HELD
        elif dt > self.initial_delay:
            self.state = ButtonState.PRESSED
            self.time_last_press = time
            self.repeating = True
        else:
            self.state = ButtonState.HELD

class InputHandler:
    def __init__(self, repeatable_keys: set[int] = set(),
                 initial_delay: int = 400, repeat_delay: int = 80):
        all_buttons = ALL_KEYS_SET.union(MB_SET) - repeatable_keys

        self.mpos = Vec(0, 0)
        self.buttons = dict()
        for key in all_buttons:
            self.buttons[key] = Button()
        for key in repeatable_keys:
            self.buttons[key] = RepeatableButton(initial_delay, repeat_delay)

    def update(self):
        # Get input
        time = pygame.time.get_ticks()
        mpos = pygame.mouse.get_pos()
        mbs = pygame.mouse.get_pressed()
        keys = pygame.key.get_pressed()

        # Update state based on input
        self.mpos = Vec(mpos)
        for idx, mb in enumerate(MB_SET):
            self.buttons[mb].update(mbs[idx])
        for key in ALL_KEYS_SET:
            btn = self.buttons[key]
            if type(btn) == Button:
                btn.update(keys[key])
            elif type(btn) == RepeatableButton:
                btn.update(keys[key], time)

    def get_state(self, key: int) -> int:
        return self.buttons.get(key).state

    def is_down(self, key: int) -> bool:
        return is_down(self.get_state(key))
    
    def any_down(self, *keys: int) -> bool:
        for key in keys:
            if self.is_down(key):
                return True
        return False

    def all_down(self, *keys: int) -> bool:
        for key in keys:
            if not self.is_down(key):
                return False
        return True

    def is_caps(self) -> bool:
        return self.is_down(pygame.K_CAPSLOCK) != \
              (self.is_down(pygame.K_LSHIFT) or self.is_down(pygame.K_RSHIFT))

    def combo_pressed(self, *keys: int) -> bool:
        press = False
        for key in keys:
            state = self.get_state(key)
            if state == ButtonState.PRESSED:
                press = True
            elif state != ButtonState.HELD:
                return False
        return press
