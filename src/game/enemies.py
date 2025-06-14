class Enemy:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.alive = True

    def move(self):
        self.y += self.speed
        if self.y > 600:  # Assuming the screen height is 600
            self.alive = False

    def reset(self, x, y):
        self.x = x
        self.y = y
        self.alive = True

    def draw(self, surface):
        if self.alive:
            # Placeholder for enemy drawing logic
            pygame.draw.rect(surface, (255, 0, 0), (self.x, self.y, 50, 50))  # Example enemy representation

    def is_colliding(self, player_rect):
        enemy_rect = pygame.Rect(self.x, self.y, 50, 50)  # Example enemy size
        return enemy_rect.colliderect(player_rect)