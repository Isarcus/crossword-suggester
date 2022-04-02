from pygame.font import Font
from pygame import Surface, Rect

ALL_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz/\\~.,:;0123456789!@#$%^&*()-_=+[]{}<> ")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class TextBox:
    def __init__(self, font: Font, color: tuple[int], max_width: int, boundary_width: int):
        max_height = font.get_height() + 2

        self.font = font
        self.color = color
        self.bd_width = boundary_width
        self.text_height = max_height
        
        self.size = (max_width + boundary_width*2, max_height + boundary_width*2)
        self.pos_x = 0
        self.letter_tiles = dict([(l, font.render(l, True, color)) for l in ALL_CHARS])
        self.string = str()
        self.image = Surface(self.size)
        self.redraw()

    def add_character(self, char: str):
        self.validate_string(char)
        tile = self.letter_tiles[char]
        width = tile.get_size()[0]
        new_pos_x = self.pos_x + width

        if new_pos_x < self.size[0] - self.bd_width*2:
            self.image.blit(tile, self.get_pos())
            self.string += char
            self.pos_x = new_pos_x

    def set_string(self, string: str):
        self.validate_string(string)
        self.string = string
        self.redraw()

    def get_string(self) -> str:
        return self.string

    def get_pos(self) -> tuple[int]:
        return (self.pos_x + self.bd_width, self.bd_width)

    def backspace(self):
        if len(self.string):
            del_char = self.string[-1]
            del_width = self.letter_tiles[del_char].get_size()[0]
            self.pos_x -= del_width

            pos = self.get_pos()
            self.image.fill(BLACK, Rect(pos[0], pos[1], del_width, self.text_height))
            self.string = self.string[:-1]

    def redraw(self):
        img = self.font.render(self.string, True, self.color)
        self.pos_x = img.get_size()[0]

        self.image.fill(BLACK)
        self.image.blit(img, (self.bd_width*2,)*2)
        self.draw_boundary()

    def draw_boundary(self):
        self.image.fill(WHITE, Rect(0, 0,                            self.size[0], self.bd_width))
        self.image.fill(WHITE, Rect(0, self.size[1] - self.bd_width, self.size[0], self.bd_width))
        self.image.fill(WHITE, Rect(0, 0,                            self.bd_width, self.size[1]))
        self.image.fill(WHITE, Rect(self.size[0] - self.bd_width, 0, self.bd_width, self.size[1]))

    def validate_string(self, string: str):
        for c in string:
            if self.letter_tiles.get(c, None) is None:
                self.letter_tiles[c] = self.font.render(c, True, self.color)
