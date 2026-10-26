import pygame
import random
import sys
import os

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Math Space Shooter with Leaderboard")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
GRAY = (100, 100, 100)
DARK_GRAY = (40, 40, 40)
GOLD = (255, 215, 0)

# Fonts
font_large = pygame.font.SysFont("arial", 40)
font_medium = pygame.font.SysFont("arial", 32)
font_small = pygame.font.SysFont("arial", 24)

# Clock to control frame rate
clock = pygame.time.Clock()
FPS = 60

# --- File System for High Scores ---
SCORE_FILE = "highscores.txt"

def load_high_scores():
    """Loads all scores from a local file, ensuring unique names."""
    scores_dict = {}
    if os.path.exists(SCORE_FILE):
        try:
            with open(SCORE_FILE, "r") as f:
                for line in f:
                    parts = line.strip().split(",")
                    if len(parts) == 2:
                        name = parts[0].strip()
                        score = int(parts[1].strip())
                        if name in scores_dict:
                            if score > scores_dict[name]:
                                scores_dict[name] = score
                        else:
                            scores_dict[name] = score
        except Exception:
            pass
            
    sorted_scores = sorted(scores_dict.items(), key=lambda x: x[1], reverse=True)
    return sorted_scores[:5]

def save_high_score(name, new_score):
    """Saves score while enforcing that a name cannot be entered twice."""
    scores_dict = {}
    if os.path.exists(SCORE_FILE):
        try:
            with open(SCORE_FILE, "r") as f:
                for line in f:
                    parts = line.strip().split(",")
                    if len(parts) == 2:
                        scores_dict[parts[0].strip()] = int(parts[1].strip())
        except Exception:
            pass

    if name in scores_dict:
        if new_score > scores_dict[name]:
            scores_dict[name] = new_score
    else:
        scores_dict[name] = new_score

    sorted_scores = sorted(scores_dict.items(), key=lambda x: x[1], reverse=True)
    
    try:
        with open(SCORE_FILE, "w") as f:
            for n, s in sorted_scores:
                f.write(f"{n},{s}\n")
    except Exception:
        pass

class StarField:
    def __init__(self):
        self.stars = []
        for _ in range(50):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            speed = random.uniform(1.0, 4.0)
            self.stars.append([x, y, speed])

    def update(self):
        for star in self.stars:
            star[1] += star[2]
            if star[1] > SCREEN_HEIGHT:
                star[1] = 0
                star[0] = random.randint(0, SCREEN_WIDTH)

    def draw(self, surface):
        for star in self.stars:
            size = 2 if star[2] < 2.5 else 3
            pygame.draw.circle(surface, GRAY, (int(star[0]), int(star[1])), size)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, CYAN, [(25, 0), (0, 40), (50, 40)])
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 20
        self.speed = 6

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((6, 15))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -10

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

class Target(pygame.sprite.Sprite):
    def __init__(self, x, y, value):
        super().__init__()
        self.value = value
        self.image = pygame.Surface((80, 50), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, RED, [0, 0, 80, 50])
        
        text_surf = font_small.render(str(self.value), True, WHITE)
        text_rect = text_surf.get_rect(center=(40, 25))
        self.image.blit(text_surf, text_rect)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 1.5

    def update(self):
        self.rect.y += self.speed

