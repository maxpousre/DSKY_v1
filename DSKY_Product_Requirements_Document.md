# Product Requirements Document: Apollo DSKY Replica System

**Project Name:** Apollo DSKY Display and Keyboard Module  
**Version:** 1.0  
**Date:** January 10, 2026  
**Target Platform:** Raspberry Pi 4 (Main Controller) + Raspberry Pi Pico (Keyboard Interface)

---

## 1. Project Overview

### 1.1 Purpose
Create a functional replica of the Apollo Guidance Computer's DSKY (Display/Keyboard) module for educational and display purposes. The system will interface with the Virtual AGC (yaAGC) software to provide authentic visual outputs and keyboard inputs.

### 1.2 Goals
- Replicate DSKY visual outputs using a pygame-based GUI
- Control physical indicator lamps using addressable LEDs
- Provide keyboard input functionality via Raspberry Pi Pico
- Ensure easy configurability and modification for prototyping
- Enable testing and validation against existing yaDSKY software

---

## 2. System Architecture

### 2.1 Hardware Components
- **Raspberry Pi 4**: Main controller running:
  - Raspberry Pi OS
  - Virtual AGC (yaAGC) software
  - Custom pygame GUI application
  - LED strip control
- **Raspberry Pi Pico**: Keyboard interface
  - Acts as USB HID keyboard
  - Interfaces with 19 physical keys
  - Communicates with Pi 4 via USB
- **WS2812B LED Strip**: 16 addressable LEDs for indicator lamps
  - Connected to GPIO 4 (configurable)
  - One LED per indicator lamp

### 2.2 Software Architecture
- **Communication Layer**: Based on piPeripheral.py framework
- **Display Layer**: pygame GUI (480x800 resolution)
- **LED Control Layer**: WS2812B driver
- **Keyboard Layer**: USB HID interface (Pico)
- **Configuration Layer**: File-based configuration system

---

## 3. Development Phases

### Phase 1: Display Output System
**Deliverables:**
- pygame GUI displaying all numerical segments
- 7-segment digit rendering (PROG, VERB, NOUN, R1, R2, R3)
- Sign indicators (+/-) for registers
- COMP ACTY indicator (GUI-based)
- Channel 10 communication from yaAGC
- Configuration file implementation
- Simulation mode for testing without yaAGC

### Phase 2: LED Indicator System
**Deliverables:**
- WS2812B LED strip control
- 16 indicator lamp mappings
- Channel 10, 11, and 13 communication
- LED brightness control
- Easily modifiable LED-to-indicator mapping
- Integration with Phase 1 display

### Phase 3: Dynamic Behaviors
**Deliverables:**
- Verb/Noun flashing implementation
- Channel 163 support for modulated indicators
- KEY REL and OPR ERR flashing
- Lamp test functionality (Verb 35)
- Full integration testing with yaDSKY

### Phase 4: Keyboard Input System
**Deliverables:**
- Raspberry Pi Pico firmware (MicroPython)
- USB HID keyboard emulation
- 19-key input handling
- Channel 15 and 32 communication to yaAGC
- Wiring documentation
- Full system integration

---

## 4. Display Requirements (Phase 1)

