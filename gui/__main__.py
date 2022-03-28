import pygame
from pathlib import Path
from gui.crossword import Crossword

DISPLAY_SIZE = (960,720)
CW_SIZE = (800, 600)

def main():
    # Path resolution
    this_dir = Path(__file__).parent
    images_dir = this_dir.joinpath("images")

    # Load resources
    pygame.init()
    logo = pygame.image.load(images_dir.joinpath("logo32.png"))
    font = pygame.font.SysFont(None, 40)

    # Window initialization
    pygame.display.set_icon(logo)
    pygame.display.set_caption("Crosswords")
    screen = pygame.display.set_mode(DISPLAY_SIZE, pygame.RESIZABLE)
    
    # Object initialization
    cw = Crossword((10, 10), CW_SIZE, font)
    for idx, letter in enumerate("CROSSWORD"):
        cw.set_letter(letter, (0, idx))

    screen.blit(cw.image, dest=(0, 0))
    pygame.display.flip()

    # Main loop
    running = True
    while running:
        # Should I quit?
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Don't bother with keys unless window focused
        if not pygame.key.get_focused():
            continue

        keys = pygame.key.get_pressed()

if __name__ == "__main__":
    main()
