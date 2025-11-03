"""Version extraction for PolyTracker.

This module extracts the version information from the C header file.
"""

import os
import re
import sys
from pathlib import Path
from typing import Optional, Tuple


def get_polytracker_header() -> Path:
    """Get the path to the polytracker.h header file."""
    package_dir = Path(__file__).parent
    header_path = package_dir / "include" / "polytracker" / "polytracker.h"

    if not header_path.exists():
        sys.stderr.write(
            f"Error loading polytracker.h!\nIt was expected to be here:\n{header_path}\n\n"
        )
        sys.exit(1)

    return header_path


def extract_version() -> Tuple[int, int, int, Optional[str]]:
    """Extract version components from the C header file.

    Returns:
        A tuple of (major, minor, revision, suffix) where suffix may be None
    """
    header_path = get_polytracker_header()
    version_parts = {}

    with open(header_path, "r") as f:
        for i, line in enumerate(f):
            m = re.match(
                r"\s*#define\s+POLYTRACKER_VERSION_([A-Za-z_0-9]+)\s+([^\s]+)\s*$", line
            )
            if m:
                if m[1] not in ("MAJOR", "MINOR", "REVISION", "SUFFIX"):
                    sys.stderr.write(
                        f'Warning: Ignoring unexpected #define for "POLYTRACKER_VERSION_{m[1]}" on line '
                        f"{i + 1} of {header_path}\n"
                    )
                else:
                    version_parts[m[1]] = m[2]

    # Validate required parts
    for required_part in ("MAJOR", "MINOR", "REVISION"):
        if required_part not in version_parts:
            sys.stderr.write(
                f"Error: #define POLYTRACKER_VERSION_{required_part} not found in {header_path}\n\n"
            )
            sys.exit(1)
        try:
            version_parts[required_part] = int(version_parts[required_part])
        except ValueError:
            sys.stderr.write(
                f"Error: POLYTRACKER_VERSION_{required_part} in {header_path} is not an integer!\n\n"
            )
            sys.exit(1)

    # Handle suffix
    suffix = version_parts.get("SUFFIX", None)
    if suffix is not None:
        suffix = suffix.strip()
        if suffix.startswith('"') and suffix.endswith('"'):
            suffix = suffix[1:-1]
        if suffix == "":
            suffix = None

    return (
        version_parts["MAJOR"],
        version_parts["MINOR"],
        version_parts["REVISION"],
        suffix,
    )


def get_version_string() -> str:
    """Get the version as a string.

    Returns:
        Version string in format "major.minor.revision" or "major.minor.revisionsuffix"
    """
    *primary, suffix = extract_version()
    primary_str = ".".join(map(str, primary))

    if suffix is None:
        return primary_str
    else:
        return f"{primary_str}{suffix}"


__version__ = get_version_string()
