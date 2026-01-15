#!/usr/bin/env python3
"""
Wayfire Bridge - Main entry point
Sync gsettings to Wayfire configuration
"""

import sys
import signal
from pathlib import Path

# Add the wayfire_bridge package to path
sys.path.insert(0, str(Path(__file__).parent))

from wayfire_bridge.bridge import WayfireBridge


def main():
    """Main entry point"""
    try:
        bridge = WayfireBridge()
        
        # Setup signal handlers for clean shutdown
        def signal_handler(sig, frame):
            print("\nShutting down Wayfire Bridge...")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Run the bridge
        bridge.run()
        
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()