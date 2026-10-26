import pygame
import random
import sys
import os
import math

# ------------------------------------------------------------
# Neon Math Space Shooter
# Keep bg_music.mp3.mp3 in the same folder as this Python file.
# ------------------------------------------------------------
pygame.init()
try:
    pygame.mixer.init()
except pygame.error:
    pass

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Neon Math Space Shooter")
CLOCK = pygame.time.Clock()

# Neon palette
BLACK = (5, 7, 22)
WHITE = (240, 250, 255)
CYAN = (40, 245, 255)
PINK = (255, 55, 190)
PURPLE = (155, 85, 255)
RED = (255, 70, 95)
GREEN = (75, 255, 150)
YELLOW = (255, 225, 80)
BLUE = (65, 130, 255)
DIM = (70, 95, 130)
DARK_PANEL = (12, 18, 43)

FONT_TINY = pygame.font.SysFont("arial", 16)
FONT_SMALL = pygame.font.SysFont("arial", 20)
FONT_MED = pygame.font.SysFont("arial", 27, bold=True)
FONT_LARGE = pygame.font.SysFont("arial", 42, bold=True)
FONT_HUGE = pygame.font.SysFont("arial", 58, bold=True)

SCORE_FILE = "highscores.txt"
MUSIC_FILE = "bg_music.mp3.mp3"

def load_music():
    """Load and loop the supplied background music, if available."""
    music_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), MUSIC_FILE)
    if pygame.mixer.get_init() and os.path.exists(music_path):
        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.42)
            pygame.mixer.music.play(-1)
        except pygame.error as exc:
            print(f"Music could not be played: {exc}")
    else:
        print(f"Music file not found or audio unavailable: {music_path}")

def load_high_scores():
    scores = {}
    if os.path.exists(SCORE_FILE):
        try:
            with open(SCORE_FILE, "r", encoding="utf-8") as file:
                for line in file:
                    parts = line.strip().rsplit(",", 1)
                    if len(parts) == 2:
                        try:
                            name, score_text = parts
                            score = int(score_text)
                            if name.strip():
                                scores[name.strip()] = max(scores.get(name.strip(), 0), score)
                        except ValueError:
                            continue
        except OSError:
            pass
    return sorted(scores.items(), key=lambda item: item[1], reverse=True)[:5]

def save_high_score(name, score):
    scores = dict(load_all_high_scores())
    name = name.strip()[:10] or "Player1"
    scores[name] = max(scores.get(name, 0), score)
    try:
        with open(SCORE_FILE, "w", encoding="utf-8") as file:
            for player, points in sorted(scores.items(), key=lambda item: item[1], reverse=True):
                file.write(f"{player},{points}\n")
    except OSError as exc:
        print(f"Could not save high scores: {exc}")

def load_all_high_scores():
    scores = {}
    if os.path.exists(SCORE_FILE):
        try:
            with open(SCORE_FILE, "r", encoding="utf-8") as file:
                for line in file:
                    parts = line.strip().rsplit(",", 1)
                    if len(parts) == 2:
                        try:
                            name, score_text = parts
                            scores[name.strip()] = max(scores.get(name.strip(), 0), int(score_text))
                        except ValueError:
                            pass
        except OSError:
            pass
    return sorted(scores.items(), key=lambda item: item[1], reverse=True)

def draw_text(surface, text, font, color, center, shadow=True):
    if shadow:
        shadow_img = font.render(str(text), True, (20, 50, 85))
        surface.blit(shadow_img, shadow_img.get_rect(center=(center[0] + 2, center[1] + 2)))
    image = font.render(str(text), True, color)
    surface.blit(image, image.get_rect(center=center))

def neon_line(surface, color, start, end, width=2):
    pygame.draw.line(surface, color, start, end, width)
    if width >= 2:
        glow = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.line(glow, (*color, 45), start, end, width + 5)
        surface.blit(glow, (0, 0))

