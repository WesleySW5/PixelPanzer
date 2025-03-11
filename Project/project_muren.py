import pygame
import math
import random

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Tank settings
TANK_WIDTH, TANK_HEIGHT = 50, 30
BARREL_LENGTH = 35
BULLET_RADIUS = 5
BULLET_SPEED = 5
SHOOT_COOLDOWN = 500  # 500 milliseconds cooldown
MAX_BULLETS = 5  # Maximum bullets allowed on screen per tank

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tank Shooter")
clock = pygame.time.Clock()


class Tank:
    def __init__(self, x, y, color, keys):
        self.x = x
        self.y = y
        self.angle = 0  # Tank body rotation
        self.barrel_angle = 0  # Barrel rotation
        self.color = color
        self.speed = 3
        self.hit_count = 0  # Track number of hits
        self.keys = keys
        self.bullets = []
        self.last_shot_time = 0  # Track last shot time

    def move(self, keys_pressed):
        if keys_pressed[self.keys['left']]:
            self.angle -= 2
        if keys_pressed[self.keys['right']]:
            self.angle += 2
        if keys_pressed[self.keys['up']]:
            self.x += self.speed * math.cos(math.radians(self.angle))
            self.y += self.speed * math.sin(math.radians(self.angle))
        if keys_pressed[self.keys['down']]:
            self.x -= self.speed * math.cos(math.radians(self.angle))
            self.y -= self.speed * math.sin(math.radians(self.angle))
        if keys_pressed[self.keys['rotate_left']]:
            self.barrel_angle -= 2
        if keys_pressed[self.keys['rotate_right']]:
            self.barrel_angle += 2

    def shoot(self, keys_pressed):
        current_time = pygame.time.get_ticks()
        if keys_pressed[self.keys['shoot']] and current_time - self.last_shot_time > SHOOT_COOLDOWN and len(
                self.bullets) < MAX_BULLETS:
            bullet_x = self.x + (BARREL_LENGTH * math.cos(math.radians(self.barrel_angle)))
            bullet_y = self.y + (BARREL_LENGTH * math.sin(math.radians(self.barrel_angle)))
            bullet_dx = BULLET_SPEED * math.cos(math.radians(self.barrel_angle))
            bullet_dy = BULLET_SPEED * math.sin(math.radians(self.barrel_angle))
            self.bullets.append([bullet_x, bullet_y, bullet_dx, bullet_dy])
            self.last_shot_time = current_time  # Update last shot time

    def draw(self):
        rotated_tank = pygame.Surface((TANK_WIDTH, TANK_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(rotated_tank, self.color, (0, 0, TANK_WIDTH, TANK_HEIGHT), border_radius=10)
        pygame.draw.rect(rotated_tank, BLACK, (5, 5, TANK_WIDTH - 10, TANK_HEIGHT - 10), 2)
        pygame.draw.rect(rotated_tank, BLACK, (0, 5, 5, TANK_HEIGHT - 10))
        pygame.draw.rect(rotated_tank, BLACK, (TANK_WIDTH - 5, 5, 5, TANK_HEIGHT - 10))
        rotated_tank = pygame.transform.rotate(rotated_tank, -self.angle)
        tank_rect = rotated_tank.get_rect(center=(self.x, self.y))
        screen.blit(rotated_tank, tank_rect.topleft)

        # Draw barrel
        barrel_start_x = self.x
        barrel_start_y = self.y
        barrel_end_x = barrel_start_x + (BARREL_LENGTH * math.cos(math.radians(self.barrel_angle)))
        barrel_end_y = barrel_start_y + (BARREL_LENGTH * math.sin(math.radians(self.barrel_angle)))
        pygame.draw.line(screen, BLACK, (barrel_start_x, barrel_start_y), (barrel_end_x, barrel_end_y), 7)

        # Draw bullets
        for bullet in self.bullets:
            pygame.draw.circle(screen, BLACK, (int(bullet[0]), int(bullet[1])), BULLET_RADIUS)

    def update_bullets(self, other_tank):
        for bullet in self.bullets[:]:
            bullet[0] += bullet[2]
            bullet[1] += bullet[3]
            # Check if bullet hits the other tank
            if self.is_hit(other_tank, bullet):
                other_tank.hit_count += 1  # Increment hit count instead of health
                self.bullets.remove(bullet)
            # Remove bullet if it goes off-screen
            elif bullet[0] < 0 or bullet[0] > WIDTH or bullet[1] < 0 or bullet[1] > HEIGHT:
                self.bullets.remove(bullet)

    def is_hit(self, other_tank, bullet):
        # Check if the bullet hits the other tank
        dist_x = bullet[0] - other_tank.x
        dist_y = bullet[1] - other_tank.y
        distance = math.sqrt(dist_x ** 2 + dist_y ** 2)
        # Check if the distance between the bullet and tank is smaller than the radius of the tank
        return distance < TANK_WIDTH / 2 + BULLET_RADIUS


def draw_retry_button():
    font = pygame.font.Font(None, 36)
    text = font.render("Retry", True, BLACK)
    button_rect = pygame.Rect(WIDTH // 2 - 60, HEIGHT // 2 + 50, 120, 50)
    pygame.draw.rect(screen, GREEN, button_rect)
    pygame.draw.rect(screen, BLACK, button_rect, 3)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + 60))
    return button_rect


def main():
    run = True
    tank1 = Tank(100, 300, RED, {'left': pygame.K_q, 'right': pygame.K_d, 'up': pygame.K_z, 'down': pygame.K_s,
                                 'rotate_left': pygame.K_a, 'rotate_right': pygame.K_e, 'shoot': pygame.K_SPACE})
    tank2 = Tank(600, 300, BLUE,
                 {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'up': pygame.K_UP, 'down': pygame.K_DOWN,
                  'rotate_left': pygame.K_KP4, 'rotate_right': pygame.K_KP6, 'shoot': pygame.K_RETURN})

    while run:
        clock.tick(60)
        screen.fill(WHITE)

        keys_pressed = pygame.key.get_pressed()

        tank1.move(keys_pressed)
        tank2.move(keys_pressed)

        tank1.shoot(keys_pressed)
        tank2.shoot(keys_pressed)

        tank1.update_bullets(tank2)
        tank2.update_bullets(tank1)

        tank1.draw()
        tank2.draw()

        if tank1.hit_count >= 5 or tank2.hit_count >= 5:
            font = pygame.font.Font(None, 74)
            text = font.render("Game Over", True, BLACK)
            screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2 - 50))

            retry_button_rect = draw_retry_button()
            pygame.display.update()

            # Wait for the player to click on the retry button
            retry_clicked = False
            while not retry_clicked:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                        retry_clicked = True
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if retry_button_rect.collidepoint(event.pos):
                            # Reset the game by creating new tank instances and resetting hit counts
                            tank1 = Tank(100, 300, RED, {'left': pygame.K_q, 'right': pygame.K_d, 'up': pygame.K_z,
                                                         'down': pygame.K_s, 'rotate_left': pygame.K_a,
                                                         'rotate_right': pygame.K_e, 'shoot': pygame.K_SPACE})
                            tank2 = Tank(600, 300, BLUE,
                                         {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'up': pygame.K_UP,
                                          'down': pygame.K_DOWN, 'rotate_left': pygame.K_KP4,
                                          'rotate_right': pygame.K_KP6, 'shoot': pygame.K_RETURN})
                            retry_clicked = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
