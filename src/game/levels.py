class Level:
    def __init__(self, level_number, background_image, enemy_data):
        self.level_number = level_number
        self.background_image = background_image
        self.enemy_data = enemy_data
        self.enemies = []

    def load_level(self):
        # Load the background image and initialize enemies
        self.load_background()
        self.initialize_enemies()

    def load_background(self):
        # Load the background image for the level
        pass  # Implement background loading logic

    def initialize_enemies(self):
        # Initialize enemies based on enemy_data
        for data in self.enemy_data:
            enemy = self.create_enemy(data)
            self.enemies.append(enemy)

    def create_enemy(self, data):
        # Create an enemy instance based on the provided data
        pass  # Implement enemy creation logic

    def update(self):
        # Update the state of the level, including enemies
        for enemy in self.enemies:
            enemy.update()  # Assuming enemy has an update method

    def draw(self, surface):
        # Draw the background and enemies on the given surface
        pass  # Implement drawing logic