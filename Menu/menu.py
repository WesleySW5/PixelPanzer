import pygame
import sys
import subprocess
import os# To launch the game script

game_path = os.path.join(os.path.dirname(__file__), "..", "Project", "project_version8.py")

# Run the game


# Initialize pygame
pygame.init()

pygame.mixer.init()  # Initialize sound mixer
pygame.mixer.music.load("MainMenu.wav")  # Load the music file
pygame.mixer.music.set_volume(0.3)  # Set volume (0.0 to 1.0)
pygame.mixer.music.play(-1)  # Play the music on loop (-1 means infinite loop)


# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
DARK_GRAY = (50, 50, 50)

# Set up screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PixelPanzer - Main Menu")

# Load background (optional, if you want the same background)
background = pygame.image.load("menuBackground.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Fonts
font = pygame.font.Font(None, 35)


def draw_button(text, color, rect):
    pygame.draw.rect(screen, color, rect, border_radius=10)
    pygame.draw.rect(screen, DARK_GRAY, rect, 3)  # Border
    text_surface = font.render(text, True, WHITE)
    screen.blit(text_surface, (rect.x + 20, rect.y + 10))

def main_menu():
    running = True
    while running:
        screen.blit(background, (0, 0))  # Draw the background

        # Define buttons
        start_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 60)
        exit_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 60)

        # Draw buttons
        draw_button("Start Game", GREEN, start_button)
        draw_button("Exit", RED, exit_button)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    pygame.mixer.music.stop()
                    subprocess.run(["python", game_path])  # Run the game file
                    running = False
                if exit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

if __name__ == "__main__":
    main_menu()
