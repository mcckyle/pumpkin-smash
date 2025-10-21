##########################################################################################
##Filename: main.py
##Author: Kyle McColgan
##Date: 19 October 2025
##Description: This file contains the main game file for the pumpkin smash game.
##########################################################################################

import pygame
import sys
import random
import math

##########################################################################################

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
INITIAL_PUMPKIN_SPEED = 5
SPEED_INCREMENT = 0.1
FPS = 60

##########################################################################################

def main():
    #Initalize Pygame.
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("🎃 Pumpkin Smash")
    clock = pygame.time.Clock()

    #Load assets...
    try:
        pumpkin_img = pygame.image.load('pumpkin-03.png').convert_alpha()
        explosion_imgs = [pygame.image.load(f'explosion-{i}.png').convert_alpha() for i in range (1,3)]
        ghost_img = pygame.image.load('ghost.webp').convert_alpha()
        ghost_img = pygame.transform.scale(ghost_img, (100, 120))
    except pygame.error as e:
        print(f"Error loading images: {e}")
        pygame.quit()
        sys.exit()

    #Font
    font = pygame.font.Font(None, 42)

    pumpkin_rect = pumpkin_img.get_rect()
    pumpkin_rect.topleft = (random.randint(0, SCREEN_WIDTH - pumpkin_rect.width), 0)

    def spawn_entity(img):
        """Return a new rect at a random x at top of the screen."""
        rect = img.get_rect()
        rect.topleft = (random.randint(0, SCREEN_WIDTH - pumpkin_rect.width), 0)
        return rect

    def draw_dynamic_gradient(screen, time):
        #A smoother gradient that changes hues slightly as the game progresses.
        top_color = (135, 206, 250)
        bottom_color = (255, 170, 60)
        hue_shift = int(30 * math.sin(time * 0.0003))
        for y in range(SCREEN_HEIGHT):
            blend = y / SCREEN_HEIGHT
            r = min(255, max(0, int(top_color[0] * (1 - blend) + bottom_color[0] * blend) + hue_shift))
            g = min(255, max(0, int(top_color[1] * (1 - blend) + bottom_color[1] * blend)))
            b = min(255, max(0, int(top_color[2] * (1 - blend) + bottom_color[2] * blend)))
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

    #Game State Variables...
    score = 0
    pumpkins = [spawn_entity(pumpkin_img)]
    pumpkin_speed = INITIAL_PUMPKIN_SPEED
    explosions = []
    message_text = None
    message_alpha = 0
    message_color = (255, 255, 255)
    ghost_rect = spawn_entity(ghost_img)
    ghost_speed = 4
    game_over = False

    #Main game loop...
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                if ghost_rect.collidepoint(event.pos):
                    game_over = True
                    message_text = "👻 You clicked the ghost! Game over!"
                    message_color = (255, 50, 50)
                    message_alpha = 255
                    continue

                #Check the pumpkins...
                for rect in pumpkins:
                    if rect.collidepoint(event.pos):
                        score += 1
                        explosions.append({"rect": rect.copy(), "frame": 0, "alpha": 255})
                        rect.topleft = (random.randint(0, SCREEN_WIDTH - rect.width), 0)
                        pumpkin_speed += SPEED_INCREMENT
                        message_text = "Nice!"
                        message_color = (255, 255, 255)
                        message_alpha = 255

        if not game_over:
            #Increase the pumpkin count by scroll thresholds...
            target_pumpkins = 1

            if score >= 30:
                target_pumpkins = 3
            elif score >= 20:
                target_pumpkins = 2

            while len(pumpkins) < target_pumpkins:
                pumpkins.append(spawn_entity(pumpkin_img))

            #Move pumpkins...
            for rect in pumpkins:
                rect.y += pumpkin_speed
                if rect.top > SCREEN_HEIGHT:
                    rect.topleft = rect.topleft = (random.randint(0, SCREEN_WIDTH - rect.width), 0)
                    pumpkin_speed += SPEED_INCREMENT
                    #score = 0
                    message_text = "Miss!"
                    message_color = (255, 80, 80)
                    message_alpha = 255

            #Move the ghost...
            ghost_rect.y += ghost_speed
            ghost_rect.x += int(3 * math.sin(pygame.time.get_ticks() * 0.003))
            if ghost_rect.top > SCREEN_HEIGHT:
                ghost_rect = spawn_entity(ghost_img)

            alpha = 190 + int(40 * math.sin(pygame.time.get_ticks() * 0.004))
            ghost_img.set_alpha(alpha)
            screen.blit(ghost_img, ghost_rect)

        #Draw the background...
        draw_dynamic_gradient(screen, pygame.time.get_ticks())

        # Draw the grass ...
        grass_rect = pygame.Rect(0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2)
        pygame.draw.rect(screen, (34, 139, 34), grass_rect) # Grass color

        #Draw pumpkins...
        for rect in pumpkins:
            offset_y = int(5 * math.sin((pygame.time.get_ticks() + rect.x) * 0.004))
            shadow_rect = rect.copy()
            shadow_rect.move_ip(5, 10)
            pygame.draw.ellipse(screen, (0, 0, 0, 80), shadow_rect.inflate(-rect.width * 0.5, -rect.height * 0.8))
            screen.blit(pumpkin_img, (rect.x, rect.y + offset_y))

        #Draw the ghost (slight transparency).
        if not game_over:
            ghost_img.set_alpha(210)
            screen.blit(ghost_img, ghost_rect)

        #Draw explosions ...
        new_explosions = []
        for exp in explosions:
            if exp["frame"] < len(explosion_imgs):
                img = explosion_imgs[exp["frame"]].copy()
                flicker = 200 + int(55 * math.sin(pygame.time.get_ticks() * 0.02))
                img.set_alpha(min(exp["alpha"], flicker))
                screen.blit(img, exp["rect"])
                exp["frame"] += 1
                exp["alpha"] -= 30
                new_explosions.append(exp)
        explosions = new_explosions

        #Render the score ...
        score_surface = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_surface, (15,10))

        #Message fade...
        if message_text and message_alpha > 0:
            msg_surface = font.render(message_text, True, message_color)
            msg_surface.set_alpha(message_alpha)
            msg_x = SCREEN_WIDTH // 2 - msg_surface.get_width() // 2
            msg_y = SCREEN_HEIGHT // 4
            screen.blit(msg_surface, (msg_x, msg_y))
            message_alpha -= 4

        #Game-over overlay....
        if game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((20, 20, 20))
            screen.blit(overlay, (0, 0))
            go_text = font.render("👻 Game Over - Click X to Exit", True, (255, 255, 255))
            msg_x = SCREEN_WIDTH // 2 - go_text.get_width() // 2
            msg_y = SCREEN_HEIGHT // 2 - go_text.get_height() // 2
            screen.blit(go_text, (msg_x, msg_y))

        #Update the display...
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()