class StarField:
    def __init__(self):
        self.stars = [
            [random.randrange(SCREEN_WIDTH), random.randrange(SCREEN_HEIGHT),
             random.uniform(0.5, 3.0), random.choice([CYAN, PURPLE, WHITE])]
            for _ in range(95)
        ]

    def update(self, speed_scale=1.0):
        for star in self.stars:
            star[1] += star[2] * speed_scale
            if star[1] >= SCREEN_HEIGHT:
                star[0] = random.randrange(SCREEN_WIDTH)
                star[1] = 0
                star[2] = random.uniform(0.5, 3.0)

    def draw(self, surface):
        for x, y, speed, color in self.stars:
            radius = 1 if speed < 1.7 else 2
            pygame.draw.circle(surface, color, (int(x), int(y)), radius)

class Particle:
    def __init__(self, x, y, color, velocity=None, life=35, radius=3):
        self.x, self.y = float(x), float(y)
        angle = random.uniform(0, math.tau)
        speed = random.uniform(1, 5)
        self.vx, self.vy = velocity or (math.cos(angle) * speed, math.sin(angle) * speed)
        self.life = self.max_life = life
        self.color = color
        self.radius = radius

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.97
        self.vy *= 0.97
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            radius = max(1, int(self.radius * self.life / self.max_life))
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), radius)

