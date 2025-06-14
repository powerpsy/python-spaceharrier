import pygame
import sys
import math
import random

WIDTH, HEIGHT = 800, 600
CENTER = (WIDTH // 2, HEIGHT // 3)
GRAY_LIGHT = (180, 180, 180)
GRAY_DARK = (60, 60, 60)
BLACK = (0, 0, 0)
PLAYER_COLOR = (0, 200, 255)
SHOT_COLOR = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (200, 40, 40)

MARGIN = 100
MAX_RADIUS = 420
enemy_spawn_rate = 200  # ms, modifiable par le bonus glowing

def get_arc_points(center, radius, angle_start, angle_end, num_points=30):
    """Retourne une liste de points sur un arc de cercle."""
    points = []
    for i in range(num_points + 1):
        angle = angle_start + (angle_end - angle_start) * i / num_points
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        points.append((x, y))
    return points

def draw_terrain(screen):
    screen.fill(BLACK)
    margin = MARGIN
    bottom_y = HEIGHT - 1

    # Points extrêmes bas
    left_base = (margin, bottom_y)
    right_base = (WIDTH - margin, bottom_y)

    # Angles des lignes extrêmes
    angle_left = math.atan2(CENTER[1] - bottom_y, CENTER[0] - margin)
    angle_right = math.atan2(CENTER[1] - bottom_y, CENTER[0] - (WIDTH - margin))

    # Points sur l'arc le plus grand
    arc_outer = get_arc_points(CENTER, MAX_RADIUS, angle_right, angle_left, 40)

    # Construction du polygone à remplir (zone centrale)
    polygon_points = [left_base] + arc_outer + [right_base]
    pygame.draw.polygon(screen, GRAY_DARK, polygon_points)

    # Tracer les traits (gris clair)
    pygame.draw.line(screen, GRAY_LIGHT, left_base, CENTER, 2)
    pygame.draw.line(screen, GRAY_LIGHT, right_base, CENTER, 2)
    pygame.draw.line(screen, GRAY_LIGHT, (WIDTH // 3, bottom_y), CENTER, 2)
    pygame.draw.line(screen, GRAY_LIGHT, (2 * WIDTH // 3, bottom_y), CENTER, 2)

    # Tracer les arcs (gris clair)
    for radius in range(100, MAX_RADIUS, 80):
        rect = pygame.Rect(CENTER[0] - radius, CENTER[1] - radius, 2 * radius, 2 * radius)
        pygame.draw.arc(screen, GRAY_LIGHT, rect, angle_right, angle_left, 2)

def draw_fps(screen, clock, font, enemy_spawn_rate):
    fps = int(clock.get_fps())
    text = font.render(f"FPS: {fps}", True, WHITE)
    screen.blit(text, (10, 10))
    # Affiche la fréquence d'apparition des ennemis sous les FPS
    text2 = font.render(f"Enemy spawn: {enemy_spawn_rate} ms", True, WHITE)
    screen.blit(text2, (10, 10 + text.get_height() + 4))

def draw_stats(screen, font, player):
    lines = [
        f"Fire rate: {player.fire_rate} ms",
        f"Bullet size: {player.bullet_size}",
        f"Bullet speed: {player.bullet_speed_z:.2f}",
        f"Shooting dist.: {player.bullet_z0:.2f}"
    ]
    for i, line in enumerate(lines):
        text = font.render(line, True, WHITE)
        screen.blit(text, (WIDTH - text.get_width() - 20, 10 + i * 24))

def draw_life_bar(screen, player):
    max_life = 1000
    bar_width = 200
    bar_height = 24
    x = (WIDTH - bar_width) // 2  # Centré horizontalement
    y = HEIGHT - bar_height - 20  # En bas de l'écran
    # Fond gris clair
    pygame.draw.rect(screen, GRAY_LIGHT, (x, y, bar_width, bar_height), border_radius=8)
    # Remplissage rouge
    fill = int(bar_width * player.life / max_life)
    pygame.draw.rect(screen, RED, (x, y, fill, bar_height), border_radius=8)
    # (Plus de texte)

class Shot:
    def __init__(self, x, y, target, size, speed, max_distance):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.max_distance = max_distance
        self.distance_travelled = 0
        dx = target[0] - x
        dy = target[1] - y
        length = math.hypot(dx, dy)
        if length == 0:
            self.vx, self.vy = 0, -1
        else:
            self.vx = dx / length
            self.vy = dy / length

    def update(self):
        self.x += self.vx * self.speed
        self.y += self.vy * self.speed
        self.distance_travelled += self.speed

    def draw(self, screen, size):
        pygame.draw.circle(screen, SHOT_COLOR, (int(self.x), int(self.y)), size)

    def is_offscreen(self):
        # Le tir disparaît s'il atteint le point de fuite ou sort de l'écran
        if math.hypot(self.x - CENTER[0], self.y - CENTER[1]) < 10:
            return True
        if self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
            return True
        if self.distance_travelled > self.max_distance:
            return True
        return False

    def get_screen_pos(self):
        return int(self.x), int(self.y)

class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 120
        self.bullet_size = 3
        self.fire_rate = 500  # ms
        self.bullet_speed_z = 0.0005
        self.bullet_z0 = 0.02
        self.last_shot_time = 0
        self.life = 1000

    def update(self, min_x, max_x):
        mouse_x = pygame.mouse.get_pos()[0]
        left = min(min_x, max_x)
        right = max(min_x, max_x)
        self.x = max(left, min(right, mouse_x))

    def draw(self, screen):
        pygame.draw.rect(screen, PLAYER_COLOR, (self.x - 15, self.y - 30, 30, 50))
        pygame.draw.circle(screen, PLAYER_COLOR, (self.x, self.y - 40), 15)
        pygame.draw.line(screen, PLAYER_COLOR, (self.x - 15, self.y - 10), (self.x - 30, self.y + 10), 6)
        pygame.draw.line(screen, PLAYER_COLOR, (self.x + 15, self.y - 10), (self.x + 30, self.y + 10), 6)
        pygame.draw.rect(screen, (180, 180, 180), (self.x - 7, self.y + 10, 14, 18))

    def can_shoot(self):
        now = pygame.time.get_ticks()
        return now - self.last_shot_time >= self.fire_rate

    def shoot(self):
        self.last_shot_time = pygame.time.get_ticks()
        return Shot(
            self.x, self.y - 40, CENTER,
            self.bullet_size, 16, 700
        )

def project_point(x, y, z, center, focal_length=1.0):
    """Projette un point 3D sur l'écran avec le point de fuite comme centre de perspective."""
    # Plus z est grand, plus le point est proche du bas de l'écran
    px = center[0] + x * focal_length / (z + 1e-6)
    py = center[1] + y * focal_length / (z + 1e-6)
    return int(px), int(py)

class Enemy:
    def __init__(self, x_screen, z0=0.02, speed_z=0.001, special=False, glowing=False, hp=1):
        self.x_fuite = CENTER[0]
        self.y_fuite = CENTER[1]
        self.z0 = z0
        self.z = z0
        self.speed_z = speed_z
        self.x_start = x_screen
        self.hp = hp
        self.special = special
        self.glowing = glowing
        self.contact_timer = 0

    def update(self):
        self.z += self.speed_z
        if self.z > 1.0:
            self.z = 1.0

    def get_screen_pos(self):
        factor = (self.z - self.z0) / (1.0 - self.z0)
        x = self.x_fuite + (self.x_start - self.x_fuite) * factor
        y = self.y_fuite + (HEIGHT - self.y_fuite) * factor
        return int(x), int(y)

    def get_size(self):
        return int(1 + (100 - 1) * ((self.z - self.z0) / (1.0 - self.z0)))

    def draw(self, screen):
        x, y = self.get_screen_pos()
        size = self.get_size()
        offset = int(size * 0.3)
        if self.glowing:
            color = (180, 60, 255)
            back_color = (100, 0, 180)
            # Effet glowing
            glow_color = (220, 120, 255)
            pygame.draw.rect(screen, glow_color, (x - size//2 - 6, y - size//2 - 6, size+12, size+12), border_radius=8)
        elif self.special:
            color = (60, 120, 255)
            back_color = (30, 60, 180)
        else:
            color = (255, 60, 60)
            back_color = (180, 30, 30)
        # Face avant
        pygame.draw.rect(screen, color, (x - size//2, y - size//2, size, size))
        # Face arrière (plus sombre)
        pygame.draw.rect(screen, back_color, (x - size//2 + offset, y - size//2 - offset, size, size), 2)
        # Arêtes reliant les faces
        pygame.draw.line(screen, (255, 255, 255), (x - size//2, y - size//2), (x - size//2 + offset, y - size//2 - offset), 2)
        pygame.draw.line(screen, (255, 255, 255), (x + size//2, y - size//2), (x + size//2 + offset, y - size//2 - offset), 2)
        pygame.draw.line(screen, (255, 255, 255), (x - size//2, y + size//2), (x - size//2 + offset, y + size//2 - offset), 2)
        pygame.draw.line(screen, (255, 255, 255), (x + size//2, y + size//2), (x + size//2 + offset, y + size//2 - offset), 2)

    def is_offscreen(self):
        return self.z >= 1.0

def get_intersection_x(center, margin, radius, height):
    x0, y0 = margin, height
    x1, y1 = center
    dx = x1 - x0
    dy = y1 - y0
    a = dx**2 + dy**2
    b = 2 * (dx * (x0 - x1) + dy * (y0 - y1))
    c = (x0 - x1)**2 + (y0 - y1)**2 - radius**2
    delta = b**2 - 4*a*c
    if delta < 0:
        return x0
    t = (-b + math.sqrt(delta)) / (2*a)
    x = x0 + t*dx
    return int(x)

def draw_score(screen, score):
    font_big = pygame.font.SysFont(None, 48)
    text = font_big.render(f"Score: {score}", True, WHITE)
    screen.blit(text, ((WIDTH - text.get_width()) // 2, 10))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Python Space Harrier - main.py complet")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)
    player = Player()
    shots = []
    enemies = []
    enemy_timer = pygame.time.get_ticks()
    score = 0

    margin = MARGIN
    bottom_y = HEIGHT - 1

    enemy_spawn_rate = 200  # <--- Mets cette ligne ici, dans main()

    game_over = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if game_over and event.type == pygame.MOUSEBUTTONDOWN:
                # Reset du jeu
                player = Player()
                shots = []
                enemies = []
                score = 0
                enemy_spawn_rate = 200
                enemy_timer = pygame.time.get_ticks()
                game_over = False

        min_x = get_intersection_x(CENTER, margin, MAX_RADIUS, bottom_y)
        max_x = get_intersection_x(CENTER, WIDTH - margin, MAX_RADIUS, bottom_y)

        player.update(min_x, max_x)

        if player.can_shoot():
            shots.append(player.shoot())

        now = pygame.time.get_ticks()
        if now - enemy_timer > enemy_spawn_rate:
            x_spawn = random.randint(min(min_x, max_x), max(min_x, max_x))
            glowing = False
            special = False
            rand = random.randint(1, 80)
            if rand == 1:
                glowing = True
            elif rand <= 10:
                special = True
            if score > 1000:
                hp = 5
            elif score > 500:
                hp = 3
            elif score > 200:
                hp = 2
            else:
                hp = 1
            enemies.append(Enemy(x_spawn, special=special, glowing=glowing, hp=hp))
            enemy_timer = now

        for shot in shots:
            shot.update()
        shots = [shot for shot in shots if not shot.is_offscreen()]

        for enemy in enemies:
            enemy.update()
        enemies = [e for e in enemies if not e.is_offscreen()]

        shots_to_remove = []
        enemies_to_remove = []
        for shot in shots:
            shot_x, shot_y = shot.get_screen_pos()
            for enemy in enemies:
                enemy_x, enemy_y = enemy.get_screen_pos()
                size = enemy.get_size()
                if abs(shot_x - enemy_x) < size//2 and abs(shot_y - enemy_y) < size//2:
                    shots_to_remove.append(shot)
                    enemy.hp -= 1
                    if enemy.hp <= 0:
                        enemies_to_remove.append(enemy)
                        score += 1
                        # ...bonus code...
                        if enemy.special:
                            bonus = random.choice(['fire_rate', 'bullet_size', 'bullet_speed_z', 'bullet_z0'])
                            if bonus == 'fire_rate':
                                player.fire_rate = max(1, int(player.fire_rate * 0.9))
                            elif bonus == 'bullet_size':
                                player.bullet_size = int(player.bullet_size * 1.1) or 1
                            elif bonus == 'bullet_speed_z':
                                player.bullet_speed_z = round(player.bullet_speed_z * 1.1, 6)
                            elif bonus == 'bullet_z0':
                                player.bullet_z0 = round(player.bullet_z0 * 1.1, 6)
                            print(f"Bonus: {bonus} augmenté de 10%")

        shots = [s for s in shots if s not in shots_to_remove]
        enemies = [e for e in enemies if e not in enemies_to_remove]

        for enemy in enemies_to_remove:
            if enemy.special:
                # Bleu
                bonus = random.choice(['fire_rate', 'bullet_size', 'bullet_speed_z', 'bullet_z0'])
                if bonus == 'fire_rate':
                    player.fire_rate = max(1, int(player.fire_rate * 0.9))
                elif bonus == 'bullet_size':
                    player.bullet_size = int(player.bullet_size * 1.1) or 1
                elif bonus == 'bullet_speed_z':
                    player.bullet_speed_z = round(player.bullet_speed_z * 1.1, 6)
                elif bonus == 'bullet_z0':
                    player.bullet_z0 = round(player.bullet_z0 * 1.1, 6)
                print(f"Bonus: {bonus} augmenté de 10%")
            if enemy.glowing:
                enemy_spawn_rate = max(20, int(enemy_spawn_rate * 0.9))
                print("Bonus: Apparition des ennemis accélérée de 10%")

        draw_terrain(screen)
        draw_score(screen, score)
        for enemy in enemies:
            _, enemy_y = enemy.get_screen_pos()
            if enemy_y < player.y:
                enemy.draw(screen)
        player.draw(screen)
        for enemy in enemies:
            _, enemy_y = enemy.get_screen_pos()
            if enemy_y >= player.y:
                enemy.draw(screen)
        for shot in shots:
            shot.draw(screen, player.bullet_size)
        draw_fps(screen, clock, font, enemy_spawn_rate)
        draw_stats(screen, font, player)
        draw_life_bar(screen, player)

        # Gestion des dégâts au joueur si contact avec un ennemi
        for enemy in enemies:
            enemy_x, enemy_y = enemy.get_screen_pos()
            size = enemy.get_size()
            # Collision simple : superposition des carrés (cube du joueur ≈ 30x50)
            if (abs(enemy_x - player.x) < (size//2 + 15)) and (abs(enemy_y - player.y) < (size//2 + 25)):
                # Contact : incrémente le timer de contact
                enemy.contact_timer += clock.get_time()
                if enemy.contact_timer >= 100:  # 0.1s = 100 ms
                    player.life = max(0, player.life - 10)
                    enemy.contact_timer = 0
            else:
                # Pas de contact, reset le timer
                enemy.contact_timer = 0

        if player.life <= 0:
            game_over = True
            player.fire_rate = 100000

        if game_over:
            # Affiche le score en gros au centre
            font_big = pygame.font.SysFont(None, 72)
            text = font_big.render(f"Score: {score}", True, WHITE)
            screen.blit(text, ((WIDTH - text.get_width()) // 2, (HEIGHT - text.get_height()) // 2))
            pygame.display.flip()
            clock.tick(60)
            continue  # saute le reste de la boucle tant que game_over

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()