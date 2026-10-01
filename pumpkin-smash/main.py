##########################################################################################
##Filename: main.py
##Author: Kyle McColgan
##Date: 1 October 2026
##Description: This file contains the main game file for the pumpkin smash game.
##########################################################################################

import math
import random
import sys

import pygame

##########################################################################################

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

INITIAL_PUMPKIN_SPEED = 5.0
SPEED_INCREMENT = 0.1

SECOND_PUMPKIN_SCORE = 20
THIRD_PUMPKIN_SCORE = 30

GHOST_SPEED = 4.0
GHOST_SIZE = (100, 120)

MESSAGE_DURATION = 900
MESSAGE_FADE_SPEED = 5

SKY_TOP = (45, 68, 92)
SKY_BOTTOM = (218, 126, 66)

GROUND_TOP = (55, 67, 47)
GROUND_BOTTOM = (28, 37, 29)

WHITE = (255, 255, 255)
MUTED_WHITE = (232, 235, 231)

SHADOW = (12, 16, 14)
DANGER = (255, 104, 91)

##########################################################################################

def quit_game():
    pygame.quit()
    sys.exit()

def spawn_entity(image):
    """Create a new entity rectangle at a random position above the screen."""
    rect = image.get_rect()
    x = random.randint(0, SCREEN_WIDTH - rect.width)
    y = random.randint(-rect.height - 40, -10)
    rect.topleft = (x, y)
    return rect

def create_gradient(top_color, bottom_color):
    """Create a reusable vertical gradient surface."""
    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    for y in range(SCREEN_HEIGHT):
        blend = y / (SCREEN_HEIGHT - 1)
        color = tuple(int(top_color[channel] * (1 - blend) + bottom_color[channel] * blend) for channel in range(3))
        pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y))

    return surface

def render_text_with_shadow(screen, font, text, position, color=WHITE, shadow_color=SHADOW, shadow_offset=(2,2)):
    """Render readable text with a subtle shadow."""
    shadow = font.render(text, True, shadow_color)
    foreground = font.render(text, True, color)

    screen.blit(shadow, (position[0] + shadow_offset[0], position[1] + shadow_offset[1]))
    screen.blit(foreground, position)

