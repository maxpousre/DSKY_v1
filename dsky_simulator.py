#!/usr/bin/env python3
"""
DSKY Simulator
Provides manual control for testing without yaAGC
"""

import pygame
from dsky_display import DisplayState


class DSKYSimulator:
    """Provides manual control for testing DSKY display without yaAGC"""

    def __init__(self, display_state: DisplayState):
        self.state = display_state
        self.selected_element = 'prog'  # prog, verb, noun, r1, r2, r3
        self.selected_digit = 0  # Which digit in the selected element

        print("\n=== DSKY Simulation Mode ===")
        print("Keyboard Controls:")
        print("  0-9: Set selected digit")
        print("  F1:  Blank display")
        print("  F2:  All eights (lamp test)")
        print("  F3:  Test pattern (VERB 16 NOUN 36)")
        print("  F4:  Count animation")
        print("  P:   Select PROG")
        print("  V:   Select VERB")
        print("  N:   Select NOUN")
        print("  R:   Select Register (cycles R1->R2->R3)")
        print("  +:   Set positive sign on selected register")
        print("  -:   Set negative sign on selected register")
        print("  C:   Toggle COMP ACTY")
        print("  E:   Toggle error display")
        print("  ESC: Exit")
        print("================================\n")

    def handle_keyboard(self, event):
        """
        Handle keyboard events for manual control

        Args:
            event: pygame.KEYDOWN event
        """
        key = event.key

        # Number keys 0-9
        if pygame.K_0 <= key <= pygame.K_9:
            digit = key - pygame.K_0
            self._set_digit(digit)

        # Function keys for test patterns
        elif key == pygame.K_F1:
            self.pattern_blank()
            print("Pattern: Blank")
        elif key == pygame.K_F2:
            self.pattern_all_eights()
            print("Pattern: All eights (lamp test)")
        elif key == pygame.K_F3:
            self.pattern_test()
            print("Pattern: Test (V16N36)")
        elif key == pygame.K_F4:
            self.pattern_counting()
            print("Pattern: Counting")

        # Element selection
        elif key == pygame.K_p:
            self.selected_element = 'prog'
            self.selected_digit = 0
            print(f"Selected: PROG digit {self.selected_digit}")
        elif key == pygame.K_v:
            self.selected_element = 'verb'
            self.selected_digit = 0
            print(f"Selected: VERB digit {self.selected_digit}")
        elif key == pygame.K_n:
            self.selected_element = 'noun'
            self.selected_digit = 0
            print(f"Selected: NOUN digit {self.selected_digit}")
        elif key == pygame.K_r:
            # Cycle through registers
            if self.selected_element == 'r1':
                self.selected_element = 'r2'
            elif self.selected_element == 'r2':
                self.selected_element = 'r3'
            else:
                self.selected_element = 'r1'
            self.selected_digit = 0
            print(f"Selected: {self.selected_element.upper()} digit {self.selected_digit}")

        # Sign control
        elif key == pygame.K_PLUS or key == pygame.K_EQUALS:  # + key
            self._set_sign('+')
        elif key == pygame.K_MINUS:  # - key
            self._set_sign('-')

        # COMP ACTY toggle
        elif key == pygame.K_c:
            with self.state.lock:
                self.state.comp_acty = not self.state.comp_acty
            print(f"COMP ACTY: {self.state.comp_acty}")

        # Error display toggle (for testing)
        elif key == pygame.K_e:
            with self.state.lock:
                self.state.connected = not self.state.connected
            print(f"Connected: {self.state.connected}")

        # Arrow keys to navigate digits
        elif key == pygame.K_LEFT:
            max_digits = self._get_max_digits()
            self.selected_digit = (self.selected_digit - 1) % max_digits
            print(f"Selected: {self.selected_element.upper()} digit {self.selected_digit}")
        elif key == pygame.K_RIGHT:
            max_digits = self._get_max_digits()
            self.selected_digit = (self.selected_digit + 1) % max_digits
            print(f"Selected: {self.selected_element.upper()} digit {self.selected_digit}")

    def _get_max_digits(self):
        """Get maximum number of digits for selected element"""
        if self.selected_element in ['prog', 'verb', 'noun']:
            return 2
        else:  # registers
            return 5

    def _set_digit(self, digit):
        """Set the currently selected digit to a value"""
        with self.state.lock:
            if self.selected_element == 'prog':
                self.state.prog[self.selected_digit] = digit
            elif self.selected_element == 'verb':
                self.state.verb[self.selected_digit] = digit
            elif self.selected_element == 'noun':
                self.state.noun[self.selected_digit] = digit
            elif self.selected_element == 'r1':
                self.state.r1[self.selected_digit] = digit
            elif self.selected_element == 'r2':
                self.state.r2[self.selected_digit] = digit
            elif self.selected_element == 'r3':
                self.state.r3[self.selected_digit] = digit

        print(f"Set {self.selected_element.upper()}[{self.selected_digit}] = {digit}")

        # Auto-advance to next digit
        max_digits = self._get_max_digits()
        self.selected_digit = (self.selected_digit + 1) % max_digits

    def _set_sign(self, sign):
        """Set sign for currently selected register"""
        if self.selected_element not in ['r1', 'r2', 'r3']:
            print("Sign can only be set on registers (R1, R2, R3)")
            return

        with self.state.lock:
            if self.selected_element == 'r1':
                self.state.r1_sign = sign
            elif self.selected_element == 'r2':
                self.state.r2_sign = sign
            elif self.selected_element == 'r3':
                self.state.r3_sign = sign

        print(f"Set {self.selected_element.upper()} sign = {sign}")

    def pattern_blank(self):
        """Blank all displays"""
        with self.state.lock:
            self.state.prog = [0, 0]
            self.state.verb = [0, 0]
            self.state.noun = [0, 0]
            self.state.r1 = [0, 0, 0, 0, 0]
            self.state.r2 = [0, 0, 0, 0, 0]
            self.state.r3 = [0, 0, 0, 0, 0]
            self.state.r1_sign = None
            self.state.r2_sign = None
            self.state.r3_sign = None
            self.state.comp_acty = False

    def pattern_all_eights(self):
        """Display 88888 in all registers (lamp test)"""
        with self.state.lock:
            self.state.prog = [8, 8]
            self.state.verb = [8, 8]
            self.state.noun = [8, 8]
            self.state.r1 = [8, 8, 8, 8, 8]
            self.state.r2 = [8, 8, 8, 8, 8]
            self.state.r3 = [8, 8, 8, 8, 8]
            self.state.r1_sign = '+'
            self.state.r2_sign = '-'
            self.state.r3_sign = '+'
            self.state.comp_acty = True

    def pattern_test(self):
        """Display test pattern: VERB 16 NOUN 36 (common AGC display)"""
        with self.state.lock:
            self.state.prog = [0, 0]
            self.state.verb = [1, 6]
            self.state.noun = [3, 6]
            self.state.r1 = [0, 0, 0, 0, 0]
            self.state.r2 = [0, 0, 0, 0, 0]
            self.state.r3 = [0, 0, 0, 0, 0]
            self.state.r1_sign = '+'
            self.state.r2_sign = '+'
            self.state.r3_sign = '+'
            self.state.comp_acty = False

    def pattern_counting(self):
        """Display counting pattern"""
        with self.state.lock:
            self.state.prog = [1, 2]
            self.state.verb = [3, 4]
            self.state.noun = [5, 6]
            self.state.r1 = [1, 2, 3, 4, 5]
            self.state.r2 = [6, 7, 8, 9, 0]
            self.state.r3 = [9, 8, 7, 6, 5]
            self.state.r1_sign = '+'
            self.state.r2_sign = '-'
            self.state.r3_sign = None
            self.state.comp_acty = True


if __name__ == '__main__':
    # Test simulator
    from dsky_display import DSKYDisplay
    from dsky_config import load_config

    try:
        config = load_config('config/dsky_config.yaml')

        # Enable simulation mode
        config._config['display']['simulation_mode'] = True

        display = DSKYDisplay(config)
        simulator = DSKYSimulator(display.state)

        # Start with test pattern
        simulator.pattern_test()

        print("Starting simulation mode...")
        display.run(simulator=simulator)

    except Exception as e:
        import sys
        import traceback
        print(f"Error: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)