### 4.1 Screen Specifications
- **Resolution**: 480x800 pixels
- **Display Mode**: Windowed (for prototype)
- **Background Color**: Black (#000000)
- **Foreground Color**: Bright green (configurable, default: #00FF00)
- **Font**: DSEG 7-segment style font

### 4.2 Display Elements

#### 4.2.1 Numerical Displays (Channel 10)
All digits use 7-segment representation:
- **PROG (Major Mode)**: 2 digits (M1, M2)
- **VERB**: 2 digits (V1, V2)
- **NOUN**: 2 digits (N1, N2)
- **Register 1 (R1)**: 5 digits + sign indicator
- **Register 2 (R2)**: 5 digits + sign indicator
- **Register 3 (R3)**: 5 digits + sign indicator

#### 4.2.2 Sign Indicators (Channel 10)
- Each register (R1, R2, R3) has dedicated +/- indicators
- Display logic:
  - Both bits zero = blank
  - "+" bit set = show "+"
  - "-" bit set = show "-"

#### 4.2.3 Computer Activity Indicator
- **COMP ACTY**: GUI-based indicator (not LED)
- Source: Channel 11
- Visual representation: Similar styling to other indicators

### 4.3 Error Handling
- **yaAGC Connection Lost**: Display error overlay on GUI
- **Error Message**: Clear, visible notification
- **Recovery**: Automatic reconnection attempt

### 4.4 Simulation Mode
- Ability to run GUI without yaAGC connection
- Manual control of display states for testing
- Toggle between simulation and live mode

---

## 5. LED Indicator Requirements (Phase 2)

### 5.1 Hardware Specifications
- **LED Type**: WS2812B addressable LEDs
- **Quantity**: 16 LEDs
- **GPIO Pin**: GPIO 4 (configurable in config file)
- **Control Protocol**: WS2812B serial protocol

### 5.2 Indicator Lamp Mapping

#### 5.2.1 Channel 10 Indicators
1. PRIO DISP (Priority Display)
2. NO DAP (No Digital Autopilot)
3. VEL (Velocity)
4. NO ATT (No Attitude)
5. ALT (Altitude)
6. GIMBAL LOCK
7. TRACKER
8. PROG (Program Alarm)

#### 5.2.2 Channel 11 Indicators
9. UPLINK ACTY
10. TEMP
11. KEY REL
12. OPR ERR

#### 5.2.3 Channel 13 Indicators
13. STBY (Standby)
14. RESTART

**Note**: COMP ACTY is GUI-only, not an LED

### 5.3 LED Control Features
- **Mapping Configuration**: LED index to indicator name mapping in config file
- **Brightness Control**: Adjustable via configuration
- **Color Control**: Per-indicator color configuration (if desired)
- **Easy Remapping**: Change physical LED positions without code changes

---

## 6. Dynamic Behavior Requirements (Phase 3)

### 6.1 Flashing Behaviors (Channel 163)
- **VERB/NOUN Flashing**: Square-wave modulation when crew input required
- **KEY REL Flashing**: Modulated display
- **OPR ERR Flashing**: Modulated display
- **Timing**: Based on Channel 163 signals from yaAGC

### 6.2 Lamp Test (Verb 35)
- **Duration**: 5 seconds
- **Effect**: All lamps and display segments illuminate
- **Includes**: 
  - All 7-segment displays (all segments on)
  - All LED indicators
  - All sign indicators
  - COMP ACTY indicator

---

## 7. Keyboard Input Requirements (Phase 4)

### 7.1 Raspberry Pi Pico Specifications
- **Language**: MicroPython
- **Interface**: USB HID Keyboard emulation
- **Connection**: USB to Raspberry Pi 4
- **Key Count**: 19 physical keys

### 7.2 Key Mapping

#### 7.2.1 Channel 15 Keys (18 keys, 5-bit keycode)
| Key | Octal Code | Binary Code | Description |
|-----|-----------|-------------|-------------|
| 0 | 0o20 | 10000 | Number 0 |
| 1 | 0o01 | 00001 | Number 1 |
| 2 | 0o02 | 00010 | Number 2 |
| 3 | 0o03 | 00011 | Number 3 |
| 4 | 0o04 | 00100 | Number 4 |
| 5 | 0o05 | 00101 | Number 5 |
| 6 | 0o06 | 00110 | Number 6 |
| 7 | 0o07 | 00111 | Number 7 |
| 8 | 0o10 | 01000 | Number 8 |
| 9 | 0o11 | 01001 | Number 9 |
| VERB | 0o21 | 10001 | Verb key |
| NOUN | 0o37 | 11111 | Noun key |
| ENTR | 0o34 | 11100 | Enter key |
| CLR | 0o36 | 11110 | Clear key |
| KEY REL | 0o31 | 11001 | Key Release |
| RSET | 0o22 | 10010 | Reset key |
| + | 0o32 | 11010 | Plus sign |
| - | 0o33 | 11011 | Minus sign |

**Bitmask for Channel 15**: 0o37 (binary 11111)

#### 7.2.2 Channel 32 Key (1 key)
| Key | Channel | Bit | Logic | Bitmask |
|-----|---------|-----|-------|---------|
| PRO | 32 | 14 | Inverted (0=pressed, 1=released) | 0o20000 |

### 7.3 Key Behavior
- Keycode appears when key is newly pressed
- Returns to neutral state when released (non-latching)
- No key repeat/auto-repeat functionality

### 7.4 Communication Protocol
- Use piPeripheral.py framework format
- Return format: List of tuples `[(channel, value, mask)]`
- Example: KEY REL press = `[(0o15, 0o31, 0o37)]`

---

## 8. Configuration Requirements

### 8.1 Configuration File Format
- **Format**: INI, JSON, or YAML (developer choice)
- **Location**: Same directory as main application
- **Name**: `dsky_config.ini` (or similar)

### 8.2 Required Configuration Parameters

#### 8.2.1 Display Configuration
```
[Display]
resolution_width = 480
resolution_height = 800
background_color = #000000
foreground_color = #00FF00
font_name = DSEG
window_mode = windowed  # or fullscreen
simulation_mode = false
```

#### 8.2.2 LED Configuration
```
[LEDs]
gpio_pin = 4
led_count = 16
brightness = 128  # 0-255
led_mapping = 0:PRIO_DISP, 1:NO_DAP, 2:VEL, 3:NO_ATT, 4:ALT, 5:GIMBAL_LOCK, ...
```

#### 8.2.3 Communication Configuration
```
[Communication]
yaagc_host = localhost
yaagc_port = 19697
reconnect_interval = 5  # seconds
timeout = 10  # seconds
```

#### 8.2.4 Keyboard Configuration (if needed)
```
[Keyboard]
enable_keyboard = true
pico_device_path = /dev/ttyACM0  # or auto-detect
```

### 8.3 Configuration Validation
- Validate configuration on startup
- Display clear error messages for invalid values
- Fall back to sensible defaults when possible

---

## 9. Communication Protocol Requirements

### 9.1 yaAGC Interface
- **Base Framework**: piPeripheral.py from Virtual AGC project
- **Protocol**: TCP/IP socket communication
- **Data Format**: As defined by Virtual AGC specification

### 9.2 Channel Monitoring

#### 9.2.1 Output Channels (AGC → DSKY)
- **Channel 10**: Numerical displays, signs, spacecraft alerts
- **Channel 11**: Computer status indicators
- **Channel 13**: Additional status indicators
- **Channel 163**: Dynamic behavior control (flashing)

#### 9.2.2 Input Channels (DSKY → AGC)
- **Channel 15**: Standard keypad (18 keys)
- **Channel 32**: PRO key (bit 14)

### 9.3 Error Handling
- Connection retry logic
- Timeout handling
- Invalid data packet handling
- Graceful degradation when yaAGC unavailable

---

## 10. Testing Requirements

### 10.1 Phase 1 Testing
- Display all digit combinations (0-9 for each position)
- Test sign indicators (+, -, blank)
- Test COMP ACTY indicator on/off
- Verify colors and font rendering
- Test simulation mode
- Test error overlay display

### 10.2 Phase 2 Testing
- Individual LED control
- All LEDs on/off simultaneously
- LED brightness levels
- LED remapping functionality
- Integration with Phase 1 display

### 10.3 Phase 3 Testing
- Flashing behavior timing accuracy
- Lamp test (Verb 35) functionality
- Channel 163 signal processing
- All dynamic behaviors with yaDSKY

### 10.4 Phase 4 Testing
- All 19 key inputs individually
- Simultaneous key press handling (if applicable)
- USB HID recognition
- Channel 15 and 32 communication
- Full integration with yaAGC running actual programs

### 10.5 Integration Testing
- Test against yaDSKY software
- Run actual AGC programs (e.g., P00, P20)
- Verify all indicators respond correctly
- Stress test (rapid key presses, rapid display updates)

---

## 11. Documentation Requirements

### 11.1 Code Documentation
- Clear module/class/function comments
- Inline comments for complex logic
- README.md with project overview

### 11.2 Wiring Documentation (Phase 4)
- GPIO pin connections for keyboard
- Wiring diagram for 19-key matrix
- Pin-to-key mapping table
- Pull-up/pull-down resistor requirements

### 11.3 Configuration Documentation
- All configuration parameters explained
- Example configuration file with comments
- Default values documented

---

## 12. Code Organization Requirements

### 12.1 Project Structure
Modular design with clear separation of concerns:
- **Main Application**: Entry point and orchestration
- **Display Module**: pygame GUI handling
- **LED Module**: WS2812B control
- **Communication Module**: yaAGC interface (piPeripheral.py based)
- **Configuration Module**: Config file loading and validation
- **Keyboard Module**: Pico firmware (separate project)

### 12.2 Code Quality
- Clear variable and function names
- Consistent coding style
- Error handling throughout
- Logging for debugging

### 12.3 Variable Organization
- All configurable variables in configuration file
- Magic numbers avoided
- Constants clearly defined

---

## 13. Success Criteria

### 13.1 Phase 1 Success
- [ ] GUI displays all numerical digits correctly
- [ ] Sign indicators function properly
- [ ] COMP ACTY indicator works
- [ ] Configuration file loads successfully
- [ ] Simulation mode operates independently
- [ ] Error overlay appears when yaAGC disconnected

### 13.2 Phase 2 Success
- [ ] All 16 LEDs controllable individually
- [ ] LED mapping easily changeable in config
- [ ] LEDs respond to correct channels
- [ ] Brightness adjustable

### 13.3 Phase 3 Success
- [ ] Flashing behaviors match specification
- [ ] Lamp test illuminates everything
- [ ] Channel 163 processed correctly
- [ ] Synchronization with yaDSKY verified

### 13.4 Phase 4 Success
- [ ] All 19 keys send correct codes
- [ ] Pico recognized as USB keyboard
- [ ] yaAGC receives key inputs correctly
- [ ] Can operate actual AGC programs

### 13.5 Overall Success
- [ ] Complete system runs actual AGC missions
- [ ] All indicators and displays match real DSKY behavior
- [ ] System stable for extended operation
- [ ] Easy to modify and configure

---

## 14. Technical Constraints

### 14.1 Performance
- Display refresh rate: Minimum 30 FPS
- LED update latency: Maximum 50ms
- Key input response: Maximum 100ms

### 14.2 Compatibility
- Raspberry Pi OS (current version)
- Python 3.7 or higher
- Virtual AGC project compatibility

### 14.3 Scalability
- Design allows for future hardware changes
- Easy transition to different display technology
- Portable to different platforms if needed

---

## 15. Future Considerations (Out of Scope for Initial Development)

- Audio feedback for key presses
- Additional authentic DSKY features
- Network-based yaAGC connection
- Multiple DSKY instances
- Hardware enclosure design
- Performance optimization in compiled language

---

**END OF PRODUCT REQUIREMENTS DOCUMENT**
