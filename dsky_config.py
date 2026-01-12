#!/usr/bin/env python3
"""
DSKY Configuration System
Handles loading and validation of YAML configuration file
"""

import yaml
import os
import sys
from typing import Any, Dict


class Config:
    """Immutable configuration object"""

    def __init__(self, config_dict: Dict[str, Any]):
        self._config = config_dict

    def __getattr__(self, name):
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        return ConfigSection(self._config.get(name, {}))


class ConfigSection:
    """Configuration section with dot notation access"""

    def __init__(self, section_dict: Dict[str, Any]):
        self._section = section_dict

    def __getattr__(self, name):
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        value = self._section.get(name)
        if isinstance(value, dict):
            return ConfigSection(value)
        return value

    def get(self, name, default=None):
        return self._section.get(name, default)


def load_config(config_path: str) -> Config:
    """
    Load and validate YAML configuration file

    Args:
        config_path: Path to configuration YAML file

    Returns:
        Config object with validated settings

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If YAML is malformed
        ValueError: If validation fails
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)

    # Apply defaults
    config_dict = apply_defaults(config_dict)

    # Validate configuration
    validate_config(config_dict)

    return Config(config_dict)


def apply_defaults(config: Dict[str, Any]) -> Dict[str, Any]:
    """Apply default values for missing configuration parameters"""

    defaults = {
        'display': {
            'resolution': {'width': 480, 'height': 800},
            'window_mode': 'windowed',
            'window_title': 'Apollo DSKY Display',
            'colors': {
                'background': '#000000',
                'foreground': '#00FF00',
                'foreground_dim': '#003300',
                'error_overlay': '#FF0000'
            },
            'font': {
                'path': 'fonts/DSEG7Classic-Regular.ttf',
                'size_prog': 48,
                'size_verb_noun': 48,
                'size_register': 36,
                'size_sign': 30
            },
            'fps': 60,
            'simulation_mode': False
        },
        'communication': {
            'yaagc': {
                'host': 'localhost',
                'port': 19799,
                'timeout': 10,
                'reconnect_interval': 5,
                'reconnect_max_attempts': 0
            },
            'pulse_rate': 0.05,
            'slow_mode': False
        },
        'layout': {
            'prog': {'x': 190, 'y': 50, 'spacing': 10},
            'verb': {'x': 100, 'y': 150, 'spacing': 10},
            'noun': {'x': 280, 'y': 150, 'spacing': 10},
            'register_1': {'x': 80, 'y': 300, 'digit_spacing': 8, 'sign_x': 50, 'sign_y': 300},
            'register_2': {'x': 80, 'y': 450, 'digit_spacing': 8, 'sign_x': 50, 'sign_y': 450},
            'register_3': {'x': 80, 'y': 600, 'digit_spacing': 8, 'sign_x': 50, 'sign_y': 600},
            'comp_acty': {'x': 360, 'y': 750, 'width': 100, 'height': 30}
        },
        'error_display': {
            'enabled': True,
            'message': 'yaAGC CONNECTION LOST',
            'blink_rate': 1.0,
            'font_size': 36
        },
        'logging': {
            'enabled': True,
            'level': 'INFO',
            'file': 'dsky.log',
            'console': True
        }
    }

    # Deep merge defaults with provided config
    return deep_merge(defaults, config)


def deep_merge(base: Dict, override: Dict) -> Dict:
    """Recursively merge two dictionaries, with override taking precedence"""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate configuration values

    Raises:
        ValueError: If validation fails
    """
    # Validate display resolution
    width = config['display']['resolution']['width']
    height = config['display']['resolution']['height']
    if not (320 <= width <= 1920) or not (240 <= height <= 1080):
        raise ValueError(f"Invalid resolution: {width}x{height}. Must be 320-1920 x 240-1080")

    # Validate colors are hex format
    for color_name, color_value in config['display']['colors'].items():
        if not isinstance(color_value, str) or not color_value.startswith('#') or len(color_value) != 7:
            raise ValueError(f"Invalid color format for {color_name}: {color_value}. Must be #RRGGBB")

    # Validate font path exists
    font_path = config['display']['font']['path']
    if not os.path.exists(font_path):
        print(f"Warning: Font file not found: {font_path}", file=sys.stderr)
        print("  Will fall back to system font", file=sys.stderr)

    # Validate FPS
    fps = config['display']['fps']
    if not (10 <= fps <= 120):
        raise ValueError(f"Invalid FPS: {fps}. Must be 10-120")

    # Validate port
    port = config['communication']['yaagc']['port']
    if not (1024 <= port <= 65535):
        raise ValueError(f"Invalid port: {port}. Must be 1024-65535")

    # Validate window mode
    window_mode = config['display']['window_mode']
    if window_mode not in ['windowed', 'fullscreen']:
        raise ValueError(f"Invalid window_mode: {window_mode}. Must be 'windowed' or 'fullscreen'")


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color string to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


if __name__ == '__main__':
    # Test configuration loading
    try:
        config = load_config('config/dsky_config.yaml')
        print("Configuration loaded successfully!")
        print(f"Resolution: {config.display.resolution.width}x{config.display.resolution.height}")
        print(f"yaAGC host: {config.communication.yaagc.host}:{config.communication.yaagc.port}")
        print(f"Simulation mode: {config.display.simulation_mode}")
    except Exception as e:
        print(f"Error loading configuration: {e}", file=sys.stderr)
        sys.exit(1)
