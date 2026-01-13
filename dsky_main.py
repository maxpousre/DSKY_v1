#!/usr/bin/env python3
"""
Apollo DSKY Display System - Phase 1
Main entry point and application orchestration
"""

import sys
import argparse
import threading
import queue
import socket
import time
from dsky_config import load_config
from dsky_display import DSKYDisplay
from dsky_simulator import DSKYSimulator
from dsky_channel_decoder import decode_channel10, decode_channel11


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Apollo DSKY Display System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python dsky_main.py --simulate              Run in simulation mode
  python dsky_main.py                         Connect to yaAGC on localhost:19799
  python dsky_main.py --host 192.168.1.10     Connect to yaAGC on remote host
  python dsky_main.py --port 19697            Connect to yaAGC on custom port
        """
    )
    parser.add_argument('--config', default='config/dsky_config.yaml',
                        help='Path to configuration file (default: config/dsky_config.yaml)')
    parser.add_argument('--simulate', action='store_true',
                        help='Run in simulation mode (no yaAGC connection)')
    parser.add_argument('--host', help='yaAGC host address (overrides config)')
    parser.add_argument('--port', type=int, help='yaAGC port (overrides config)')
    return parser.parse_args()


class AGCCommunicator:
    """
    Handles TCP socket communication with yaAGC
    Adapted from piPeripheral.py framework
    """

    def __init__(self, config, display_state):
        self.config = config
        self.display_state = display_state
        self.host = config.communication.yaagc.host
        self.port = config.communication.yaagc.port
        self.timeout = config.communication.yaagc.timeout
        self.reconnect_interval = config.communication.yaagc.reconnect_interval
        self.reconnect_max_attempts = config.communication.yaagc.reconnect_max_attempts
        self.pulse = config.communication.pulse_rate

        self.socket = None
        self.running = False
        self.last_packet_time = time.time()

    def connect(self):
        """Connect to yaAGC with retry logic"""
        attempts = 0
        max_attempts = self.reconnect_max_attempts if self.reconnect_max_attempts > 0 else float('inf')

        print(f"Connecting to yaAGC at {self.host}:{self.port}...")

        while attempts < max_attempts:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(self.timeout)  # Set timeout for connection
                self.socket.connect((self.host, self.port))
                print("Connected to yaAGC!")

                # Set to non-blocking after successful connection
                self.socket.setblocking(0)

                # Reset packet timer on successful connection
                self.last_packet_time = time.time()

                with self.display_state.lock:
                    self.display_state.connected = True

                return True

            except socket.error as e:
                attempts += 1
                print(f"Connection attempt {attempts} failed: {e}")

                if attempts < max_attempts:
                    print(f"Retrying in {self.reconnect_interval} seconds...")
                    time.sleep(self.reconnect_interval)
                else:
                    print("Max connection attempts reached.")
                    break

        with self.display_state.lock:
            self.display_state.connected = False

        return False

    def disconnect(self):
        """Close socket connection"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None

        with self.display_state.lock:
            self.display_state.connected = False

    def receive_packet(self):
        """
        Receive and parse a 4-byte packet from yaAGC

        Returns:
            (channel, value) tuple or None if no packet available
        """
        packet_size = 4
        input_buffer = bytearray(packet_size)
        left_to_read = packet_size
        view = memoryview(input_buffer)

        # Try to read 4 bytes (non-blocking)
        try:
            while left_to_read > 0:
                num_bytes = self.socket.recv_into(view, left_to_read)
                if num_bytes == 0:
                    return None
                view = view[num_bytes:]
                left_to_read -= num_bytes

            # Full packet received - parse it
            # Sanity check
            if (input_buffer[0] & 0xF0) != 0x00:
                return None
            if (input_buffer[1] & 0xC0) != 0x40:
                return None
            if (input_buffer[2] & 0xC0) != 0x80:
                return None
            if (input_buffer[3] & 0xC0) != 0xC0:
                return None

            # Parse channel and value
            channel = (input_buffer[0] & 0x0F) << 3
            channel |= (input_buffer[1] & 0x38) >> 3
            value = (input_buffer[1] & 0x07) << 12
            value |= (input_buffer[2] & 0x3F) << 6
            value |= (input_buffer[3] & 0x3F)

            self.last_packet_time = time.time()
            return (channel, value)

        except socket.timeout:
            return None
        except BlockingIOError:
            return None
        except Exception as e:
            print(f"Packet receive error: {e}")
            return None

    def communication_loop(self):
        """Main communication loop running in background thread"""
        self.running = True

        # Connect to yaAGC
        if not self.connect():
            print("Failed to connect to yaAGC")
            self.running = False
            return

        # Main loop
        while self.running:
            # Try to receive packet
            packet = self.receive_packet()
            if packet:
                channel, value = packet
                self.process_packet(channel, value)

            # Note: We don't check for timeout based on last packet time
            # because yaAGC only sends packets when data changes.
            # Connection errors are caught in receive_packet() instead.

            # Small sleep to avoid busy-waiting
            time.sleep(self.pulse)

    def process_packet(self, channel, value):
        """Process received packet and update display state"""
        # Convert channel to octal for easier identification
        channel_octal = channel

        if channel_octal == 0o10:  # Channel 10 - Display data
            decode_channel10(value, self.display_state)

        elif channel_octal == 0o11:  # Channel 11 - COMP ACTY and indicators
            decode_channel11(value, self.display_state)

        elif channel_octal == 0o13:  # Channel 13 - Additional indicators
            # Phase 2 - LED indicators
            pass

        elif channel_octal == 0o163:  # Channel 163 - Flashing behavior
            # Phase 3 - Dynamic behaviors
            pass

    def stop(self):
        """Stop communication loop"""
        self.running = False
        self.disconnect()


def main():
    """Main application entry point"""
    args = parse_arguments()

    # Load configuration
    try:
        config = load_config(args.config)
        print(f"Loaded configuration from {args.config}")
    except Exception as e:
        print(f"Error loading configuration: {e}", file=sys.stderr)
        sys.exit(1)

    # Override config with command-line arguments
    if args.simulate:
        config._config['display']['simulation_mode'] = True
        print("Running in SIMULATION MODE")
    if args.host:
        config._config['communication']['yaagc']['host'] = args.host
        print(f"Overriding yaAGC host: {args.host}")
    if args.port:
        config._config['communication']['yaagc']['port'] = args.port
        print(f"Overriding yaAGC port: {args.port}")

    # Initialize display
    try:
        display = DSKYDisplay(config)
        print(f"Display initialized: {config.display.resolution.width}x{config.display.resolution.height}")
    except Exception as e:
        print(f"Error initializing display: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Run in simulation mode or with yaAGC communication
    if config.display.simulation_mode:
        # Simulation mode - manual keyboard control
        simulator = DSKYSimulator(display.state)
        simulator.pattern_test()  # Start with test pattern
        display.run(simulator=simulator)

    else:
        # Communication mode - connect to yaAGC
        communicator = AGCCommunicator(config, display.state)

        # Start communication thread
        comm_thread = threading.Thread(
            target=communicator.communication_loop,
            daemon=True
        )
        comm_thread.start()
        print("Communication thread started")

        try:
            # Run display loop in main thread
            display.run()
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            communicator.stop()

    print("DSKY Display System terminated.")


if __name__ == '__main__':
    main()
