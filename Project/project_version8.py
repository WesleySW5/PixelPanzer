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
MAIN_SOUND = os.path.join(ASSETS_DIR, "main.wav")  # Geluid bestand voor achtergrondmuziek
ENGINE_SOUND = os.path.join(ASSETS_DIR, "engine.wav")  # Geluid bestand voor engine

# Load bullet images
BLUE_BULLET_IMAGE = pygame.image.load(os.path.join(ASSETS_DIR, "blue_raket.png"))
RED_BULLET_IMAGE = pygame.image.load(os.path.join(ASSETS_DIR, "red_raket.png"))

# Draai de blauwe raket afbeelding 180°
BLUE_BULLET_IMAGE = pygame.transform.rotate(BLUE_BULLET_IMAGE, 180)

# Schaal de raketten kleiner (bijvoorbeeld 20x10)
BLUE_BULLET_IMAGE = pygame.transform.scale(BLUE_BULLET_IMAGE, (20, 10))
RED_BULLET_IMAGE = pygame.transform.scale(RED_BULLET_IMAGE, (20, 10))

TANK_WIDTH, TANK_HEIGHT = 50, 50
BLUE_TANK_IMAGE = pygame.transform.scale(BLUE_TANK_IMAGE, (TANK_WIDTH, TANK_HEIGHT))
RED_TANK_IMAGE = pygame.transform.scale(RED_TANK_IMAGE, (TANK_WIDTH, TANK_HEIGHT))

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tank Shooter")
clock = pygame.time.Clock()

# Laad en speel achtergrond muziek af
pygame.mixer.music.load(MAIN_SOUND)
pygame.mixer.music.set_volume(0.3)  # Zet het volume naar 50%
pygame.mixer.music.play(-1, 0)  # Zet de muziek op repeat (-1) vanaf het begin (0.0)

# Laad het engine geluid
engine_sound = pygame.mixer.Sound(ENGINE_SOUND)

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
        self.is_moving = False  # Houdt bij of de tank beweegt om geluid af te spelen

    def move(self, keys_pressed, obstacles, other_tank):
        if keys_pressed[self.keys['left']]:
            self.angle -= 2
        if keys_pressed[self.keys['right']]:
            self.angle += 2
        
        direction = 1 if self.reverse_movement else 1
        new_x, new_y = self.x, self.y
        moving = False  # Controleer of de tank beweegt

        # Bereken nieuwe positie op basis van de ingedrukte toetsen
        if keys_pressed[self.keys['up']]:
            new_x += direction * self.speed * math.cos(math.radians(self.angle))
            new_y += direction * self.speed * math.sin(math.radians(self.angle))
            moving = True
        elif keys_pressed[self.keys['down']]:
            new_x -= direction * self.speed * math.cos(math.radians(self.angle))
            new_y -= direction * self.speed * math.sin(math.radians(self.angle))
            moving = True
        
        # Controleer op botsingen met obstakels
        tank_rect = pygame.Rect(new_x - TANK_WIDTH / 2, new_y - TANK_HEIGHT / 2, TANK_WIDTH, TANK_HEIGHT)
        for obstacle in obstacles:
            if tank_rect.colliderect(obstacle):
                return  # Stop met bewegen als er een botsing is

        # Controleer of de tanks elkaar niet overlappen
        other_tank_rect = pygame.Rect(other_tank.x - TANK_WIDTH / 2, other_tank.y - TANK_HEIGHT / 2, TANK_WIDTH, TANK_HEIGHT)
        if tank_rect.colliderect(other_tank_rect):
            return  # Stop met bewegen als de tanks elkaar raken
        
        # Als er geen botsing is, werk dan de positie bij
        self.x = max(TANK_WIDTH / 2, min(WIDTH - TANK_WIDTH / 2, new_x))
        self.y = max(TANK_HEIGHT / 2, min(HEIGHT - TANK_HEIGHT / 2, new_y))

        # Speel het engine geluid af als de tank beweegt
        if moving and not self.is_moving:
            engine_sound.play()  # Speel het geluid af wanneer de tank begint te bewegen
        if not moving and self.is_moving:
            engine_sound.stop()  # Stop het geluid als de tank stopt met bewegen

        self.is_moving = moving  # Update de status of de tank beweegt of niet

    def draw(self):
        rotated_image = pygame.transform.rotate(self.image, -self.angle)
        tank_rect = rotated_image.get_rect(center=(self.x, self.y))
        screen.blit(rotated_image, tank_rect.topleft)
    
    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > SHOOT_COOLDOWN and len(self.bullets) < MAX_BULLETS:
            # Start de raket net iets boven de tankloop
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
            
            # Teken de raket en laat deze meedraaien met de tank
            if self == tank1:  # Als het de rode tank is
                rotated_bullet = pygame.transform.rotate(RED_BULLET_IMAGE, -self.angle)
                screen.blit(rotated_bullet, (bullet[0] - rotated_bullet.get_width() / 2, bullet[1] - rotated_bullet.get_height() / 2))
            else:  # Als het de blauwe tank is
                rotated_bullet = pygame.transform.rotate(BLUE_BULLET_IMAGE, -self.angle)
                screen.blit(rotated_bullet, (bullet[0] - rotated_bullet.get_width() / 2, bullet[1] - rotated_bullet.get_height() / 2))

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

    # Voeg obstakels toe (bijvoorbeeld rechthoeken)
    obstacles = [
        pygame.Rect(300, 200, 100, 50),  # Obstakel 1
        pygame.Rect(700, 400, 100, 50),  # Obstakel 2
        pygame.Rect(500, 500, 150, 50)   # Obstakel 3
    ]

    while run:
        clock.tick(60)
        
        # Teken de achtergrond
        screen.fill(WHITE)  # Vervang dit eventueel door een achtergrondafbeelding
        screen.blit(BACKGROUND_IMAGE, (0, 0))  # Achtergrond afbeelding
        
        # Teken obstakels
        for obstacle in obstacles:
            pygame.draw.rect(screen, (0, 0, 0), obstacle)
        
        keys_pressed = pygame.key.get_pressed()

        if tank1.hit_count >= 3:
            draw_game_over("Blue Tank")
            break
        if tank2.hit_count >= 3:
            draw_game_over("Red Tank")
            break
        
        # Beweeg de tanks en controleer botsingen met obstakels en andere tanks
        tank1.move(keys_pressed, obstacles, tank2)
        tank2.move(keys_pressed, obstacles, tank1)
        
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
