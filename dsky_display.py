#!/usr/bin/env python3
"""
DSKY Display Module
Handles pygame rendering and display state management
"""

import pygame
import time
import sys
import os
import threading
from dsky_config import Config, hex_to_rgb


class DisplayState:
    """Manages the current state of all DSKY display elements"""

    def __init__(self):
        self.prog = [0, 0]  # M1, M2 (PROG/Major mode)
        self.verb = [0, 0]  # V1, V2
        self.noun = [0, 0]  # N1, N2
        self.r1 = [0, 0, 0, 0, 0]  # Register 1 (5 digits)
        self.r2 = [0, 0, 0, 0, 0]  # Register 2 (5 digits)
        self.r3 = [0, 0, 0, 0, 0]  # Register 3 (5 digits)
        self.r1_sign = None  # None, '+', or '-'
        self.r2_sign = None
        self.r3_sign = None
        self.comp_acty = False  # Computer Activity indicator
        self.connected = True   # yaAGC connection status
        self.lock = threading.Lock()  # Thread safety

    def set_prog(self, m1, m2):
        """Set PROG display"""
        with self.lock:
            self.prog = [m1, m2]

    def set_verb(self, v1, v2):
        """Set VERB display"""
        with self.lock:
            self.verb = [v1, v2]

    def set_noun(self, n1, n2):
        """Set NOUN display"""
        with self.lock:
            self.noun = [n1, n2]

    def set_register(self, reg_num, digits, sign=None):
        """Set register display (reg_num: 1, 2, or 3)"""
        with self.lock:
            if reg_num == 1:
                self.r1 = digits[:5]
                if sign is not None:
                    self.r1_sign = sign
            elif reg_num == 2:
                self.r2 = digits[:5]
                if sign is not None:
                    self.r2_sign = sign
            elif reg_num == 3:
                self.r3 = digits[:5]
                if sign is not None:
                    self.r3_sign = sign

    def get_snapshot(self):
        """Get thread-safe snapshot of current state"""
        with self.lock:
            return {
                'prog': self.prog.copy(),
                'verb': self.verb.copy(),
                'noun': self.noun.copy(),
                'r1': self.r1.copy(),
                'r2': self.r2.copy(),
                'r3': self.r3.copy(),
                'r1_sign': self.r1_sign,
                'r2_sign': self.r2_sign,
                'r3_sign': self.r3_sign,
                'comp_acty': self.comp_acty,
                'connected': self.connected
            }