class GameController:
    def __init__(self):
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.targets = pygame.sprite.Group()
        
        self.player = Player()
        self.all_sprites.add(self.player)
        
        self.starfield = StarField()
        
        self.score = 0
        self.lives = 3
        self.state = "PLAYING"
        self.running = True
        
        self.player_name = ""
        self.max_name_len = 10
        
        self.current_question = ""
        self.correct_answer = 0
        self.generate_math_problem()

    def generate_math_problem(self):
        for target in self.targets:
            target.kill()
            
        num1 = random.randint(1, 12)
        num2 = random.randint(1, 12)
        operation = random.choice(['+', '-', '*'])
        
        if operation == '+':
            self.correct_answer = num1 + num2
        elif operation == '-':
            if num1 < num2: num1, num2 = num2, num1
            self.correct_answer = num1 - num2
        else:
            self.correct_answer = num1 * num2
            
        self.current_question = f"{num1} {operation} {num2} = ?"
        
        options = [self.correct_answer]
        while len(options) < 3:
            wrong = self.correct_answer + random.randint(-10, 10)
            if wrong != self.correct_answer and wrong not in options and wrong >= 0:
                options.append(wrong)
        random.shuffle(options)
        
        x_positions = [150, 360, 570]
        for i, val in enumerate(options):
            target = Target(x_positions[i], -60, val)
            self.targets.add(target)
            self.all_sprites.add(target)

    def run(self):
        while self.running:
            self.handle_events()
            
            if self.state == "PLAYING":
                self.update_logic()
                self.draw_screen()
            elif self.state == "INPUT_NAME":
                self.draw_name_input_screen()
            elif self.state == "LEADERBOARD":
                self.draw_leaderboard_screen()
                
            clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                if self.state == "PLAYING":
                    if event.key == pygame.K_SPACE:
                        bullet = Bullet(self.player.rect.centerx, self.player.rect.top)
                        self.bullets.add(bullet)
                        self.all_sprites.add(bullet)
                        
                elif self.state == "INPUT_NAME":
                    if event.key == pygame.K_RETURN:
                        if self.player_name.strip() == "":
                            self.player_name = "Player1"
                        save_high_score(self.player_name.strip(), self.score)
                        self.state = "LEADERBOARD"
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    else:
                        if len(self.player_name) < self.max_name_len:
                            if event.unicode.isalnum() or event.unicode == ' ':
                                self.player_name += event.unicode
                                
                elif self.state == "LEADERBOARD":
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.__init__()
                        self.state = "PLAYING"

    def update_logic(self):
        self.starfield.update()
        self.all_sprites.update()
        
        hits = pygame.sprite.groupcollide(self.bullets, self.targets, True, False)
        for bullet, hit_targets in hits.items():
            for target in hit_targets:
                if target.value == self.correct_answer:
                    self.score += 10
                    target.kill()
                    self.generate_math_problem()
                    break 
                else:
                    target.kill()
                    self.lives -= 1
                    if self.lives <= 0:
                        self.state = "INPUT_NAME"
                    else:
                        self.generate_math_problem()
                    break

        for target in self.targets:
            if target.rect.top > SCREEN_HEIGHT or pygame.sprite.collide_rect(self.player, target):
                self.lives -= 1
                if self.lives <= 0:
                    self.state = "INPUT_NAME"
                else:
                    self.generate_math_problem()
                break

    def draw_screen(self):
        screen.fill(BLACK)
        self.starfield.draw(screen)
        self.all_sprites.draw(screen)
        
        q_surf = font_large.render(self.current_question, True, WHITE)
        screen.blit(q_surf, (20, 20))
        
        score_surf = font_medium.render(f"Score: {self.score}", True, GREEN)
        screen.blit(score_surf, (SCREEN_WIDTH - 200, 20))
        lives_surf = font_medium.render(f"Lives: {self.lives}", True, RED)
        screen.blit(lives_surf, (SCREEN_WIDTH - 200, 60))
        pygame.display.flip()

    def draw_name_input_screen(self):
        screen.fill(BLACK)
        self.starfield.update()
        self.starfield.draw(screen)
        menu_rect = pygame.Rect(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        pygame.draw.rect(screen, DARK_GRAY, menu_rect, border_radius=15)
        pygame.draw.rect(screen, CYAN, menu_rect, width=3, border_radius=15)
        title_surf = font_large.render("GAME OVER", True, RED)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 40))
        screen.blit(title_surf, title_rect)
        final_score_surf = font_medium.render(f"Final Score: {self.score}", True, YELLOW)
        final_score_rect = final_score_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 90))
        screen.blit(final_score_surf, final_score_rect)
        prompt_surf = font_small.render("Enter Name:", True, WHITE)
        prompt_rect = prompt_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        screen.blit(prompt_surf, prompt_rect)
        name_surf = font_medium.render(self.player_name + "_", True, CYAN)
        name_rect = name_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(name_surf, name_rect)
        sub_surf = font_small.render("Press Enter to Confirm", True, GRAY)
        sub_rect = sub_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 110))
        screen.blit(sub_surf, sub_rect)
        pygame.display.flip()

    def draw_leaderboard_screen(self):
        screen.fill(BLACK)
        self.starfield.update()
        self.starfield.draw(screen)
        lead_rect = pygame.Rect(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 6, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3)
        pygame.draw.rect(screen, DARK_GRAY, lead_rect, border_radius=15)
        pygame.draw.rect(screen, GOLD, lead_rect, width=3, border_radius=15)
        title_surf = font_large.render("TOP SCORES", True, GOLD)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 6 + 40))
        screen.blit(title_surf, title_rect)
        high_progs = load_high_scores()
        start_y = SCREEN_HEIGHT // 6 + 110
        for i, (name, score) in enumerate(high_progs):
            rank_str = f"{i+1}. {name.ljust(12)} {score}"
            color = GOLD if i == 0 else WHITE
            entry_surf = font_small.render(rank_str, True, color)
            entry_rect = entry_surf.get_rect(topleft=(SCREEN_WIDTH // 4 + 50, start_y + (i * 40)))
            screen.blit(entry_surf, entry_rect)
        reset_surf = font_small.render("Press SPACE / ENTER to Play Again", True, CYAN)
        reset_rect = reset_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 5 // 6 - 30))
        screen.blit(reset_surf, reset_rect)
        pygame.display.flip()

if __name__ == "__main__":
    game = GameController()
    game.run()