class Player:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 68
        self.speed = 6
        self.width, self.height = 44, 42
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (self.x, self.y)
        self.shield_time = 0
        self.rapid_time = 0
        self.invulnerable_time = 0
        self.shot_cooldown = 0

    def update(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        self.x = max(self.width // 2, min(SCREEN_WIDTH - self.width // 2, self.x))
        self.rect.center = (int(self.x), self.y)
        self.shield_time = max(0, self.shield_time - 1)
        self.rapid_time = max(0, self.rapid_time - 1)
        self.invulnerable_time = max(0, self.invulnerable_time - 1)
        self.shot_cooldown = max(0, self.shot_cooldown - 1)

    def draw(self, surface):
        # Twin neon fins and cockpit
        points = [(self.x, self.y - 25), (self.x - 23, self.y + 19),
                  (self.x - 7, self.y + 13), (self.x, self.y + 20),
                  (self.x + 7, self.y + 13), (self.x + 23, self.y + 19)]
        if self.invulnerable_time and (self.invulnerable_time // 4) % 2 == 0:
            return
        pygame.draw.polygon(surface, PURPLE, points)
        pygame.draw.polygon(surface, CYAN, points, 2)
        pygame.draw.ellipse(surface, WHITE, (self.x - 5, self.y - 12, 10, 17))
        pygame.draw.polygon(surface, PINK, [(self.x - 9, self.y + 17), (self.x, self.y + 29), (self.x + 9, self.y + 17)])
        if self.shield_time > 0:
            pygame.draw.circle(surface, CYAN, (int(self.x), self.y), 32, 2)
            pygame.draw.circle(surface, (50, 120, 180), (int(self.x), self.y), 36, 1)

class Bullet:
    def __init__(self, x, y, color=CYAN, speed=10):
        self.rect = pygame.Rect(int(x - 3), int(y - 12), 6, 15)
        self.color = color
        self.speed = speed

    def update(self):
        self.rect.y -= self.speed

    def draw(self, surface):
        pygame.draw.line(surface, self.color, self.rect.midbottom, self.rect.midtop, 4)
        pygame.draw.circle(surface, WHITE, self.rect.midtop, 2)

class Target:
    def __init__(self, x, y, value, speed):
        self.value = value
        self.x, self.y = float(x), float(y)
        self.speed = speed
        self.rect = pygame.Rect(0, 0, 86, 48)
        self.rect.center = (int(self.x), int(self.y))
        self.phase = random.random() * math.tau

    def update(self):
        self.y += self.speed
        self.phase += 0.08
        self.rect.center = (int(self.x + math.sin(self.phase) * 1.5), int(self.y))

    def draw(self, surface):
        pygame.draw.ellipse(surface, (35, 20, 65), self.rect)
        pygame.draw.ellipse(surface, PINK, self.rect, 2)
        pygame.draw.ellipse(surface, PURPLE, self.rect.inflate(-8, -8), 1)
        draw_text(surface, self.value, FONT_SMALL, WHITE, self.rect.center, shadow=False)

class PowerUp:
    TYPES = {
        "SHIELD": (CYAN, "S"),
        "RAPID FIRE": (YELLOW, "R"),
        "LIFE +1": (GREEN, "+"),
        "DOUBLE POINTS": (PINK, "2X"),
    }

    def __init__(self, x, y, kind, speed=2):
        self.x, self.y = x, y
        self.kind = kind
        self.speed = speed
        self.color, self.symbol = self.TYPES[kind]
        self.rect = pygame.Rect(0, 0, 32, 32)
        self.rect.center = (int(x), int(y))
        self.phase = random.random() * math.tau

    def update(self):
        self.y += self.speed
        self.phase += 0.12
        self.rect.center = (int(self.x + math.sin(self.phase) * 2), int(self.y))

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.rect.center, 17, 2)
        pygame.draw.circle(surface, (30, 40, 70), self.rect.center, 13)
        draw_text(surface, self.symbol, FONT_TINY, self.color, self.rect.center, shadow=False)

class Boss:
    def __init__(self, level):
        self.max_health = 8 + level * 2
        self.health = self.max_health
        self.x = SCREEN_WIDTH // 2
        self.y = 105
        self.direction = 1
        self.rect = pygame.Rect(0, 0, 150, 70)
        self.rect.center = (self.x, self.y)
        self.phase = 0

    def update(self):
        self.phase += 0.06
        self.x += self.direction * (2.0 + self.max_health * 0.03)
        if self.x < 95 or self.x > SCREEN_WIDTH - 95:
            self.direction *= -1
        self.y = 100 + math.sin(self.phase) * 12
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        x, y = int(self.x), int(self.y)
        points = [(x - 75, y - 8), (x - 45, y - 32), (x - 15, y - 20),
                  (x, y - 35), (x + 15, y - 20), (x + 45, y - 32),
                  (x + 75, y - 8), (x + 55, y + 28), (x + 20, y + 35),
                  (x - 20, y + 35), (x - 55, y + 28)]
        pygame.draw.polygon(surface, (65, 15, 70), points)
        pygame.draw.polygon(surface, RED, points, 3)
        pygame.draw.circle(surface, PINK, (x - 28, y), 8)
        pygame.draw.circle(surface, PINK, (x + 28, y), 8)
        pygame.draw.line(surface, PURPLE, (x - 45, y + 18), (x + 45, y + 18), 3)
        bar = pygame.Rect(x - 75, y - 48, 150, 8)
        pygame.draw.rect(surface, (55, 25, 50), bar, border_radius=4)
        fill = bar.copy()
        fill.width = int(bar.width * max(0, self.health) / self.max_health)
        pygame.draw.rect(surface, GREEN if self.health / self.max_health > .35 else RED, fill, border_radius=4)

class Game:
    def __init__(self):
        self.stars = StarField()
        self.reset_game()

    def reset_game(self):
        self.player = Player()
        self.bullets = []
        self.targets = []
        self.powerups = []
        self.particles = []
        self.score = 0
        self.lives = 3
        self.level = 1
        self.state = "MENU"
        self.player_name = ""
        self.max_name_len = 10
        self.question = ""
        self.answer = 0
        self.boss = None
        self.boss_spawned_for_level = False
        self.question_timer = 0
        self.spawn_timer = 0
        self.double_points_time = 0
        self.banner_timer = 0
        self.banner_text = ""
        self.shake_time = 0
        self.generate_question()

    def difficulty(self):
        # Score-driven and level-driven difficulty, with a cap.
        return min(12 + self.level * 4 + self.score // 20, 80)

    def target_speed(self):
        return min(1.25 + self.level * 0.22 + self.score * 0.008, 5.5)

    def question_interval(self):
        # Questions cycle more quickly as score and level rise.
        return max(34, 100 - self.level * 5 - self.score // 4)

    def generate_question(self):
        for target in self.targets:
            pass
        self.targets.clear()
        maximum = self.difficulty()
        if self.level == 1 and self.score < 30:
            operation = random.choice(["+", "-", "*"])
        elif self.level < 3:
            operation = random.choice(["+", "-", "*", "*"])
        else:
            operation = random.choice(["+", "-", "*", "/", "*"])
        a, b = random.randint(1, maximum), random.randint(1, maximum)
        if operation == "-":
            a, b = max(a, b), min(a, b)
            self.answer = a - b
        elif operation == "*":
            self.answer = a * b
        elif operation == "/":
            b = random.randint(1, max(2, min(maximum, 12)))
            self.answer = random.randint(1, maximum)
            a = b * self.answer
        else:
            self.answer = a + b
        self.question = f"{a} {operation} {b} = ?"
        options = [self.answer]
        while len(options) < 3:
            offset = random.randint(-max(8, maximum), max(8, maximum))
            wrong = self.answer + offset
            if wrong >= 0 and wrong not in options:
                options.append(wrong)
        random.shuffle(options)
        x_positions = [150, 360, 570]
        for x, value in zip(x_positions, options):
            self.targets.append(Target(x, -35, value, self.target_speed()))
        self.question_timer = 0
        self.spawn_timer = 0

    def burst(self, x, y, color, count=18):
        for _ in range(count):
            self.particles.append(Particle(x, y, color, life=random.randint(18, 38),
                                           radius=random.randint(2, 4)))

    def start_boss(self):
        self.boss = Boss(self.level)
        self.boss_spawned_for_level = True
        self.banner_text = f"LEVEL {self.level} BOSS!"
        self.banner_timer = 130
        self.burst(SCREEN_WIDTH // 2, 100, RED, 35)

    def next_level(self):
        self.level += 1
        self.boss = None
        self.boss_spawned_for_level = False
        self.lives = min(5, self.lives + 1)
        self.banner_text = f"LEVEL {self.level}!"
        self.banner_timer = 120
        self.burst(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, CYAN, 40)
        self.generate_question()

    def collect_powerup(self, powerup):
        if powerup.kind == "SHIELD":
            self.player.shield_time = 60 * 8
        elif powerup.kind == "RAPID FIRE":
            self.player.rapid_time = 60 * 7
        elif powerup.kind == "LIFE +1":
            self.lives = min(5, self.lives + 1)
        elif powerup.kind == "DOUBLE POINTS":
            self.double_points_time = 60 * 8
        self.banner_text = powerup.kind + "!"
        self.banner_timer = 70
        self.burst(powerup.x, powerup.y, powerup.color, 16)

    def lose_life(self):
        if self.player.shield_time > 0:
            self.player.shield_time = 0
            self.burst(self.player.x, self.player.y, CYAN, 20)
            return
        self.lives -= 1
        self.player.invulnerable_time = 75
        self.shake_time = 12
        self.burst(self.player.x, self.player.y, RED, 24)
        if self.lives <= 0:
            self.state = "GAME_OVER"

    def update(self):
        keys = pygame.key.get_pressed()
        self.stars.update(1 + self.level * 0.08)
        self.player.update(keys)
        self.double_points_time = max(0, self.double_points_time - 1)
        self.banner_timer = max(0, self.banner_timer - 1)
        self.shake_time = max(0, self.shake_time - 1)

        for particle in self.particles:
            particle.update()
        self.particles = [p for p in self.particles if p.life > 0]

        if self.state != "PLAYING":
            return

        self.question_timer += 1
        self.spawn_timer += 1

        if self.player.shot_cooldown == 0:
            if keys[pygame.K_SPACE]:
                if self.player.rapid_time > 0:
                    self.bullets.extend([Bullet(self.player.x - 10, self.player.y - 20),
                                         Bullet(self.player.x + 10, self.player.y - 20)])
                    self.player.shot_cooldown = 7
                else:
                    self.bullets.append(Bullet(self.player.x, self.player.y - 20))
                    self.player.shot_cooldown = 14

        for bullet in self.bullets:
            bullet.update()
        self.bullets = [b for b in self.bullets if b.rect.bottom > 0]

        for target in self.targets:
            target.speed = self.target_speed()
            target.update()
        for powerup in self.powerups:
            powerup.update()
        self.powerups = [p for p in self.powerups if p.rect.top < SCREEN_HEIGHT]

        if self.boss:
            self.boss.update()

        # Correct answer targets; incorrect targets cost a life.
        for bullet in list(self.bullets):
            hit_target = next((t for t in self.targets if bullet.rect.colliderect(t.rect)), None)
            if hit_target:
                self.bullets.remove(bullet)
                if hit_target.value == self.answer:
                    self.score += 20 if self.double_points_time else 10
                    self.burst(hit_target.rect.centerx, hit_target.rect.centery, CYAN, 22)
                    if random.random() < 0.22:
                        kind = random.choice(list(PowerUp.TYPES.keys()))
                        self.powerups.append(PowerUp(hit_target.rect.centerx, hit_target.rect.centery, kind))
                    self.generate_question()
                    if self.score >= self.level * 100 and not self.boss_spawned_for_level and not self.boss:
                        self.start_boss()
                else:
                    self.burst(hit_target.rect.centerx, hit_target.rect.centery, RED, 12)
                    self.targets.remove(hit_target)
                    self.lose_life()
                break

            if self.boss and bullet.rect.colliderect(self.boss.rect):
                self.bullets.remove(bullet)
                self.boss.health -= 1
                self.burst(bullet.rect.centerx, bullet.rect.centery, PINK, 5)
                if self.boss.health <= 0:
                    self.score += 50
                    self.burst(self.boss.x, self.boss.y, YELLOW, 55)
                    self.boss = None
                    self.next_level()
                break

        # Targets reaching the bottom or hitting the player cost a life.
        for target in list(self.targets):
            if target.rect.top > SCREEN_HEIGHT:
                self.targets.remove(target)
                self.lose_life()
                self.generate_question()
                break
            if target.rect.colliderect(self.player.rect):
                self.targets.remove(target)
                self.lose_life()
                self.generate_question()
                break

        for powerup in list(self.powerups):
            if powerup.rect.colliderect(self.player.rect):
                self.collect_powerup(powerup)
                self.powerups.remove(powerup)

        # Spawn the boss when the level's score threshold is reached.
        if self.score >= self.level * 100 and not self.boss_spawned_for_level and not self.boss:
            self.start_boss()

        # Questions and targets refresh on a score-scaled timer, even if the player waits.
        if not self.boss and self.question_timer >= self.question_interval():
            self.generate_question()

    def draw_background(self):
        SCREEN.fill(BLACK)
        # Subtle neon grid in the lower background.
        for y in range(390, SCREEN_HEIGHT, 35):
            pygame.draw.line(SCREEN, (12, 25, 55), (0, y), (SCREEN_WIDTH, y), 1)
        for x in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(SCREEN, (10, 22, 48), (x, 390), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 1)
        self.stars.draw(SCREEN)

    def draw_hud(self):
        pygame.draw.rect(SCREEN, DARK_PANEL, (12, 10, 300, 92), border_radius=12)
        pygame.draw.rect(SCREEN, CYAN, (12, 10, 300, 92), 1, border_radius=12)
        SCREEN.blit(FONT_SMALL.render(f"SCORE  {self.score}", True, GREEN), (25, 18))
        SCREEN.blit(FONT_SMALL.render(f"LIVES  {self.lives}", True, RED), (25, 45))
        SCREEN.blit(FONT_TINY.render(f"LEVEL {self.level}  |  NEXT BOSS AT {self.level * 100}", True, CYAN), (25, 74))

        q_panel = pygame.Rect(325, 12, 300, 48)
        pygame.draw.rect(SCREEN, DARK_PANEL, q_panel, border_radius=10)
        pygame.draw.rect(SCREEN, PURPLE, q_panel, 2, border_radius=10)
        draw_text(SCREEN, self.question, FONT_MED, WHITE, q_panel.center)

        if self.player.rapid_time:
            SCREEN.blit(FONT_TINY.render("RAPID FIRE", True, YELLOW), (SCREEN_WIDTH - 145, 18))
        if self.player.shield_time:
            SCREEN.blit(FONT_TINY.render("SHIELD", True, CYAN), (SCREEN_WIDTH - 145, 40))
        if self.double_points_time:
            SCREEN.blit(FONT_TINY.render("2X POINTS", True, PINK), (SCREEN_WIDTH - 145, 62))

    def draw(self):
        self.draw_background()
        if self.state == "MENU":
            draw_text(SCREEN, "NEON MATH", FONT_HUGE, CYAN, (SCREEN_WIDTH // 2, 190))
            draw_text(SCREEN, "SPACE SHOOTER", FONT_LARGE, PINK, (SCREEN_WIDTH // 2, 245))
            draw_text(SCREEN, "Move: LEFT / RIGHT or A / D", FONT_SMALL, WHITE, (SCREEN_WIDTH // 2, 330))
            draw_text(SCREEN, "Shoot: SPACE     |     Collect glowing power-ups", FONT_SMALL, WHITE, (SCREEN_WIDTH // 2, 365))
            draw_text(SCREEN, "Press ENTER to launch", FONT_MED, GREEN, (SCREEN_WIDTH // 2, 430))
            draw_text(SCREEN, "Boss battles every 100 points • Maths gets harder as you level up", FONT_TINY, DIM, (SCREEN_WIDTH // 2, 475))
        elif self.state == "PLAYING":
            self.draw_hud()
            for target in self.targets:
                target.draw(SCREEN)
            for powerup in self.powerups:
                powerup.draw(SCREEN)
            for bullet in self.bullets:
                bullet.draw(SCREEN)
            if self.boss:
                self.boss.draw(SCREEN)
                draw_text(SCREEN, "BOSS BATTLE — HIT THE BOSS!", FONT_SMALL, RED, (SCREEN_WIDTH // 2, 195))
            self.player.draw(SCREEN)
            for particle in self.particles:
                particle.draw(SCREEN)
            if self.banner_timer:
                draw_text(SCREEN, self.banner_text, FONT_LARGE, YELLOW, (SCREEN_WIDTH // 2, 275))
            draw_text(SCREEN, "SPACE: shoot   |   ESC: pause/menu", FONT_TINY, DIM, (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 15), shadow=False)
        elif self.state == "GAME_OVER":
            draw_text(SCREEN, "GAME OVER", FONT_HUGE, RED, (SCREEN_WIDTH // 2, 185))
            draw_text(SCREEN, f"Final score: {self.score}    Level: {self.level}", FONT_MED, WHITE, (SCREEN_WIDTH // 2, 260))
            draw_text(SCREEN, "Enter your name (max 10 chars):", FONT_SMALL, CYAN, (SCREEN_WIDTH // 2, 330))
            draw_text(SCREEN, self.player_name + "_", FONT_LARGE, YELLOW, (SCREEN_WIDTH // 2, 380))
            draw_text(SCREEN, "ENTER: save score    ESC: leaderboard", FONT_SMALL, DIM, (SCREEN_WIDTH // 2, 450))
        elif self.state == "LEADERBOARD":
            draw_text(SCREEN, "TOP SCORES", FONT_HUGE, YELLOW, (SCREEN_WIDTH // 2, 115))
            scores = load_high_scores()
            if not scores:
                draw_text(SCREEN, "No scores yet — be the first!", FONT_MED, WHITE, (SCREEN_WIDTH // 2, 210))
            for i, (name, score) in enumerate(scores):
                color = YELLOW if i == 0 else WHITE
                draw_text(SCREEN, f"{i + 1}. {name:<10}  {score}", FONT_MED, color, (SCREEN_WIDTH // 2, 205 + i * 48))
            draw_text(SCREEN, "ENTER: play again    ESC: main menu", FONT_SMALL, CYAN, (SCREEN_WIDTH // 2, 500))
        pygame.display.flip()

    def run(self):
        load_music()
        while True:
            CLOCK.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "PLAYING":
                            self.state = "MENU"
                        elif self.state in ("GAME_OVER", "LEADERBOARD"):
                            self.state = "LEADERBOARD"
                        else:
                            self.state = "MENU"
                    elif self.state == "MENU" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.state = "PLAYING"
                    elif self.state == "GAME_OVER":
                        if event.key == pygame.K_RETURN:
                            save_high_score(self.player_name, self.score)
                            self.state = "LEADERBOARD"
                        elif event.key == pygame.K_BACKSPACE:
                            self.player_name = self.player_name[:-1]
                        elif event.unicode.isalnum() or event.unicode == " ":
                            if len(self.player_name) < self.max_name_len:
                                self.player_name += event.unicode
                    elif self.state == "LEADERBOARD" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.reset_game()
                    elif self.state == "LEADERBOARD" and event.key == pygame.K_ESCAPE:
                        self.state = "MENU"

            if self.state in ("PLAYING", "MENU", "GAME_OVER", "LEADERBOARD"):
                self.update()
            self.draw()

if __name__ == "__main__":
    Game().run()
