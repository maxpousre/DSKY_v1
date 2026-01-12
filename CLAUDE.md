# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Apollo DSKY (Display/Keyboard) replica system that interfaces with the Virtual AGC (yaAGC) software. The system uses a Raspberry Pi 4 as the main controller with a pygame-based GUI, WS2812B LED strips for indicator lamps, and a Raspberry Pi Pico for keyboard input.

**Target Platform:** Raspberry Pi 4 + Raspberry Pi Pico
**Language:** Python 3.7+
**Operating System:** Raspberry Pi OS

## Architecture

### Communication Framework

The system is built on the `piPeripheral.py` framework from the Virtual AGC project, which handles TCP/IP socket communication with yaAGC. This framework provides:

- **Event loop architecture:** Continuously polls for data from yaAGC and sends keyboard inputs
- **Packet-based protocol:** 4-byte packets for bi-directional communication
- **Channel-based I/O:** AGC communicates via numbered channels (e.g., Channel 10 for display, Channel 15 for keyboard input)
- **Non-blocking sockets:** Asynchronous I/O handling

### Key Communication Channels

**Output Channels (AGC → DSKY):**
- Channel 10: Numerical displays, sign indicators, and spacecraft alerts
- Channel 11: Computer status indicators (UPLINK ACTY, TEMP, KEY REL, OPR ERR, COMP ACTY)
- Channel 13: STBY and RESTART indicators
- Channel 163: Dynamic behavior control (flashing patterns for VERB/NOUN, KEY REL, OPR ERR)

**Input Channels (DSKY → AGC):**
- Channel 15: Standard keypad (18 keys, 5-bit keycodes with bitmask 0o37)
- Channel 32: PRO key (bit 14, inverted logic - 0=pressed, 1=released, bitmask 0o20000)

### Data Format

Values are transmitted in 15-bit 1's-complement format (see `toOnesComplement()` function in piPeripheral.py:214-217). The `packetize()` function (piPeripheral.py:403-423) converts (channel, value, mask) tuples into 4-byte packets for transmission.

## Development Phases

The project is structured in 4 phases:

**Phase 1: Display Output System**
- pygame GUI with 7-segment digits (PROG, VERB, NOUN, R1, R2, R3)
- Sign indicators (+/-) for registers
- COMP ACTY indicator (GUI-based, not LED)
- Channel 10 communication
- Simulation mode for testing without yaAGC

**Phase 2: LED Indicator System**
- WS2812B LED strip control (16 LEDs on GPIO 4)
- LED-to-indicator mapping via configuration file
- Channels 10, 11, and 13 support

**Phase 3: Dynamic Behaviors**
- Verb/Noun flashing (Channel 163)
- KEY REL and OPR ERR flashing
- Lamp test functionality (Verb 35 - all segments and LEDs on for 5 seconds)

**Phase 4: Keyboard Input System**
- Raspberry Pi Pico firmware (MicroPython)
- USB HID keyboard emulation
- 19-key input handling with proper channel/keycode mapping

## Display Specifications

**Resolution:** 480x800 pixels
**7-Segment Elements:**
- PROG (Major Mode): 2 digits
- VERB: 2 digits
- NOUN: 2 digits
- R1/R2/R3 registers: 5 digits each with +/- sign indicators

**Sign Indicator Logic:**
- Both bits zero = blank
- "+" bit set = show "+"
- "-" bit set = show "-"

## Key Mapping Reference

All keys use Channel 15 except PRO (Channel 32):

```
Numbers:  0=0o20, 1=0o01, 2=0o02, 3=0o03, 4=0o04
          5=0o05, 6=0o06, 7=0o07, 8=0o10, 9=0o11
Actions:  VERB=0o21, NOUN=0o37, ENTR=0o34, CLR=0o36
          KEY REL=0o31, RSET=0o22, +=0o32, -=0o33
Special:  PRO (Channel 32, bit 14, inverted logic)
```

Keyboard input format: `[(channel, value, mask)]`
Example: KEY REL press = `[(0o15, 0o31, 0o37)]`

## Configuration System

Configuration should use file-based settings (INI/JSON/YAML) with parameters for:

**Display:**
- Resolution, colors, font, window mode, simulation mode

**LEDs:**
- GPIO pin (default: 4), LED count (16), brightness (0-255)
- LED mapping: physical LED index to indicator name

**Communication:**
- yaAGC host (default: localhost), port (default: 19799 for AGC, 19899 for AGS)
- Reconnection interval, timeout

## Important Implementation Notes

### Custom Functions to Implement

When extending `piPeripheral.py`, you must implement:

1. **`inputsForAGx()`** (line 229): Returns list of tuples `[(channel, value, mask), ...]` for data to send to yaAGC
2. **`outputFromAGx(channel, value)`** (line 349): Processes output data received from yaAGC

### Connection Handling

- The `connectToAGC()` function (line 373) establishes TCP connection with retries (max 10 attempts)
- Event loop is in lines 432-516, handling bidirectional communication
- Non-blocking socket operations accumulate packet data over multiple reads

### Error Handling Requirements

- Display error overlay when yaAGC connection is lost
- Implement automatic reconnection attempts
- Validate configuration on startup with clear error messages
- Handle invalid/corrupted packets (see lines 475-493)

## Testing Strategy

**Without yaAGC:**
- Use simulation mode to manually control display states
- Test individual LED control and brightness
- Validate keyboard input encoding

**With yaAGC:**
- Run actual AGC programs (P00, P20, etc.)
- Test lamp test (Verb 35)
- Verify flashing behaviors
- Validate against yaDSKY reference implementation

## Performance Requirements

- Display refresh: minimum 30 FPS
- LED update latency: maximum 50ms
- Key input response: maximum 100ms

## Running yaAGC

Example command to run Virtual AGC for testing:
```bash
yaAGC --core=Luminary099.bin --port=19797 --cfg=LM.ini
```

Then run your DSKY peripheral to connect to it.