class DSKYDisplay:
    """Main DSKY display renderer using pygame"""

    def __init__(self, config: Config):
        self.config = config
        self.state = DisplayState()
        self.running = False

        # Initialize pygame
        pygame.init()

        # Create window
        width = config.display.resolution.width
        height = config.display.resolution.height
        if config.display.window_mode == 'fullscreen':
            self.screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((width, height))

        pygame.display.set_caption(config.display.window_title)

        # Parse colors
        self.bg_color = hex_to_rgb(config.display.colors.background)
        self.fg_color = hex_to_rgb(config.display.colors.foreground)
        self.fg_dim_color = hex_to_rgb(config.display.colors.foreground_dim)
        self.error_color = hex_to_rgb(config.display.colors.error_overlay)

        # Load fonts
        self.fonts = self._load_fonts()

        # Create clock for FPS management
        self.clock = pygame.time.Clock()

        # Last error blink time
        self.last_blink_time = time.time()
        self.blink_state = False

    def _load_fonts(self):
        """Load all required fonts - using system fonts for Pi compatibility"""
        fonts = {}

        print("Using system monospace font for Raspberry Pi compatibility")
        # Use system monospace font directly (bold for better visibility)
        fonts['prog'] = pygame.font.SysFont('monospace', self.config.display.font.size_prog, bold=True)
        fonts['verb_noun'] = pygame.font.SysFont('monospace', self.config.display.font.size_verb_noun, bold=True)
        fonts['register'] = pygame.font.SysFont('monospace', self.config.display.font.size_register, bold=True)
        fonts['sign'] = pygame.font.SysFont('monospace', self.config.display.font.size_sign, bold=True)
        fonts['error'] = pygame.font.SysFont('monospace', self.config.error_display.font_size)

        return fonts

    def render_7segment_digit(self, digit, x, y, font):
        """
        Render a 7-segment digit with authentic appearance
        Shows ghost '8' in background, then actual digit on top
        """
        # Render background "8" (all segments) in dim color
        ghost = font.render("8", True, self.fg_dim_color)
        self.screen.blit(ghost, (x, y))

        # Render actual digit in bright color
        if digit is not None:
            digit_surface = font.render(str(digit), True, self.fg_color)
            self.screen.blit(digit_surface, (x, y))

    def render_sign(self, sign, x, y):
        """Render +/- sign indicator"""
        font = self.fonts['sign']

        # Render both + and - in dim color as background
        ghost_plus = font.render("+", True, self.fg_dim_color)
        ghost_minus = font.render("-", True, self.fg_dim_color)

        # Calculate positions (+ above -)
        plus_y = y - 20
        minus_y = y + 5

        self.screen.blit(ghost_plus, (x, plus_y))
        self.screen.blit(ghost_minus, (x, minus_y))

        # Render active sign in bright color
        if sign == '+':
            sign_surface = font.render("+", True, self.fg_color)
            self.screen.blit(sign_surface, (x, plus_y))
        elif sign == '-':
            sign_surface = font.render("-", True, self.fg_color)
            self.screen.blit(sign_surface, (x, minus_y))

    def render_prog(self, snapshot):
        """Render PROG (Major Mode) display"""
        layout = self.config.layout.prog
        font = self.fonts['prog']
        x = layout.x
        spacing = layout.spacing

        for i, digit in enumerate(snapshot['prog']):
            self.render_7segment_digit(digit, x + i * (spacing + 40), layout.y, font)

    def render_verb(self, snapshot):
        """Render VERB display"""
        layout = self.config.layout.verb
        font = self.fonts['verb_noun']
        x = layout.x
        spacing = layout.spacing

        for i, digit in enumerate(snapshot['verb']):
            self.render_7segment_digit(digit, x + i * (spacing + 40), layout.y, font)

    def render_noun(self, snapshot):
        """Render NOUN display"""
        layout = self.config.layout.noun
        font = self.fonts['verb_noun']
        x = layout.x
        spacing = layout.spacing

        for i, digit in enumerate(snapshot['noun']):
            self.render_7segment_digit(digit, x + i * (spacing + 40), layout.y, font)

    def render_register(self, reg_num, snapshot):
        """Render a register (R1, R2, or R3)"""
        if reg_num == 1:
            layout = self.config.layout.register_1
            digits = snapshot['r1']
            sign = snapshot['r1_sign']
        elif reg_num == 2:
            layout = self.config.layout.register_2
            digits = snapshot['r2']
            sign = snapshot['r2_sign']
        elif reg_num == 3:
            layout = self.config.layout.register_3
            digits = snapshot['r3']
            sign = snapshot['r3_sign']
        else:
            return

        font = self.fonts['register']
        x = layout.x
        spacing = layout.digit_spacing

        # Render sign indicator
        self.render_sign(sign, layout.sign_x, layout.sign_y)

        # Render 5 digits
        for i, digit in enumerate(digits):
            self.render_7segment_digit(digit, x + i * (spacing + 30), layout.y, font)

    def render_comp_acty(self, snapshot):
        """Render COMP ACTY indicator"""
        layout = self.config.layout.comp_acty

        # Draw rectangle
        if snapshot['comp_acty']:
            color = self.fg_color
        else:
            color = self.fg_dim_color

        pygame.draw.rect(self.screen, color,
                        (layout.x, layout.y, layout.width, layout.height), 2)

        # Draw label
        font = pygame.font.SysFont('monospace', 12)
        label = font.render("COMP ACTY", True, color)
        label_rect = label.get_rect(center=(layout.x + layout.width // 2, layout.y + layout.height // 2))
        self.screen.blit(label, label_rect)

    def render_error_overlay(self):
        """Render error overlay when yaAGC connection is lost"""
        if not self.config.error_display.enabled:
            return

        # Create semi-transparent overlay
        overlay = pygame.Surface((self.config.display.resolution.width,
                                 self.config.display.resolution.height))
        overlay.set_alpha(200)
        overlay.fill(self.error_color)
        self.screen.blit(overlay, (0, 0))

        # Blinking error message
        current_time = time.time()
        if current_time - self.last_blink_time > self.config.error_display.blink_rate:
            self.last_blink_time = current_time
            self.blink_state = not self.blink_state

        if self.blink_state:
            font = self.fonts['error']
            text = font.render(self.config.error_display.message, True, (255, 255, 255))
            rect = text.get_rect(center=(self.config.display.resolution.width // 2,
                                        self.config.display.resolution.height // 2))
            self.screen.blit(text, rect)

    def render(self):
        """Main render method - draws all display elements"""
        # Get thread-safe snapshot of current state
        snapshot = self.state.get_snapshot()

        # Clear screen with background color
        self.screen.fill(self.bg_color)

        # Render all display elements
        self.render_prog(snapshot)
        self.render_verb(snapshot)
        self.render_noun(snapshot)
        self.render_register(1, snapshot)
        self.render_register(2, snapshot)
        self.render_register(3, snapshot)
        self.render_comp_acty(snapshot)

        # Render error overlay if not connected
        if not snapshot['connected']:
            self.render_error_overlay()

        # Update display
        pygame.display.flip()

    def run(self, simulator=None):
        """
        Main display loop

        Args:
            simulator: Optional DSKYSimulator for simulation mode
        """
        self.running = True

        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif simulator:
                        simulator.handle_keyboard(event)

            # Render display
            self.render()

            # Maintain target FPS
            self.clock.tick(self.config.display.fps)

        # Cleanup
        pygame.quit()


if __name__ == '__main__':
    # Test display rendering
    from dsky_config import load_config

    try:
        config = load_config('config/dsky_config.yaml')
        display = DSKYDisplay(config)

        # Set some test values
        display.state.set_prog(1, 6)
        display.state.set_verb(3, 7)
        display.state.set_noun(0, 6)
        display.state.set_register(1, [1, 2, 3, 4, 5], '+')
        display.state.set_register(2, [9, 8, 7, 6, 5], '-')
        display.state.set_register(3, [0, 0, 0, 0, 0], None)
        display.state.comp_acty = True

        print("Starting display test...")
        print("Press ESC to exit")
        display.run()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
