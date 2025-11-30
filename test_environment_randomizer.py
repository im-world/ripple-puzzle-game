#!/usr/bin/env python3
"""
Test script for Environment Randomizer button.
Tests the button functionality, animations, and environment system.
"""

import pygame
import sys
from game.config import SCREEN_WIDTH, SCREEN_HEIGHT
from game.environment import EnvironmentSystem
from main import EnvironmentRandomizerButton


def test_environment_randomizer():
    """Test the environment randomizer button and system."""
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Environment Randomizer Test")
    clock = pygame.time.Clock()
    
    # Create environment system
    environment = EnvironmentSystem()
    
    # Create environment randomizer button
    button = EnvironmentRandomizerButton(20, 20, 50)
    
    # Font for text
    font = pygame.font.SysFont('Arial', 20)
    title_font = pygame.font.SysFont('Arial', 32, bold=True)
    
    running = True
    randomize_count = 0
    
    print("Environment Randomizer Test")
    print("=" * 50)
    print("Click the dice button in the top-left to randomize!")
    print("Watch for:")
    print("  - Hover pulse animation")
    print("  - Click spin animation")
    print("  - Background color changes")
    print("  - Weather effects (leaves, snow, rain, fireflies)")
    print("  - Time of day tints")
    print("\nPress ESC to exit")
    print("=" * 50)
    
    while running:
        dt = clock.get_time() / 1000.0
        mouse_pos = pygame.mouse.get_pos()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button.is_clicked(mouse_pos):
                    environment.randomize()
                    button.start_spin()
                    randomize_count += 1
                    
                    # Print current environment settings
                    print(f"\nRandomization #{randomize_count}")
                    print(f"  Theme: {environment.current_theme}")
                    print(f"  Weather: {environment.current_weather}")
                    print(f"  Time: {environment.current_time}")
                    print(f"  Background: {environment.background_color}")
                    print(f"  Water Light: {environment.water_light}")
                    print(f"  Water Dark: {environment.water_dark}")
        
        # Update
        environment.update(dt)
        button.update(mouse_pos, dt)
        
        # Render
        screen.fill(environment.get_background_color())
        
        # Draw water pool representation
        water_rect = pygame.Rect(100, 150, 824, 468)
        water_light, water_dark = environment.get_water_colors()
        
        # Gradient water
        for i in range(water_rect.height):
            ratio = i / water_rect.height
            smooth_ratio = ratio * ratio * (3 - 2 * ratio)
            
            r = int(water_light[0] * (1 - smooth_ratio) + water_dark[0] * smooth_ratio)
            g = int(water_light[1] * (1 - smooth_ratio) + water_dark[1] * smooth_ratio)
            b = int(water_light[2] * (1 - smooth_ratio) + water_dark[2] * smooth_ratio)
            
            pygame.draw.line(screen, (r, g, b), 
                           (water_rect.left, water_rect.top + i), 
                           (water_rect.right, water_rect.top + i))
        
        pygame.draw.rect(screen, (120, 180, 200), water_rect, 3)
        
        # Render weather effects
        environment.render_weather(screen)
        
        # Render button
        button.draw(screen, font)
        
        # Render title
        title_text = "Environment Randomizer Test"
        title_surface = title_font.render(title_text, True, (70, 70, 70))
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(title_surface, title_rect)
        
        # Render current settings
        y_offset = 100
        settings_texts = [
            f"Theme: {environment.current_theme}",
            f"Weather: {environment.current_weather}",
            f"Time: {environment.current_time}",
            f"Randomizations: {randomize_count}"
        ]
        
        for text in settings_texts:
            text_surface = font.render(text, True, (70, 70, 70))
            screen.blit(text_surface, (SCREEN_WIDTH - 300, y_offset))
            y_offset += 30
        
        # Render instructions
        instructions = [
            "Click the dice button to randomize",
            "Hover over button to see pulse effect",
            "Watch the spin animation on click"
        ]
        
        y_offset = SCREEN_HEIGHT - 120
        for text in instructions:
            text_surface = font.render(text, True, (100, 100, 100))
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(text_surface, text_rect)
            y_offset += 30
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("\nTest completed!")
    print(f"Total randomizations: {randomize_count}")


if __name__ == "__main__":
    test_environment_randomizer()
