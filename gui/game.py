import pygame
from pathlib import Path
from enum import Enum

from gui import suggester
from gui.game_input import *
from gui.vec import *
from gui.text_box import TextBox
from gui.crossword import Crossword
from gui.clickable import ClickIcon

REPEATABLE_KEYS = ARROW_KEY_SET.union({pygame.K_BACKSPACE})
SUG_BTN_MIN = Vec(720, 80)
BTN_SIZE = Vec(64, 64)
CW_MIN = Vec(40, 40)
CW_SIZE = Vec(640, 640)
CW_MAX = CW_MIN + CW_SIZE

class InputMode(Enum):
    CROSSWORD = 0
    TEXT_ENTRY = 1

class Game:
    def __init__(self, disp_size: tuple[int], screen: pygame.Surface):
        # Important numbers
        self.disp_size = Vec(disp_size[0], disp_size[1])
        self.input_mode = InputMode.CROSSWORD

        # Paths
        this_dir = Path(__file__).parent
        images_dir = this_dir.joinpath("images")

        # Objects
        self.font = pygame.font.SysFont(None, 40)
        self.screen = screen
        self.cw = Crossword((20, 20), self.font, screen, CW_MIN)
        self.inp = InputHandler(REPEATABLE_KEYS)
        self.text = TextBox(pygame.font.SysFont(None, 32), (255,)*3, 400, 2)
        sug_button = ClickIcon(SUG_BTN_MIN, SUG_BTN_MIN + BTN_SIZE, self.request_suggestion,
                               screen, images_dir.joinpath("button_suggest.png"))
        self.buttons = [sug_button]
        
        # State and side functions
        self.exec_func = None
        self.awaiting_suggestion = False

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
        # Check if currently awaiting any output from the word suggester
        if self.awaiting_suggestion:
            suggestions = suggester.get_result()
            if suggestions is not None:
                print(suggestions)
                self.awaiting_suggestion = False

        # Check key combos
        if self.inp.any_down(pygame.K_LCTRL, pygame.K_RCTRL):
            # CTRL+S initiates save script
            if self.inp.get_state(pygame.K_s) == ButtonState.PRESSED:
                self.begin_mode_text_entry(self.attempt_save)
            # CTRL+L initiates load script
            elif self.inp.get_state(pygame.K_l) == ButtonState.PRESSED:
                self.begin_mode_text_entry(self.attempt_load)
        # LMB Selects a tile or clicks a button
        elif self.inp.get_state(LMB) == ButtonState.PRESSED:
            if self.inp.mpos.in_rect(CW_MIN, CW_MAX):
                tile_coord = self.get_tile_coord(self.inp.mpos)
                self.cw.select(tile_coord)
            else:
                for btn in self.buttons:
                    btn.click_if_in_range(self.inp.mpos)
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
                    if is_letter(key):
                        self.cw.recv_letter(pygame.key.name(key))
                    # Backspace deletes the selected tile. If the selected
                    # tile is blank then deletes the preceding tile.
                    elif key == pygame.K_SPACE:
                        self.cw.select_next_typable()
                    elif key == pygame.K_BACKSPACE:
                        self.cw.recv_backspace()
                    # Tab changes typing direction
                    elif key == pygame.K_TAB:
                        self.cw.toggle_select_dir()
                    # Arrow keys select the next typable tile in a given direction
                    elif key == pygame.K_DOWN:
                        self.cw.select_next_typable(VEC_DOWN)
                    elif key == pygame.K_UP:
                        self.cw.select_next_typable(VEC_UP)
                    elif key == pygame.K_LEFT:
                        self.cw.select_next_typable(VEC_LEFT)
                    elif key == pygame.K_RIGHT:
                        self.cw.select_next_typable(VEC_RIGHT)

    def handle_mode_text_entry(self):
        # ctrl + backspace clears entire text box
        should_finish = False
        if self.inp.combo_pressed(pygame.K_LCTRL, pygame.K_BACKSPACE):
            self.text.set_string(str())
        else:
            for key, btn in self.inp.buttons.items():
                if btn.state == ButtonState.PRESSED:
                    # Letters and punctuation should be typed
                    if is_letter(key) or is_punct(key):
                        char = get_key_char(key)
                        if self.inp.is_caps():
                            char = char.upper()
                        self.text.add_character(char)
                    # Backspace deletes a letter
                    elif key == pygame.K_BACKSPACE:
                        self.text.backspace()
                    # Return finishes text entry mode
                    elif key == pygame.K_RETURN:
                        should_finish = self.exec_func()
                    elif key == pygame.K_ESCAPE:
                        should_finish = True
        
        if should_finish:
            self.begin_mode_crossword()
        else:
            self.screen.blit(self.text.image, (100, 100))

    def begin_mode_text_entry(self, exec_func):
        self.input_mode = InputMode.TEXT_ENTRY
        self.exec_func = exec_func
        self.screen.fill((0,0,0))

    def begin_mode_crossword(self):
        self.input_mode = InputMode.CROSSWORD
        self.exec_func = None
        self.screen.fill((0,0,0))
        self.cw.redraw()
        self.draw_buttons()

    def request_suggestion(self):
        if not self.awaiting_suggestion:
            word = self.cw.get_highlighted_word()
            if word is not None:
                self.awaiting_suggestion = True
                suggester.send_request(word)

    # ----------------- #
    # Utility functions #
    # ----------------- #

    def get_tile_coord(self, screen_coord: Vec) -> Vec:
        return (screen_coord - CW_MIN) // 32

    def get_screen_coord(self, tile_coord: Vec) -> Vec:
        return (tile_coord * 32) + CW_MIN

    def attempt_save(self) -> bool:
        path = self.text.get_string()
        overwrite = self.inp.any_down(pygame.K_LCTRL, pygame.K_RCTRL)
        if len(path):
            success, reason = self.cw.save(path, overwrite)
            if success:
                return True
            else:
                print(f"[WARNING] Could not save at {path}\n -> Reason: {reason}")
        return False

    def attempt_load(self) -> bool:
        path = self.text.get_string()
        if len(path):
            success, reason = self.cw.load(path)
            if success:
                return True
            else:
                print(f"[WARNING] Could not load {path}\n -> Reason: {reason}")
        return False

    def draw_buttons(self):
        for btn in self.buttons:
            btn.draw()
