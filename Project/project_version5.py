import pygame
import math
import os

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1200, 700
WHITE = (255, 255, 255)
BULLET_RADIUS = 5
BULLET_SPEED = 5
SHOOT_COOLDOWN = 500
MAX_BULLETS = 5
GAME_OVER_FONT = pygame.font.Font(None, 74)
BUTTON_FONT = pygame.font.Font(None, 50)

# Load assets
ASSETS_DIR = "assets"
BLUE_TANK_IMAGE = pygame.image.load(os.path.join(ASSETS_DIR, "blue_tank.png"))
RED_TANK_IMAGE = pygame.image.load(os.path.join(ASSETS_DIR, "red_tank.png"))
BACKGROUND_IMAGE = pygame.image.load(os.path.join(ASSETS_DIR, "background.png"))

# Load sounds
pygame.mixer.music.load(os.path.join(ASSETS_DIR, "main.wav"))
pygame.mixer.music.play(-1, 0.0)  # Loop het geluid oneindig af

TANK_WIDTH, TANK_HEIGHT = 50, 50
BLUE_TANK_IMAGE = pygame.transform.scale(BLUE_TANK_IMAGE, (TANK_WIDTH, TANK_HEIGHT))
RED_TANK_IMAGE = pygame.transform.scale(RED_TANK_IMAGE, (TANK_WIDTH, TANK_HEIGHT))

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tank Shooter")
clock = pygame.time.Clock()

# Obstacles list (x, y, width, height)
obstacles = [
    pygame.Rect(300, 200, 200, 50),
    pygame.Rect(600, 400, 200, 50),
    pygame.Rect(900, 100, 100, 200)
]

class Tank:
    def __init__(self, x, y, angle, image, keys, reverse_movement=False):
        self.x = x
        self.y = y
        self.angle = angle
        self.image = image
        self.speed = 3
        self.hit_count = 0
        self.keys = keys
        self.bullets = []
        self.last_shot_time = 0
        self.reverse_movement = reverse_movement

    def move(self, keys_pressed):
        if keys_pressed[self.keys['left']]:
            self.angle -= 2
        if keys_pressed[self.keys['right']]:
            self.angle += 2
    
        direction = 1 if self.reverse_movement else 1
    
    # Beperk de beweging tot als de toetsen 'up' of 'down' zijn ingedrukt
        if keys_pressed[self.keys['up']]:
            self.x += direction * self.speed * math.cos(math.radians(self.angle))
            self.y += direction * self.speed * math.sin(math.radians(self.angle))
        elif keys_pressed[self.keys['down']]:
            self.x -= direction * self.speed * math.cos(math.radians(self.angle))
            self.y -= direction * self.speed * math.sin(math.radians(self.angle))
    
    # Boundaries for the tank (not outside the screen)
        self.x = max(TANK_WIDTH / 2, min(WIDTH - TANK_WIDTH / 2, self.x))
        self.y = max(TANK_HEIGHT / 2, min(HEIGHT - TANK_HEIGHT / 2, self.y))

    
    def draw(self):
        rotated_image = pygame.transform.rotate(self.image, -self.angle)
        tank_rect = rotated_image.get_rect(center=(self.x, self.y))
        screen.blit(rotated_image, tank_rect.topleft)
    
    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > SHOOT_COOLDOWN and len(self.bullets) < MAX_BULLETS:
            barrel_x = self.x + (TANK_WIDTH // 2) * math.cos(math.radians(self.angle))
            barrel_y = self.y + (TANK_HEIGHT // 2) * math.sin(math.radians(self.angle))
            bullet_dx = BULLET_SPEED * math.cos(math.radians(self.angle))
            bullet_dy = BULLET_SPEED * math.sin(math.radians(self.angle))
            self.bullets.append([barrel_x, barrel_y, bullet_dx, bullet_dy])
            self.last_shot_time = current_time
    
    def update_bullets(self, opponent):
        for bullet in self.bullets[:]:
            bullet[0] += bullet[2]
            bullet[1] += bullet[3]
            if bullet[0] < 0 or bullet[0] > WIDTH or bullet[1] < 0 or bullet[1] > HEIGHT:
                self.bullets.remove(bullet)
            elif opponent.hitbox().collidepoint(bullet[0], bullet[1]):
                opponent.hit_count += 1
                self.bullets.remove(bullet)
            pygame.draw.circle(screen, (0, 0, 0), (int(bullet[0]), int(bullet[1])), BULLET_RADIUS)
    
    def hitbox(self):
        return pygame.Rect(self.x - TANK_WIDTH / 2, self.y - TANK_HEIGHT / 2, TANK_WIDTH, TANK_HEIGHT)

def draw_game_over(winner):
    screen.fill(WHITE)
    text = GAME_OVER_FONT.render(f"{winner} Wins!", True, (255, 0, 0))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 3))
    
    retry_button = pygame.Rect(WIDTH // 3, HEIGHT // 2, 200, 50)
    exit_button = pygame.Rect(2 * WIDTH // 3 - 100, HEIGHT // 2, 200, 50)
    
    pygame.draw.rect(screen, (0, 255, 0), retry_button)
    pygame.draw.rect(screen, (255, 0, 0), exit_button)
    
    retry_text = BUTTON_FONT.render("Retry", True, WHITE)
    exit_text = BUTTON_FONT.render("Exit", True, WHITE)
    
    screen.blit(retry_text, (retry_button.x + 50, retry_button.y + 10))
    screen.blit(exit_text, (exit_button.x + 70, exit_button.y + 10))
    
    pygame.display.update()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_button.collidepoint(event.pos):
                    main()
                if exit_button.collidepoint(event.pos):
                    pygame.quit()
                    exit()

def main():
    run = True
    tank1 = Tank(100, 350, 0, RED_TANK_IMAGE, {'left': pygame.K_q, 'right': pygame.K_d, 'up': pygame.K_z, 'down': pygame.K_s, 'shoot': pygame.K_SPACE}, reverse_movement=True)
    tank2 = Tank(1100, 350, 180, BLUE_TANK_IMAGE, {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'up': pygame.K_UP, 'down': pygame.K_DOWN, 'shoot': pygame.K_RETURN}, reverse_movement=True)
    
    while run:
        clock.tick(60)
        
        # Draw background
        screen.blit(BACKGROUND_IMAGE, (0, 0))
        
        # Draw obstacles
        for obstacle in obstacles:
            pygame.draw.rect(screen, (100, 100, 100), obstacle)  # Obstakels grijs tekenen
        
        keys_pressed = pygame.key.get_pressed()

        if tank1.hit_count >= 3:
            draw_game_over("Blue Tank")
            break
        if tank2.hit_count >= 3:
            draw_game_over("Red Tank")
            break
        
        tank1.move(keys_pressed)
        tank2.move(keys_pressed)
        
        if keys_pressed[tank1.keys['shoot']]:
            tank1.shoot()
        if keys_pressed[tank2.keys['shoot']]:
            tank2.shoot()
        
        tank1.update_bullets(tank2)
        tank2.update_bullets(tank1)
        tank1.draw()
        tank2.draw()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                run = False

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
