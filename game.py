import pygame
import random
import sys

# 1. CORE SYSTEM INITIALIZATION
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Math Cosmic Defender")
clock = pygame.time.Clock()

# Safe Web Assembly Fonts
font_small = pygame.font.Font(None, 28)
font_medium = pygame.font.Font(None, 38)
font_large = pygame.font.Font(None, 52)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
YELLOW = (255, 255, 0)
GREEN = (50, 255, 50)
BLUE = (50, 150, 255)

# 2. RANDOMIZED MATH LOGIC GENERATOR
def generate_question():
    operation = random.choice(["+", "-", "*"])
    if operation == "+":
        num1 = random.randint(1, 20)
        num2 = random.randint(1, 20)
        return str(num1) + " + " + str(num2) + " = ?", num1 + num2
    elif operation == "-":
        num1 = random.randint(10, 30)
        num2 = random.randint(1, 9)
        return str(num1) + " - " + str(num2) + " = ?", num1 - num2
    elif operation == "*":
        num1 = random.randint(2, 9)
        num2 = random.randint(2, 9)
        return str(num1) + " x " + str(num2) + " = ?", num1 * num2

# 3. OBJECT-ORIENTED ENTITIES
class Player:
    def __init__(self):
        self.width = 50
        self.height = 40
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 60
        self.speed = 8

    def draw(self):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed

class Bullet:
    def __init__(self, x, y):
        self.x = x + 22
        self.y = y
        self.speed = 12
        self.radius = 5

    def update(self):
        self.y -= self.speed

    def draw(self):
        pygame.draw.circle(screen, YELLOW, (self.x, self.y), self.radius)

