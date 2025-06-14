import pygame


class GameEngine:
    def __init__(self):
        self.running = True
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        pass  # Update game state here

    def render(self):
        self.screen.fill((0, 0, 0))  # Clear screen with black
        pygame.display.flip()  # Update the full display Surface to the screen

    def quit(self):
        pygame.quit()