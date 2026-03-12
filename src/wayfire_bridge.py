#!/usr/bin/env python3
"""
Wayfire Bridge - Main entry point
Sync gsettings to Wayfire configuration
"""

import argparse
import os
import signal
import sys
from pathlib import Path

# Add the wayfire_bridge package to path
sys.path.insert(0, str(Path(__file__).parent))

from wayfire_bridge.logging_config import setup_logging, is_verbose

# ---------------------------------------------------------------------------
# Parse CLI arguments before importing anything else so that logging is
# configured before any module-level code runs.
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Wayfire Bridge – synchronise gsettings to wayfire.ini"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        default=is_verbose(),  # also honoured via WAYFIRE_BRIDGE_VERBOSE=1
        help=(
            "Enable verbose (DEBUG) logging.  "
            "Can also be set via the WAYFIRE_BRIDGE_VERBOSE=1 environment variable."
        ),
    )
    return parser.parse_args()


def main():
    """Main entry point"""
    args = _parse_args()

    # Configure logging first – all subsequent imports will inherit this setup
    log = setup_logging(verbose=args.verbose)

    try:
        # Deferred import so logging is already configured when the package loads
        from wayfire_bridge.bridge import WayfireBridge

        bridge = WayfireBridge()

        def signal_handler(sig, frame):
            log.info("Received signal %s – shutting down Wayfire Bridge", sig)
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        bridge.run()

    except Exception as e:
        log.critical("Fatal error: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
