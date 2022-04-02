import pygame
from pathlib import Path
from gui.game import Game
from gui.timer import Timer
from gui import suggester

DISPLAY_SIZE = (960,720)
MAX_FPS = 30
FRAME_PERIOD = 1.0 / MAX_FPS

def main():
    # Initialize word suggester first
    suggester.init()

    # Load resources
    this_dir = Path(__file__).parent
    images_dir = this_dir.joinpath("images")
    logo = pygame.image.load(images_dir.joinpath("logo32.png"))

    # Window initialization
    pygame.init()
    pygame.display.set_icon(logo)
    pygame.display.set_caption("Crosswords")
    screen = pygame.display.set_mode(DISPLAY_SIZE)
    
    # Game initialization
    game = Game(DISPLAY_SIZE, screen)
    timer = Timer(FRAME_PERIOD)

    # Main loop
    running = True
    init_time = pygame.time.get_ticks()
    iters = 0
    while running:
        # Pause to keep FPS below limit
        timer.wait()
        iters += 1
        
        # Should I quit?
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        game.tick()
        pygame.display.flip()

    fps = iters / ((pygame.time.get_ticks() - init_time) / 1000)
    print(f"Average FPS: {fps:.2f}")
    suggester.shutdown()

if __name__ == "__main__":
    main()
