#!/usr/bin/env python3
"""
Demo script for high-contrast mode.
Shows the settings menu with high-contrast mode checkbox.
"""

import pygame
import sys
from game.config import SCREEN_WIDTH, SCREEN_HEIGHT

# Import necessary classes
from main import Button, Checkbox, Slider

def main():
    """Run high-contrast mode demo."""
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("High-Contrast Mode Demo")
    clock = pygame.time.Clock()
    
    # Create UI elements (matching settings screen layout)
    slider_width = 300
    slider_x = SCREEN_WIDTH // 2 - slider_width // 2
    
    sound_volume_slider = Slider(slider_x, 200, slider_width, 40, 0.0, 1.0, 0.7, "Sound Effects Volume")
    music_volume_slider = Slider(slider_x, 280, slider_width, 40, 0.0, 1.0, 0.25, "Music Volume")
    
    # High-contrast mode checkbox
    checkbox_size = 20
    checkbox_x = SCREEN_WIDTH // 2 - 100
    checkbox_y = 360
    high_contrast_checkbox = Checkbox(checkbox_x, checkbox_y, checkbox_size, "High-Contrast Mode", checked=False)
    
    # Mute toggle buttons
    toggle_button_width = 150
    toggle_button_x = SCREEN_WIDTH // 2 - toggle_button_width // 2
    button_width = 200
    button_height = 50
    button_x = SCREEN_WIDTH // 2 - button_width // 2
    
    settings_buttons = {
        'sound_mute': Button(toggle_button_x, 420, toggle_button_width, 40, "Mute Sounds", (150, 100, 100), (170, 120, 120)),
        'music_mute': Button(toggle_button_x, 470, toggle_button_width, 40, "Mute Music", (150, 100, 100), (170, 120, 120)),
        'back': Button(button_x, SCREEN_HEIGHT - 120, button_width, button_height, "Back to Menu")
    }
    
    # Fonts
    title_font = pygame.font.SysFont('Arial', 56, bold=True)
    slider_font = pygame.font.SysFont('Arial', 20)
    checkbox_font = pygame.font.SysFont('Arial', 18)
    button_font = pygame.font.SysFont('Arial', 20)
    info_font = pygame.font.SysFont('Arial', 16)
    
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            # Handle mouse events
            mouse_pos = pygame.mouse.get_pos()
            
            # Handle slider events
            sound_volume_slider.handle_event(event, mouse_pos)
            music_volume_slider.handle_event(event, mouse_pos)
            
            # Handle checkbox click
            if event.type == pygame.MOUSEBUTTONDOWN:
                if high_contrast_checkbox.is_clicked(mouse_pos):
                    high_contrast_checkbox.toggle()
                    print(f"High-contrast mode: {'ON' if high_contrast_checkbox.is_checked() else 'OFF'}")
        
        # Update
        mouse_pos = pygame.mouse.get_pos()
        for button in settings_buttons.values():
            button.update(mouse_pos)
        high_contrast_checkbox.update(mouse_pos)
        
        # Render
        screen.fill((200, 220, 240))
        
        # Render title
        title_surface = title_font.render("Settings", True, (70, 130, 180))
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title_surface, title_rect)
        
        # Render sliders
        sound_volume_slider.draw(screen, slider_font)
        music_volume_slider.draw(screen, slider_font)
        
        # Render high-contrast mode checkbox
        high_contrast_checkbox.draw(screen, checkbox_font)
        
        # Render buttons
        for button in settings_buttons.values():
            button.draw(screen, button_font)
        
        # Render info text
        info_lines = [
            "High-Contrast Mode Demo",
            "",
            "Click the checkbox to toggle high-contrast mode.",
            "This setting overrides zen palette for accessibility.",
            "",
            "Features:",
            "• Maintains smooth animations",
            "• Keeps minimalist UI design",
            "• Improves visibility for users with visual impairments",
            "",
            "Press ESC to exit"
        ]
        
        y_offset = SCREEN_HEIGHT - 280
        for line in info_lines:
            if line:
                info_surface = info_font.render(line, True, (100, 100, 100))
            else:
                info_surface = info_font.render(" ", True, (100, 100, 100))
            info_rect = info_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(info_surface, info_rect)
            y_offset += 20
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()
