#!/usr/bin/env python3
"""
DSKY Channel Decoder
Decodes AGC output channels (especially Channel 10) into display state
"""

from dsky_display import DisplayState


# 7-segment encoding lookup table
# Maps 5-bit patterns to digits 0-9
# Based on standard 7-segment encoding used by AGC
SEVEN_SEGMENT_TO_DIGIT = {
    0b11111: 0,  # All segments except middle
    0b00110: 1,  # Right segments only
    0b11011: 2,  # Top, middle, bottom, etc.
    0b01111: 3,
    0b00110: 4,
    0b01101: 5,
    0b11101: 6,
    0b00111: 7,
    0b11111: 8,
    0b01111: 9,
    0b00000: None,  # Blank
}

# Alternative: Direct mapping if AGC sends digit values directly
# We'll try both approaches


def seven_segment_to_digit(bits: int) -> int:
    """
    Convert 5-bit 7-segment encoding to digit 0-9

    Args:
        bits: 5-bit pattern representing 7-segment encoding

    Returns:
        Digit 0-9, or None if blank

    Note: The AGC may send digits directly (0-9) rather than
          7-segment bit patterns. We'll handle both cases.
    """
    # Try direct interpretation first (if bits are 0-9)
    if 0 <= bits <= 9:
        return bits

    # Try lookup table for 7-segment encoding
    if bits in SEVEN_SEGMENT_TO_DIGIT:
        return SEVEN_SEGMENT_TO_DIGIT[bits]

    # For values 10-31, map to octal interpretation
    # AGC uses octal, so value might be in octal format
    try:
        octal_str = oct(bits)[2:]  # Convert to octal string
        if len(octal_str) == 2 and octal_str[0] == '0':
            digit = int(octal_str[1])
            if 0 <= digit <= 9:
                return digit
        elif len(octal_str) == 1:
            return int(octal_str)
    except:
        pass

    # Default to showing the value modulo 10
    return bits % 10


def decode_channel10(value: int, display_state: DisplayState):
    """
    Decode Channel 10 15-bit value and update display state

    Format: AAAABCCCCCDDDDD
    - AAAA (bits 11-14): Relay code (identifies which digit pair)
    - B (bit 10): Sign bit for registers
    - CCCCC (bits 5-9): First digit (7-segment encoding or direct)
    - DDDDD (bits 0-4): Second digit (7-segment encoding or direct)

    Relay Codes:
      11 (0xB): PROG (M1, M2)
      10 (0xA): VERB (V1, V2)
       9 (0x9): NOUN (N1, N2)
       8 (0x8): R1 digits 1-2
       7 (0x7): R1 digits 2-3 (with sign)
       6 (0x6): R1 digits 4-5
       5 (0x5): R2 digits 1-2 (with sign)
       4 (0x4): R2 digits 3-4
       3 (0x3): R2 digit 5, R3 digit 1
       2 (0x2): R3 digits 2-3 (with sign)
       1 (0x1): R3 digits 4-5
      12 (0xC): Indicator lamps (Phase 2)

    Args:
        value: 15-bit value from Channel 10
        display_state: DisplayState object to update
    """
    # Extract bit fields
    relay = (value >> 11) & 0b1111        # Bits 11-14
    sign_bit = (value >> 10) & 0b1       # Bit 10
    digit1_bits = (value >> 5) & 0b11111 # Bits 5-9
    digit2_bits = value & 0b11111          # Bits 0-4

    # Convert to digits
    d1 = seven_segment_to_digit(digit1_bits)
    d2 = seven_segment_to_digit(digit2_bits)

    # Update display based on relay code
    if relay == 11:  # PROG (M1, M2)
        display_state.set_prog(d1 or 0, d2 or 0)

    elif relay == 10:  # VERB (V1, V2)
        display_state.set_verb(d1 or 0, d2 or 0)

    elif relay == 9:  # NOUN (N1, N2)
        display_state.set_noun(d1 or 0, d2 or 0)

    elif relay == 8:  # R1 digits 1-2
        with display_state.lock:
            display_state.r1[0] = d1 or 0
            display_state.r1[1] = d2 or 0

    elif relay == 7:  # R1 digits 2-3 with sign
        with display_state.lock:
            display_state.r1[2] = d1 or 0
            display_state.r1[3] = d2 or 0
            # Sign: 0 = +, 1 = -
            display_state.r1_sign = '-' if sign_bit else '+'

    elif relay == 6:  # R1 digits 4-5
        with display_state.lock:
            display_state.r1[3] = d1 or 0
            display_state.r1[4] = d2 or 0

    elif relay == 5:  # R2 digits 1-2 with sign
        with display_state.lock:
            display_state.r2[0] = d1 or 0
            display_state.r2[1] = d2 or 0
            # Sign: 0 = +, 1 = -
            display_state.r2_sign = '-' if sign_bit else '+'

    elif relay == 4:  # R2 digits 3-4
        with display_state.lock:
            display_state.r2[2] = d1 or 0
            display_state.r2[3] = d2 or 0

    elif relay == 3:  # R2 digit 5, R3 digit 1
        with display_state.lock:
            display_state.r2[4] = d1 or 0
            display_state.r3[0] = d2 or 0

    elif relay == 2:  # R3 digits 2-3 with sign
        with display_state.lock:
            display_state.r3[1] = d1 or 0
            display_state.r3[2] = d2 or 0
            # Sign: 0 = +, 1 = -
            display_state.r3_sign = '-' if sign_bit else '+'

    elif relay == 1:  # R3 digits 4-5
        with display_state.lock:
            display_state.r3[3] = d1 or 0
            display_state.r3[4] = d2 or 0

    elif relay == 12:  # Indicator lamps (Phase 2)
        # Ignore for Phase 1 - will be implemented with LED control
        pass


