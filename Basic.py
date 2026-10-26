import os
import sys

# --- ENVIRONMENT OVERRIDE PATCH FOR PYTHON 3.14 LOCKUPS ---
# Force Thonny's backend shell pipeline to handle the graphics window separately
os.environ['SDL_VIDEO_WINDOW_POS'] = "center"
if sys.platform.startswith('win'):
    os.environ['SDL_VIDEODRIVER'] = 'windib'

import pygame
import random

# --- INITIALIZATION ---
pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Math Cosmic Defender")
clock = pygame.time.Clock()

# --- COLORS ---
BLACK = (0, 0, 10)
WHITE = (255, 255, 255)
GREEN = (0, 255, 100)
RED = (255, 50, 50)
YELLOW = (255, 220, 0)
CYAN = (0, 255, 255)

# --- GAME STATES ---
current_state = "START_MENU"

# --- GAME VARIABLES ---
player_name = ""
score = 0
player_health = 100
player_x = WIDTH // 2

# Math Variables
current_question = ""
correct_answer = 0
player_input = ""

# Game Objects
asteroids = []
lasers = []
explosions = []

# Leaderboard data (Friends only - no bots)
leaderboard = [
    {"name": "Rahul", "score": 120},
    {"name": "Sanjay", "score": 90},
    {"name": "Arjun", "score": 70}
]

# --- UTILITY FUNCTIONS ---
def get_font(size):
    return pygame.font.SysFont("monospace", size, bold=True)

def generate_question():
    """Generates a unique math problem and its numeric answer."""
    num1 = random.randint(2, 12)
    num2 = random.randint(2, 12)
    operator = random.choice(['+', '-', '*'])
    
    question_str = f"{num1} {operator} {num2}"
    answer = eval(question_str)
    return question_str, answer

# Initialize the first question
current_question, correct_answer = generate_question()

def spawn_asteroid():
    """Spawns an asteroid at a random top location."""
    x = random.randint(50, WIDTH - 50)
    y = random.randint(-100, -40)
    speed = random.uniform(1.0, 2.5)
    size = random.randint(20, 40)
    asteroids.append({"x": x, "y": y, "speed": speed, "size": size})

def update_leaderboard(name, final_score):
    """Adds a real friend score and sorts the leaderboard."""
    global leaderboard
    if name.strip() == "":
        name = "Player"
    leaderboard.append({"name": name, "score": final_score})
    leaderboard = sorted(leaderboard, key=lambda i: i['score'], reverse=True)
    leaderboard = leaderboard[:5]

