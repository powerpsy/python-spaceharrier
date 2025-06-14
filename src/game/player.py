class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.health = 100
        self.score = 0

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def shoot(self):
        # Logic for shooting
        pass

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def reset(self):
        self.health = 100
        self.score = 0
        self.x = 0
        self.y = 0