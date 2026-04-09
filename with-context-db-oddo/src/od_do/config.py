"""
Configuration management for OD-DO.
"""

import platform
from pathlib import Path


def get_platform_defaults():
    system = platform.system()

    if system == "Darwin":
        return {
            "svg_viewer": ["open", "-a", "Google Chrome"],
            "png_viewer": ["open", "-a", "Preview"],
            "drawio_viewer": ["open"],
        }
    elif system == "Linux":
        return {
            "svg_viewer": "xdg-open",
            "png_viewer": "xdg-open",
            "drawio_viewer": "xdg-open",
        }
    elif system == "Windows":
        return {
            "svg_viewer": "start",
            "png_viewer": "start",
            "drawio_viewer": "start",
        }
    else:
        return {
            "svg_viewer": "xdg-open",
            "png_viewer": "xdg-open",
            "drawio_viewer": "xdg-open",
        }


def load_config():
    config_path = Path.home() / ".od-do-config"

    defaults = {
        "default_backend": "svg",
        "default_width": 800,
        "default_height": 600,
        **get_platform_defaults(),
    }

    if not config_path.exists():
        return defaults

    try:
        import sys

        if sys.version_info >= (3, 11):
            import tomllib

            with open(config_path, "rb") as f:
                user_config = tomllib.load(f)
        else:
            import toml

            user_config = toml.load(config_path)

        defaults.update(user_config)
    except Exception:
        pass

    return defaults


_config = None


def get_config():
    global _config
    if _config is None:
        _config = load_config()
    return _config