class Enemy:
    def __init__(self, x_position, value):
        self.width = 60
        self.height = 40
        self.x = x_position
        self.y = -50
        self.speed = 2.0
        self.value = value

    def update(self):
        self.y += self.speed

    def draw(self):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
        val_text = font_small.render(str(self.value), True, WHITE)
        screen.blit(val_text, (self.x + (self.width // 2 - val_text.get_width() // 2), self.y + 10))

# 4. SYSTEM FLOW MANAGEMENT SETUP
current_state = "NAME_ENTRY"
player_name = ""
score = 0
lives = 3

player = None
bullets = []
enemies = []

current_question_text = ""
correct_answer = 0

session_high_scores = []

def spawn_math_wave(correct_val):
    enemies.clear()
    choices = [correct_val, correct_val + random.randint(1, 5), correct_val - random.randint(1, 4)]
    random.shuffle(choices)
    # FIXED: Lanes are explicitly set up so enemies do not overlap or error out
    lanes = [150, 370, 590]
    for i in range(3):
        enemies.append(Enemy(lanes[i], choices[i]))

# 5. MAIN LOOP
main_loop_running = True
while main_loop_running:
    clock.tick(60)
    screen.fill(BLACK)

    if current_state == "NAME_ENTRY":
        title_text = font_large.render("MATH COSMIC DEFENDER", True, BLUE)
        prompt_text = font_medium.render("Enter Player Name & Press Enter:", True, WHITE)
        name_text = font_large.render(player_name + "_", True, YELLOW)
        
        screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 60))
        screen.blit(prompt_text, (SCREEN_WIDTH//2 - prompt_text.get_width()//2, 180))
        screen.blit(name_text, (SCREEN_WIDTH//2 - name_text.get_width()//2, 250))
        
        lb_title = font_medium.render("SESSION TOP SCORES", True, GREEN)
        screen.blit(lb_title, (SCREEN_WIDTH//2 - lb_title.get_width()//2, 350))
        
        if not session_high_scores:
            no_score_text = font_small.render("No records yet! Be the first to play.", True, WHITE)
            screen.blit(no_score_text, (SCREEN_WIDTH//2 - no_score_text.get_width()//2, 410))
        else:
            for i, (name, s) in enumerate(session_high_scores[:5]):
                lb_entry = font_small.render(str(i+1) + ". " + str(name) + " ------- " + str(s) + " pts", True, WHITE)
                screen.blit(lb_entry, (SCREEN_WIDTH//2 - lb_entry.get_width()//2, 400 + (i * 28)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                main_loop_running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if player_name.strip() == "":
                        player_name = "PLAYER"
                    player = Player()
                    bullets = []
                    enemies = []
                    score = 0
                    lives = 3
                    current_question_text, correct_answer = generate_question()
                    spawn_math_wave(correct_answer)
                    current_state = "PLAYING"
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    if len(player_name) < 10 and event.unicode.isalnum():
                        player_name += event.unicode.upper()

    elif current_state == "PLAYING":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                main_loop_running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullets.append(Bullet(player.x, player.y))

        keys = pygame.key.get_pressed()
        player.move(keys)

        if len(enemies) == 0:
            current_question_text, correct_answer = generate_question()
            spawn_math_wave(correct_answer)

        for bullet in bullets[:]:
            bullet.update()
            if bullet.y < 0:
                bullets.remove(bullet)

        wave_passed = False
        for enemy in enemies[:]:
            enemy.update()
            
            if enemy.y > SCREEN_HEIGHT - 40:
                wave_passed = True
            
            if (player.x < enemy.x + enemy.width and player.x + player.width > enemy.x and
                player.y < enemy.y + enemy.height and player.y + player.height > enemy.y):
                wave_passed = True

            for bullet in bullets[:]:
                if (bullet.x > enemy.x and bullet.x < enemy.x + enemy.width and
                    bullet.y > enemy.y and bullet.y < enemy.y + enemy.height):
                    
                    if bullet in bullets:
                        bullets.remove(bullet)
                    
                    if enemy.value == correct_answer:
                        score += 10
                        enemies.clear()
                        break
                    else:
                        lives -= 1
                        if enemy in enemies:
                            enemies.remove(enemy)
                        if lives <= 0:
                            session_high_scores.append((player_name, score))
                            session_high_scores.sort(key=lambda x: x, reverse=True)
                            current_state = "GAME_OVER"
                        break

        if wave_passed:
            lives -= 1
            enemies.clear()
            if lives <= 0:
                session_high_scores.append((player_name, score))
                session_high_scores.sort(key=lambda x: x, reverse=True)
                current_state = "GAME_OVER"

        player.draw()
        for bullet in bullets: bullet.draw()
        for enemy in enemies: enemy.draw()

        pygame.draw.rect(screen, BLUE, (0, 0, SCREEN_WIDTH, 50))
        math_display = font_medium.render("TARGET: " + str(current_question_text), True, YELLOW)
        screen.blit(math_display, (SCREEN_WIDTH//2 - math_display.get_width()//2, 8))

        name_display = font_small.render("Pilot: " + str(player_name), True, GREEN)
        score_display = font_small.render("Score: " + str(score), True, WHITE)
        lives_display = font_small.render("Lives: " + str(lives), True, RED)
        
        screen.blit(name_display, (15, 65))
        screen.blit(score_display, (15, 95))
        screen.blit(lives_display, (SCREEN_WIDTH - 150, 65))

    elif current_state == "GAME_OVER":
        go_text = font_large.render("GAME OVER", True, RED)
        final_score_text = font_medium.render(str(player_name) + "'s Score: " + str(score), True, WHITE)
        restart_text = font_small.render("Press [R] to Try Again", True, YELLOW)
        quit_text = font_small.render("Press [Q] for New Player Name", True, YELLOW)
        
        screen.blit(go_text, (SCREEN_WIDTH//2 - go_text.get_width()//2, 50))
        screen.blit(final_score_text, (SCREEN_WIDTH//2 - final_score_text.get_width()//2, 110))
        screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, 170))
        screen.blit(quit_text, (SCREEN_WIDTH//2 - quit_text.get_width()//2, 205))
        
        lb_title = font_medium.render("HALL OF FAME", True, GREEN)
        screen.blit(lb_title, (SCREEN_WIDTH//2 - lb_title.get_width()//2, 270))
        
        for i, (name, s) in enumerate(session_high_scores[:5]):
            color = YELLOW if name == player_name and s == score else WHITE
            lb_entry = font_medium.render(str(i+1) + ". " + str(name) + " ....... " + str(s), True, color)
            screen.blit(lb_entry, (SCREEN_WIDTH//2 - lb_entry.get_width()//2, 320 + (i * 42)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                main_loop_running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    player = Player()
