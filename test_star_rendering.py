#!/usr/bin/env python3
"""
Visual test for star rating rendering and animation
"""

import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Screen setup
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Star Rating Visual Test")

# Import renderer
from game.renderer import Renderer

# Create renderer
renderer = Renderer(screen)

# Clock for frame rate
clock = pygame.time.Clock()

# Animation state
animation_progress = 0.0
animation_speed = 0.3  # Progress per second
current_stars = 3
zen_mode = False

# Font for instructions
font = pygame.font.SysFont('Arial', 20)

running = True
while running:
    dt = clock.get_time() / 1000.0
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                # Reset animation
                animation_progress = 0.0
            elif event.key == pygame.K_1:
                current_stars = 1
                animation_progress = 0.0
            elif event.key == pygame.K_2:
                current_stars = 2
                animation_progress = 0.0
            elif event.key == pygame.K_3:
                current_stars = 3
                animation_progress = 0.0
            elif event.key == pygame.K_0:
                current_stars = 0
                animation_progress = 0.0
            elif event.key == pygame.K_z:
                zen_mode = not zen_mode
    
    # Update animation
    if animation_progress < 1.0:
        animation_progress += dt * animation_speed
        animation_progress = min(1.0, animation_progress)
    
    # Clear screen
    screen.fill((200, 220, 240))
    
    # Render title
    title_font = pygame.font.SysFont('Arial', 48, bold=True)
    title_surface = title_font.render("Star Rating System Test", True, (70, 130, 180))
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 80))
    screen.blit(title_surface, title_rect)
    
    # Render star rating or peace
    if zen_mode:
        renderer.render_peace_rating(SCREEN_WIDTH // 2, 250)
        mode_text = "Zen Mode: Peace Rating"
    else:
        renderer.render_star_rating(SCREEN_WIDTH // 2, 250, current_stars, animation_progress)
        mode_text = f"Star Rating: {current_stars} stars"
    
    # Render mode text
    mode_surface = font.render(mode_text, True, (100, 100, 100))
    mode_rect = mode_surface.get_rect(center=(SCREEN_WIDTH // 2, 380))
    screen.blit(mode_surface, mode_rect)
    
    # Render animation progress
    progress_text = f"Animation Progress: {int(animation_progress * 100)}%"
    progress_surface = font.render(progress_text, True, (100, 100, 100))
    progress_rect = progress_surface.get_rect(center=(SCREEN_WIDTH // 2, 420))
    screen.blit(progress_surface, progress_rect)
    
    # Render instructions
    instructions = [
        "Press 0-3 to change star count",
        "Press R to reset animation",
        "Press Z to toggle Zen mode",
        "Press ESC to exit"
    ]
    
    y_offset = 500
    for instruction in instructions:
        inst_surface = font.render(instruction, True, (80, 80, 80))
        inst_rect = inst_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
        screen.blit(inst_surface, inst_rect)
        y_offset += 30
    
    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
