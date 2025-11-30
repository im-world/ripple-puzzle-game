"""
Demo script for Fish Builder interface.
Run this to test the fish builder UI interactively.
"""

import pygame
import sys
from game.fish_builder import FishBuilder
from game.config import SCREEN_WIDTH, SCREEN_HEIGHT, TARGET_FPS


def main():
    """Run fish builder demo."""
    # Initialize Pygame
    pygame.init()
    
    # Create window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Fish Builder Demo")
    
    # Create clock
    clock = pygame.time.Clock()
    
    # Create fish builder
    fish_builder = FishBuilder(screen)
    
    # Create back button
    class Button:
        def __init__(self, x, y, width, height, text):
            self.rect = pygame.Rect(x, y, width, height)
            self.text = text
            self.is_hovered = False
        
        def update(self, mouse_pos):
            self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        def draw(self, screen, font):
            color = (120, 170, 220) if self.is_hovered else (100, 150, 200)
            pygame.draw.rect(screen, color, self.rect, border_radius=10)
            pygame.draw.rect(screen, (70, 70, 70), self.rect, 2, border_radius=10)
            
            text_surface = font.render(self.text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)
        
        def is_clicked(self, mouse_pos):
            return self.rect.collidepoint(mouse_pos)
    
    back_button = Button(
        SCREEN_WIDTH // 2 - 100,
        SCREEN_HEIGHT - 60,
        200,
        50,
        "Exit Demo"
    )
    
    running = True
    
    print("\n=== Fish Builder Demo ===")
    print("Controls:")
    print("- Click tool buttons to select drawing tools")
    print("- Click color swatches to change color")
    print("- Click and drag on canvas to draw")
    print("- Ctrl+Z to undo, Ctrl+Y to redo")
    print("- Click 'Clear' to clear canvas")
    print("- Click fish templates on left to switch between them")
    print("- Click 'Exit Demo' button or press ESC to exit")
    print("========================\n")
    
    while running:
        dt = clock.get_time() / 1000.0
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    fish_builder.handle_key_down(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if back_button.is_clicked(mouse_pos):
                    running = False
                else:
                    fish_builder.handle_mouse_down(mouse_pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_pos = pygame.mouse.get_pos()
                fish_builder.handle_mouse_up(mouse_pos)
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                fish_builder.handle_mouse_motion(mouse_pos)
        
        # Update
        mouse_pos = pygame.mouse.get_pos()
        back_button.update(mouse_pos)
        
        # Render
        fish_builder.draw()
        
        # Draw back button
        button_font = pygame.font.SysFont('Arial', 28)
        back_button.draw(screen, button_font)
        
        # Draw keyboard shortcuts hint
        hint_font = pygame.font.SysFont('Arial', 16)
        hint_text = "Ctrl+Z: Undo | Ctrl+Y: Redo | Click color swatches to change color"
        hint_surface = hint_font.render(hint_text, True, (100, 100, 100))
        hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
        screen.blit(hint_surface, hint_rect)
        
        # Update display
        pygame.display.flip()
        
        # Maintain frame rate
        clock.tick(TARGET_FPS)
    
    # Clean up
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