def main():
    #Initalize Pygame.
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("🎃 Pumpkin Smash")
    clock = pygame.time.Clock()

    #Load assets...
    try:
        pumpkin_img = pygame.image.load("pumpkin-03.png").convert_alpha()
        explosion_imgs = [pygame.image.load(f"explosion-{index}.png").convert_alpha() for index in range (1,3)]
        ghost_img = pygame.image.load("ghost.webp").convert_alpha()
        ghost_img = pygame.transform.scale(ghost_img, GHOST_SIZE)
    except pygame.error as error:
        print(f"Error loading image: {error}")
        quit_game()

    #Fonts.
    score_font = pygame.font.Font(None, 42)
    message_font = pygame.font.Font(None, 48)
    game_over_font = pygame.font.Font(None, 58)
    subtitle_font = pygame.font.Font(None, 30)

    background = create_gradient(SKY_TOP, SKY_BOTTOM)
    ground = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT // 2))

    for y in range(ground.get_height()):
        blend = y / (ground.get_height() - 1)
        color = tuple(int(GROUND_TOP[channel] * (1 - blend) + GROUND_BOTTOM[channel] * blend) for channel in range(3))
        pygame.draw.line(ground, color, (0, y), (SCREEN_WIDTH, y))

    #Game State Variables...
    score = 0
    pumpkin_speed = INITIAL_PUMPKIN_SPEED
    pumpkins = [spawn_entity(pumpkin_img)]
    explosions = []

    ghost_rect = spawn_entity(ghost_img)
    ghost_speed = GHOST_SPEED
    ghost_base_x = ghost_rect.x

    game_over = False

    message_text = None
    message_color = WHITE
    message_alpha = 0
    message_timer = 0

    running = True
    #Main game loop...
    while running:
        delta_time = clock.tick(FPS)
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()

            if (event.type == pygame.MOUSEBUTTONDOWN and not game_over):
                """Ghost collision takes priority."""
                if ghost_rect.collidepoint(event.pos):
                    game_over = True
                    message_text = "👻 You clicked the ghost! Game over!"
                    message_color = DANGER
                    message_alpha = 255
                    message_timer = MESSAGE_DURATION
                    continue

                #Check the pumpkins...
                for pumpkin_rect in pumpkins:
                    if pumpkin_rect.collidepoint(event.pos):
                        score += 1
                        explosions.append({"rect": pumpkin_rect.copy(), "frame": 0, "alpha": 255})
                        pumpkin_rect.topleft = (random.randint(0, SCREEN_WIDTH - pumpkin_rect.width), random.randint(-pumpkin_rect.height * 2, -pumpkin_rect.height))
                        pumpkin_speed += SPEED_INCREMENT
                        message_text = "Nice!"
                        message_color = WHITE
                        message_alpha = 255
                        message_timer = MESSAGE_DURATION

                        break

        if not game_over:
            """Determine pumpkin count."""
            if score >= THIRD_PUMPKIN_SCORE:
                target_pumpkins = 3
            elif score >= SECOND_PUMPKIN_SCORE:
                target_pumpkins = 2
            else:
                target_pumpkins = 1

            while len(pumpkins) < target_pumpkins:
                pumpkins.append(spawn_entity(pumpkin_img))

            #Move pumpkins...
            for pumpkin_rect in pumpkins:
                pumpkin_rect.y += pumpkin_speed

                if pumpkin_rect.top > SCREEN_HEIGHT:
                    pumpkin_rect.topleft = (random.randint(0, SCREEN_WIDTH - pumpkin_rect.width), random.randint(-pumpkin_rect.height * 2, -pumpkin_rect.height))
                    pumpkin_speed += SPEED_INCREMENT
                    #score = 0
                    message_text = "Miss!"
                    message_color = DANGER
                    message_alpha = 255
                    message_timer = MESSAGE_DURATION

            """Move the ghost vertically."""
            ghost_rect.y += ghost_speed

            """Give the ghost a controlled floating motion."""
            ghost_rect.x = int(ghost_base_x + math.sin(current_time * 0.0025) * 45)
            ghost_rect.x = max(0, min(SCREEN_WIDTH - ghost_rect.width, ghost_rect.x))

            """Respawn the ghost."""
            if ghost_rect.top > SCREEN_HEIGHT:
                ghost_rect = spawn_entity(ghost_img)
                ghost_base_x = ghost_rect.x

        """Background."""
        screen.blit(background, (0, 0))

        #Ground begins around the horizon.
        ground_y = SCREEN_HEIGHT // 2
        screen.blit(ground, (0, ground_y))

        """Atmospheric Details."""
        horizon = pygame.Surface((SCREEN_WIDTH, 90), pygame.SRCALPHA)

        for y in range(90):
            alpha = int(38 * (1 - y / 90))

            pygame.draw.line(horizon, (255, 188, 102, alpha), (0, y), (SCREEN_WIDTH, y))
            screen.blit(horizon, (0, ground_y - 45))

        #Draw pumpkins...
        for pumpkin_rect in pumpkins:
            bob = int(math.sin((current_time + pumpkin_rect.x * 8) * 0.004) * 4)
            draw_rect = pumpkin_rect.copy()
            draw_rect.y += bob

            #Ground shadow.
            if draw_rect.bottom > ground_y:
                shadow_width = max(20, int(draw_rect.width * 0.55))
                shadow_height = max(8, int(draw_rect.height * 0.12))
                shadow_rect = pygame.Rect(draw_rect.centerx - shadow_width // 2, ground_y - shadow_height // 2, shadow_width, shadow_height)
                shadow_surface = pygame.Surface(shadow_rect.size, pygame.SRCALPHA)
                pygame.draw.ellipse(shadow_surface, (0, 0, 0, 85), shadow_surface.get_rect())
                screen.blit(shadow_surface, shadow_rect)

            screen.blit(pumpkin_img, draw_rect)

        #Draw the ghost (slight transparency).
        if not game_over:
            ghost_alpha = 190 + int(25 * math.sin(current_time * 0.003))
            ghost_surface = ghost_img.copy()
            ghost_surface.set_alpha(ghost_alpha)
            ghost_bob = int(math.sin(current_time * 0.004) * 5)
            screen.blit(ghost_surface, (ghost_rect.x, ghost_rect.y + ghost_bob))

        #Draw explosions ...
        active_explosions = []
        for explosion in explosions:
            frame = explosion["frame"]

            if frame < len(explosion_imgs):
                image = explosion_imgs[frame].copy()
                image.set_alpha(explosion["alpha"])
                screen.blit(image, explosion["rect"])
                explosion["frame"] += 1
                explosion["alpha"] -= 32
                active_explosions.append(explosion)
        explosions = active_explosions

        #Render the score ...
        score_text = f"SCORE {score:02d}"
        score_surface = score_font.render(score_text, True, WHITE)
        score_panel = pygame.Surface((score_surface.get_width() + 32, score_surface.get_height() + 18), pygame.SRCALPHA)
        pygame.draw.rect(score_panel, (16, 23, 27, 175), score_panel.get_rect(), border_radius=12)
        screen.blit(score_panel, (16, 16))
        screen.blit(score_surface, (32, 25))

        #Message fade...
        if message_text and message_alpha > 0:
            message_surface = message_font.render(message_text, True, message_color)
            message_surface.set_alpha(message_alpha)
            message_x = (SCREEN_WIDTH - message_surface.get_width()) // 2
            message_y = 120

            #Small shadow.
            shadow_surface = message_font.render(message_text, True, SHADOW)
            shadow_surface.set_alpha(max(0, message_alpha - 40))
            screen.blit(shadow_surface, (message_x + 2, message_y + 3))
            screen.blit(message_surface, (message_x, message_y))
            message_alpha = max(0, message_alpha - MESSAGE_FADE_SPEED)
            message_timer = max(0, message_timer - delta_time)

            if message_timer == 0:
                message_text = None

        #Game-over overlay....
        if game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((10, 14, 17, 190))
            screen.blit(overlay, (0, 0))
            title = game_over_font.render("👻 Game Over - Click X to Exit", True, WHITE)
            subtitle = subtitle_font.render(f"Final score {score:02d}", True, MUTED_WHITE)
            instruction = subtitle_font.render("Close the window to exit", True, (190, 198, 194))
            title_x = (SCREEN_WIDTH - title.get_width()) // 2
            subtitle_x = (SCREEN_WIDTH - subtitle.get_width()) // 2
            instruction_x = (SCREEN_WIDTH - instruction.get_width()) // 2
            screen.blit(title, (title_x, SCREEN_HEIGHT // 2 - 60))
            screen.blit(subtitle, (subtitle_x, SCREEN_HEIGHT // 2 + 5))
            screen.blit(instruction, (instruction_x, SCREEN_HEIGHT // 2 + 42))

        #Update the display...
        pygame.display.flip()

    quit_game()

if __name__ == "__main__":
    main()