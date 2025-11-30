#!/usr/bin/env python3
"""
Demo script showing the star rating system in action
This simulates completing a level and showing the star rating
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
pygame.display.set_caption("Star Rating System Demo")

# Import required modules
from game.renderer import Renderer
from game.level import LevelManager, LevelData
from game.physics import Vector2, Ball

# Create renderer
renderer = Renderer(screen)

# Create a test level
test_level = LevelData(
    level_id=1,
    ball_start=Vector2(100, 300),
    target_position=Vector2(700, 300),
    target_radius=40,
    obstacles=[],
    walls=[],
    current_zones=[],
    whirlpools=[],
    initial_stones=10,
    tutorial=False
)

# Create level manager
level_manager = LevelManager([test_level])
level_manager.initialize_level(Ball, 0)

# Demo scenarios
scenarios = [
    {"stones": 3, "description": "Perfect Performance", "stars": 3},
    {"stones": 5, "description": "Excellent Performance", "stars": 3},
    {"stones": 7, "description": "Good Performance", "stars": 2},
    {"stones": 9, "description": "Okay Performance", "stars": 1},
    {"stones": 12, "description": "Completed (No Stars)", "stars": 0},
]

current_scenario = 0
animation_progress = 0.0
animation_duration = 1.5
zen_mode = False

# Font
font = pygame.font.SysFont('Arial', 24)
title_font = pygame.font.SysFont('Arial', 56, bold=True)

clock = pygame.time.Clock()
running = True

print("Star Rating System Demo")
print("=" * 60)
print("Controls:")
print("  SPACE - Next scenario")
print("  R - Reset animation")
print("  Z - Toggle Zen mode")
print("  ESC - Exit")
print("=" * 60)

while running:
    dt = clock.get_time() / 1000.0
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                # Next scenario
                current_scenario = (current_scenario + 1) % len(scenarios)
                animation_progress = 0.0
                print(f"\nScenario {current_scenario + 1}: {scenarios[current_scenario]['description']}")
                print(f"  Stones used: {scenarios[current_scenario]['stones']}")
                print(f"  Star rating: {scenarios[current_scenario]['stars']} stars")
            elif event.key == pygame.K_r:
                # Reset animation
                animation_progress = 0.0
            elif event.key == pygame.K_z:
                # Toggle Zen mode
                zen_mode = not zen_mode
                print(f"\nZen mode: {'ON' if zen_mode else 'OFF'}")
    
    # Update animation
    if animation_progress < 1.0:
        animation_progress += dt / animation_duration
        animation_progress = min(1.0, animation_progress)
    
    # Get current scenario data
    scenario = scenarios[current_scenario]
    stones_used = scenario["stones"]
    description = scenario["description"]
    stars = scenario["stars"]
    
    # Clear screen
    screen.fill((200, 220, 240))
    
    # Render title
    title_surface = title_font.render("Level Complete!", True, (70, 180, 70))
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
    
    # Add bounce animation
    import time
    bounce = abs(math.sin(time.time() * 3)) * 5
    title_rect.y -= int(bounce)
    
    screen.blit(title_surface, title_rect)
    
    # Render star rating or peace
    star_y = 220
    
    if zen_mode:
        renderer.render_peace_rating(SCREEN_WIDTH // 2, star_y)
    else:
        renderer.render_star_rating(SCREEN_WIDTH // 2, star_y, stars, animation_progress)
    
    # Render scenario info
    y_offset = 340
    
    # Scenario description
    desc_surface = font.render(f"Scenario: {description}", True, (100, 100, 100))
    desc_rect = desc_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
    screen.blit(desc_surface, desc_rect)
    y_offset += 40
    
    # Stones used
    stones_surface = font.render(f"Stones Used This Level: {stones_used}", True, (100, 100, 100))
    stones_rect = stones_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
    screen.blit(stones_surface, stones_rect)
    y_offset += 40
    
    # Star rating
    if not zen_mode:
        rating_text = f"Star Rating: {stars} star{'s' if stars != 1 else ''}"
        rating_surface = font.render(rating_text, True, (100, 100, 100))
        rating_rect = rating_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
        screen.blit(rating_surface, rating_rect)
        y_offset += 40
    
    # Animation progress
    progress_text = f"Animation: {int(animation_progress * 100)}%"
    progress_surface = font.render(progress_text, True, (100, 100, 100))
    progress_rect = progress_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
    screen.blit(progress_surface, progress_rect)
    
    # Render controls at bottom
    controls = [
        "SPACE - Next Scenario",
        "R - Reset Animation",
        "Z - Toggle Zen Mode",
        "ESC - Exit"
    ]
    
    y_offset = 550
    for control in controls:
        control_surface = font.render(control, True, (80, 80, 80))
        control_rect = control_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
        screen.blit(control_surface, control_rect)
        y_offset += 30
    
    # Render scenario counter
    counter_text = f"Scenario {current_scenario + 1} of {len(scenarios)}"
    counter_surface = font.render(counter_text, True, (120, 120, 120))
    counter_rect = counter_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
    screen.blit(counter_surface, counter_rect)
    
    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
