# Apollo DSKY Display System - Phase 1

A functional replica of the Apollo Guidance Computer's DSKY (Display/Keyboard) module display system. This implementation provides a pygame-based GUI that interfaces with the Virtual AGC (yaAGC) software.

## Features Implemented (Phase 1)

- ✅ pygame GUI display (480x800 resolution)
- ✅ 7-segment digit rendering using DSEG7 font
- ✅ PROG, VERB, NOUN displays (2 digits each)
- ✅ Three 5-digit registers (R1, R2, R3) with sign indicators (+/-)
- ✅ COMP ACTY (Computer Activity) indicator
- ✅ Channel 10 and 11 communication from yaAGC
- ✅ YAML configuration file system
- ✅ Simulation mode for testing without yaAGC
- ✅ Error overlay when yaAGC disconnected
- ✅ Automatic reconnection to yaAGC

## Installation

### Requirements

- Python 3.7 or higher
- pygame 2.0.0+
- PyYAML 5.4.0+

### Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify font installation:**
   The DSEG7 font should already be in `fonts/DSEG7Classic-Regular.ttf`. If missing, download from:
   https://github.com/keshikan/DSEG/raw/master/fonts/DSEG7Classic-Regular.ttf

3. **Test configuration:**
   ```bash
   python dsky_config.py
   ```

## Usage

### Simulation Mode (No yaAGC Required)

Run the display in simulation mode for testing:

```bash
python dsky_main.py --simulate
```

**Keyboard Controls in Simulation Mode:**
- `0-9`: Set selected digit
- `F1`: Blank display
- `F2`: All eights (lamp test)
- `F3`: Test pattern (VERB 16 NOUN 36)
- `F4`: Count animation
- `P`: Select PROG
- `V`: Select VERB
- `N`: Select NOUN
- `R`: Select Register (cycles R1→R2→R3)
- `+`: Set positive sign on selected register
- `-`: Set negative sign on selected register
- `C`: Toggle COMP ACTY
- `E`: Toggle error display
- `Arrow Keys`: Navigate between digits
- `ESC`: Exit

### With yaAGC (Real AGC Simulation)

1. **Start yaAGC** (in separate terminal):
   ```bash
   yaAGC --core=Luminary099.bin --port=19799 --cfg=LM.ini
   ```

2. **Start DSKY display:**
   ```bash
   python dsky_main.py
   ```

3. **With custom host/port:**
   ```bash
   python dsky_main.py --host 192.168.1.10 --port 19697
   ```

## Configuration

Edit `config/dsky_config.yaml` to customize:

- Display resolution and colors
- Font sizes
- Element positions on screen
- yaAGC connection settings
- FPS and performance settings

## Project Structure

```
DSKY_v1/
├── dsky_main.py              # Main entry point
├── dsky_display.py           # pygame rendering engine
├── dsky_config.py            # Configuration system
├── dsky_channel_decoder.py   # Channel 10/11 protocol decoder
├── dsky_simulator.py         # Simulation mode
├── piPeripheral.py           # Original Virtual AGC framework (reference)
├── config/
│   └── dsky_config.yaml      # Configuration file
├── fonts/
│   └── DSEG7Classic-Regular.ttf  # 7-segment display font
├── requirements.txt          # Python dependencies
├── CLAUDE.md                 # Development guide
└── README.md                 # This file
```

## Architecture

### Display State

The `DisplayState` class manages all display elements:
- PROG (Major Mode): 2 digits
- VERB: 2 digits
- NOUN: 2 digits
- R1, R2, R3: 5 digits each with optional +/- sign
- COMP ACTY indicator
- Connection status

### Communication

- Main thread: pygame display loop (60 FPS)
- Background thread: yaAGC TCP socket communication
- Thread-safe queue for data exchange
- Automatic reconnection on connection loss

### Channel Decoding

**Channel 10 Format:** `AAAABCCCCCDDDDD` (15 bits)
- AAAA: Relay code (which digit pair)
- B: Sign bit
- CCCCC: First digit
- DDDDD: Second digit

**Relay Codes:**
- 11: PROG (M1, M2)
- 10: VERB (V1, V2)
- 9: NOUN (N1, N2)
- 8, 7, 6: R1 digits
- 5, 4, 3: R2 digits
- 2, 1: R3 digits

## Testing

### Test Configuration Loading
```bash
python dsky_config.py
```

### Test Channel Decoder
```bash
python dsky_channel_decoder.py
```

### Test Display Rendering
```bash
python dsky_display.py
```

### Test Simulation Mode
```bash
python dsky_simulator.py
```

## Known Issues / Future Work

### Phase 2 (Planned)
- LED indicator lamps (16 WS2812B LEDs)
- Physical GPIO control for LEDs
- Complete indicator lamp mapping

### Phase 3 (Planned)
- Verb/Noun flashing (Channel 163)
- KEY REL and OPR ERR flashing
- Lamp test functionality (Verb 35)

### Phase 4 (Planned)
- Raspberry Pi Pico keyboard interface
- USB HID keyboard emulation
- 19-key input handling

## Troubleshooting

**"Font not found" warning:**
- Download DSEG7 font from https://github.com/keshikan/DSEG
- Place in `fonts/DSEG7Classic-Regular.ttf`
- System monospace font will be used as fallback

**"Connection timeout" errors:**
- Verify yaAGC is running on the specified host/port
- Check firewall settings
- Try `--host localhost --port 19799` explicitly

**Display not updating:**
- Check if yaAGC is sending data to Channel 10
- Enable DEBUG logging in config
- Try simulation mode to verify display rendering works

**Low frame rate:**
- Reduce FPS in config (try 30 instead of 60)
- Enable slow_mode in config for very slow systems

## References

- [Virtual AGC Project](https://www.ibiblio.org/apollo/)
- [Virtual AGC Developer Documentation](https://www.ibiblio.org/apollo/developer.html)
- [DSEG 7-Segment Font](https://github.com/keshikan/DSEG)
- Product Requirements: `DSKY_Product_Requirements_Document.md`
- Development Guide: `CLAUDE.md`

## License

This project uses the piPeripheral.py framework from the Virtual AGC project (public domain).
DSEG7 font is licensed under SIL Open Font License 1.1.

## Acknowledgments

- Ron Burkey and the Virtual AGC project team
- DSEG font by Keshikan
- Apollo Guidance Computer engineers and astronauts