# --- MAIN RUNNING ENGINE ---
running = True
while running:
    # Crucial: Forces OS window heartbeat communications synchronously 
    pygame.event.pump() 
    
    # Set target framerate 
    clock.tick(60)
    
    # 1. EVENT HANDLING LOOP
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif current_state == "START_MENU":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if len(player_name.strip()) > 0:
                        score = 0
                        player_health = 100
                        asteroids.clear()
                        lasers.clear()
                        explosions.clear()
                        player_input = ""
                        current_question, correct_answer = generate_question()
                        current_state = "GAMEPLAY"
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    if len(player_name) < 12 and event.unicode.isalnum():
                        player_name += event.unicode
                        
        elif current_state == "GAMEPLAY":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    try:
                        if int(player_input) == correct_answer:
                            score += 10
                            lasers.append({"x": player_x, "y": HEIGHT - 60})
                            current_question, correct_answer = generate_question()
                        else:
                            player_health -= 10
                    except ValueError:
                        pass
                    player_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    player_input = player_input[:-1]
                else:
                    if event.unicode in "0123456789-":
                        player_input += event.unicode
                        
        elif current_state == "GAME_OVER":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    current_state = "START_MENU"

    # 2. STATE LOGIC AND POSITION UPDATES
    if current_state == "GAMEPLAY":
        mouse_x, _ = pygame.mouse.get_pos()
        player_x = max(40, min(WIDTH - 40, mouse_x))
        
        if random.random() < 0.02 and len(asteroids) < 6:
            spawn_asteroid()
            
        for asteroid in asteroids[:]:
            asteroid["y"] += asteroid["speed"]
            if asteroid["y"] > HEIGHT - 50:
                player_health -= 15
                asteroids.remove(asteroid)
                
        for laser in lasers[:]:
            laser["y"] -= 12
            if laser["y"] < 0:
                lasers.remove(laser)
                
        for laser in lasers[:]:
            for asteroid in asteroids[:]:
                distance = ((laser["x"] - asteroid["x"])**2 + (laser["y"] - asteroid["y"])**2)**0.5
                if distance < asteroid["size"] + 5:
                    if laser in lasers:
                        lasers.remove(laser)
                    explosions.append({"x": asteroid["x"], "y": asteroid["y"], "duration": 15})
                    asteroids.remove(asteroid)
                    break
                    
        for exp in explosions[:]:
            exp["duration"] -= 1
            if exp["duration"] <= 0:
                explosions.remove(exp)
                
        if player_health <= 0:
            player_health = 0
            update_leaderboard(player_name, score)
            current_state = "GAME_OVER"

    # 3. GRAPHICS RENDERING
    screen.fill(BLACK)
    
    if current_state == "START_MENU":
        title_text = get_font(42).render("MATH COSMIC DEFENDER", True, CYAN)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 80))
        
        prompt_text = get_font(20).render("Enter Pilot Name to Start:", True, WHITE)
        screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, 220))
        
        name_surface = get_font(28).render(player_name + "_", True, YELLOW)
        screen.blit(name_surface, (WIDTH // 2 - name_surface.get_width() // 2, 260))
        
        info_text = get_font(16).render("Press ENTER to Launch Mission", True, GREEN)
        screen.blit(info_text, (WIDTH // 2 - info_text.get_width() // 2, 340))
        
    elif current_state == "GAMEPLAY":
        pygame.draw.polygon(screen, CYAN, [
            (player_x, HEIGHT - 65), 
            (player_x - 20, HEIGHT - 35), 
            (player_x + 20, HEIGHT - 35)
        ])
        
        for asteroid in asteroids:
            pygame.draw.circle(screen, RED, (int(asteroid["x"]), int(asteroid["y"])), asteroid["size"])
            
        for laser in lasers:
            pygame.draw.line(screen, GREEN, (laser["x"], laser["y"]), (laser["x"], laser["y"] - 15), 4)
            
        for exp in explosions:
            pygame.draw.circle(screen, YELLOW, (int(exp["x"]), int(exp["y"])), 35, 3)
            
        pygame.draw.rect(screen, (20, 20, 40), (0, 0, WIDTH, 75))
        pygame.draw.line(screen, CYAN, (0, 75), (WIDTH, 75), 2)
        
        question_surface = get_font(26).render(f"SOLVE: {current_question} = ", True, YELLOW)
        screen.blit(question_surface, (30, 22))
        
        input_surface = get_font(26).render(player_input + "_", True, WHITE)
        screen.blit(input_surface, (30 + question_surface.get_width(), 22))
        
        score_surface = get_font(20).render(f"SCORE: {score}", True, GREEN)
        screen.blit(score_surface, (WIDTH - 180, 15))
        
        health_surface = get_font(20).render(f"SHIELDS: {player_health}%", True, RED if player_health <= 30 else WHITE)
        screen.blit(health_surface, (WIDTH - 180, 40))
        
    elif current_state == "GAME_OVER":
        go_title = get_font(46).render("MISSION FAILED", True, RED)
        screen.blit(go_title, (WIDTH // 2 - go_title.get_width() // 2, 50))
        
        score_title = get_font(24).render(f"Your Score: {score}", True, WHITE)
        screen.blit(score_title, (WIDTH // 2 - score_title.get_width() // 2, 120))
        
        box_y = 190
        pygame.draw.rect(screen, (15, 15, 35), (WIDTH // 2 - 175, box_y, 350, 250))
        pygame.draw.rect(screen, CYAN, (WIDTH // 2 - 175, box_y, 350, 250), 2)
        
        lead_header = get_font(22).render("COSMIC LEADERBOARD", True, CYAN)
        screen.blit(lead_header, (WIDTH // 2 - lead_header.get_width() // 2, box_y + 15))
        
        for index, row in enumerate(leaderboard):
            row_text = f"{index + 1}. {row['name']:<12} {row['score']:>5}"
            row_surface = get_font(18).render(row_text, True, YELLOW if row['name'] == player_name else WHITE)
            screen.blit(row_surface, (WIDTH // 2 - 140, box_y + 60 + (index * 32)))
            
        restart_text = get_font(18).render("Press 'R' Key to Return to Main Menu", True, GREEN)
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, 480))

    pygame.display.flip()

# --- FORCE DESTRUCTION ---
pygame.quit()
sys.exit(0)
