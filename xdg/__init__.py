import os
from pathlib import Path
from typing import List, Optional

from xdg import BaseDirectory

__all__ = [
    "BaseDirectory",
    "DesktopEntry",
    "Menu",
    "Exceptions",
    "IniFile",
    "IconTheme",
    "Locale",
    "Config",
    "Mime",
    "RecentFiles",
    "MenuEditor",
]

__version__ = "0.28"


def xdg_cache_home() -> Path:
    """Return a Path corresponding to XDG_CACHE_HOME."""
    return Path(BaseDirectory.xdg_cache_home)


def xdg_config_dirs() -> List[Path]:
    """Return a list of Paths corresponding to XDG_CONFIG_DIRS."""
    try:
        return [Path(path) for path in os.environ["XDG_CONFIG_DIRS"].split(":")]
    except KeyError:
        return [Path("/etc/xdg")]


def xdg_config_home() -> Path:
    """Return a Path corresponding to XDG_CONFIG_HOME."""
    return Path(BaseDirectory.xdg_config_home)


def xdg_data_dirs() -> List[Path]:
    """Return a list of Paths corresponding to XDG_DATA_DIRS."""
    try:
        return [Path(path) for path in os.environ["XDG_DATA_DIRS"].split(":")]
    except KeyError:
        return [Path("/usr/local/share"), Path("/usr/share")]


def xdg_data_home() -> Path:
    """Return a Path corresponding to XDG_DATA_HOME."""
    return Path(BaseDirectory.xdg_data_home)


def xdg_runtime_dir() -> Optional[Path]:
    """Return a Path corresponding to XDG_RUNTIME_DIR.

    If the XDG_RUNTIME_DIR environment variable is not set, None will be
    returned as per the specification.
    """
    try:
        return Path(BaseDirectory.get_runtime_dir())
    except KeyError:
        return None


def xdg_state_home() -> Path:
    """Return a Path corresponding to XDG_STATE_HOME."""
    return Path(BaseDirectory.xdg_state_home)
