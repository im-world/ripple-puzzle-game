#!/usr/bin/env python3
"""
Demo script to showcase the tutorial system.
Shows tooltips for each tutorial level.
"""

import pygame
import sys
from game.tutorial import TutorialManager
from game.level import load_levels_with_fallback
from game.config import SCREEN_WIDTH, SCREEN_HEIGHT

def main():
    """Run tutorial demo."""
    # Initialize Pygame
    pygame.init()
    
    # Create window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Ripple - Tutorial Demo")
    
    # Create clock
    clock = pygame.time.Clock()
    
    # Load levels
    levels = load_levels_with_fallback("levels/level_data.json")
    
    # Create tutorial manager
    tutorial_manager = TutorialManager(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # Current level being demoed
    current_level_index = 0
    tutorial_levels = [0, 1, 2, 3]  # Levels 1-4 (0-indexed)
    
    # Start first tutorial
    tutorial_manager.start_tutorial(
        tutorial_levels[current_level_index] + 1,
        levels[tutorial_levels[current_level_index]]
    )
    
    # Font for instructions
    font = pygame.font.SysFont('Arial', 20)
    title_font = pygame.font.SysFont('Arial', 32, bold=True)
    
    running = True
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
                elif event.key == pygame.K_SPACE:
                    # Next level
                    current_level_index = (current_level_index + 1) % len(tutorial_levels)
                    tutorial_manager.start_tutorial(
                        tutorial_levels[current_level_index] + 1,
                        levels[tutorial_levels[current_level_index]]
                    )
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Handle tutorial clicks
                tutorial_manager.handle_click(mouse_pos)
        
        # Update tutorial
        tutorial_manager.update(dt, mouse_pos)
        
        # Render
        screen.fill((200, 220, 240))
        
        # Draw title
        level_num = tutorial_levels[current_level_index] + 1
        title_text = f"Tutorial Demo - Level {level_num}"
        title_surface = title_font.render(title_text, True, (70, 130, 180))
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(title_surface, title_rect)
        
        # Draw instructions
        instructions = [
            "Press SPACE to cycle through tutorial levels (1-4)",
            "Click 'Got it!' to advance to next tooltip",
            "Click 'Skip Tutorial' to skip all tooltips",
            "Press ESC to exit"
        ]
        
        y_offset = 120
        for instruction in instructions:
            text_surface = font.render(instruction, True, (100, 100, 100))
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(text_surface, text_rect)
            y_offset += 30
        
        # Draw level info
        info_y = 250
        level_info = [
            f"Level {level_num} Tutorial:",
            ""
        ]
        
        if level_num == 1:
            level_info.append("• Catapult interaction")
            level_info.append("• Trajectory preview")
            level_info.append("• Ripple creation")
        elif level_num == 2:
            level_info.append("• Anti-ripple zone mechanics")
        elif level_num == 3:
            level_info.append("• Wall reflection mechanics")
        elif level_num == 4:
            level_info.append("• Whirlpool mechanics")
            level_info.append("• Current zone mechanics")
        
        for info in level_info:
            text_surface = font.render(info, True, (70, 70, 70))
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, info_y))
            screen.blit(text_surface, text_rect)
            info_y += 25
        
        # Draw tutorial status
        status_y = SCREEN_HEIGHT - 100
        if tutorial_manager.is_tutorial_active():
            status_text = f"Tooltip {tutorial_manager.current_tooltip_index + 1} of {len(tutorial_manager.active_tooltips)}"
            status_color = (70, 180, 70)
        else:
            status_text = "Tutorial completed or skipped"
            status_color = (180, 70, 70)
        
        status_surface = font.render(status_text, True, status_color)
        status_rect = status_surface.get_rect(center=(SCREEN_WIDTH // 2, status_y))
        screen.blit(status_surface, status_rect)
        
        # Render tutorial UI
        tutorial_manager.render(screen)
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