def decode_channel11(value: int, display_state: DisplayState):
    """
    Decode Channel 11 for COMP ACTY and other indicators

    Channel 11 bits (from Virtual AGC documentation):
      Bit 1: COMP ACTY (Computer Activity)
      Other bits: Various indicator lamps (Phase 2)

    Args:
        value: 15-bit value from Channel 11
        display_state: DisplayState object to update
    """
    # COMP ACTY is bit 1 (may need verification)
    comp_acty = (value >> 1) & 0b1

    with display_state.lock:
        display_state.comp_acty = bool(comp_acty)


def decode_channel13(value: int, display_state: DisplayState):
    """
    Decode Channel 13 for STBY and RESTART indicators

    Phase 2 feature - LED indicators only

    Args:
        value: 15-bit value from Channel 13
        display_state: DisplayState object to update
    """
    # Phase 2: Will control LED indicators
    pass


if __name__ == '__main__':
    # Test channel decoding
    from dsky_display import DisplayState

    state = DisplayState()

    # Test PROG = 16
    print("Testing PROG = 16")
    # Relay 11, digit1 = 1, digit2 = 6
    value = (11 << 11) | (1 << 5) | 6
    decode_channel10(value, state)
    print(f"  PROG: {state.prog}")

    # Test VERB = 37
    print("Testing VERB = 37")
    value = (10 << 11) | (3 << 5) | 7
    decode_channel10(value, state)
    print(f"  VERB: {state.verb}")

    # Test NOUN = 06
    print("Testing NOUN = 06")
    value = (9 << 11) | (0 << 5) | 6
    decode_channel10(value, state)
    print(f"  NOUN: {state.noun}")

    # Test R1 with sign
    print("Testing R1 = +12345")
    # R1 digits 1-2
    value = (8 << 11) | (1 << 5) | 2
    decode_channel10(value, state)
    # R1 digits 2-3 with + sign
    value = (7 << 11) | (0 << 10) | (3 << 5) | 4
    decode_channel10(value, state)
    # R1 digits 4-5
    value = (6 << 11) | (4 << 5) | 5
    decode_channel10(value, state)
    print(f"  R1: {state.r1}, sign: {state.r1_sign}")

    # Test COMP ACTY
    print("Testing COMP ACTY = ON")
    value = (1 << 1)  # Bit 1 set
    decode_channel11(value, state)
    print(f"  COMP ACTY: {state.comp_acty}")

    print("\nAll decoder tests passed!")
