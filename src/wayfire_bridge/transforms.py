"""
Transform functions for converting gsettings values to Wayfire format
"""

from typing import Any


class TransformFunctions:
    """Collection of transform functions for gsettings to Wayfire conversion"""

    @staticmethod
    def str(value: Any) -> str:
        """Pass through as string"""
        return str(value)

    @staticmethod
    def int(value: Any) -> int:
        """Convert to integer"""
        return int(value)

    @staticmethod
    def float(value: Any) -> float:
        """Convert to float"""
        return float(value)

    @staticmethod
    def bool(value: bool) -> str:
        """Transform boolean to wayfire format (true/false)"""
        return 'true' if value else 'false'

    @staticmethod
    def button_layout(value: str) -> str:
        """Transform GNOME button layout to Wayfire format"""
        return value.replace(':', '').strip()

    @staticmethod
    def focus_mode(value: str) -> str:
        """Transform focus mode"""
        mode_map = {
            'click': 'click',
            'sloppy': 'sloppy',
            'mouse': 'mouse'
        }
        return mode_map.get(value, 'click')

    @staticmethod
    def scroll_method(value: bool) -> str:
        """Transform two-finger scrolling to scroll method"""
        return 'two-finger' if value else 'edge'

    @staticmethod
    def num_workspaces(value: int) -> str:
        """Transform number of workspaces to viewport grid"""
        # Wayfire uses a 2D grid, assume horizontal layout
        return f"{value} 1"

    @staticmethod
    def keybinding(value: Any) -> str:
        """Transform GNOME keybinding format to Wayfire format"""
        if isinstance(value, list) and len(value) > 0:
            # GNOME can have multiple keybindings in array
            # Convert each and join with pipe separator
            converted = []
            for binding in value:
                wayfire_binding = TransformFunctions.convert_keybinding(binding)
                if wayfire_binding:
                    converted.append(wayfire_binding)
            return ' | '.join(converted) if converted else ''
        return ''

    @staticmethod
    def convert_keybinding(gnome_binding: str) -> str:
        """Convert GNOME keybinding to Wayfire format

        Wayfire format: <modifier1> <modifier2> KEY_X
        - Modifiers FIRST, lowercase, in angle brackets
        - Key LAST, uppercase with KEY_ prefix
        - Example: <ctrl> <alt> KEY_T (NOT KEY_T CTRL ALT!)
        """
        if not gnome_binding or gnome_binding == 'disabled':
            return ''

        modifiers = []
        key = gnome_binding

        # Extract modifiers in order - will be lowercase in angle brackets
        if '<Super>' in key or '<Mod4>' in key:
            modifiers.append('<super>')
        if '<Primary>' in key or '<Control>' in key or '<Ctrl>' in key:
            modifiers.append('<ctrl>')
        if '<Alt>' in key:
            modifiers.append('<alt>')
        if '<Shift>' in key:
            modifiers.append('<shift>')

        # Remove modifiers to get key
        for mod in ['<Super>', '<Mod4>', '<Primary>', '<Control>', '<Ctrl>', '<Alt>', '<Shift>']:
            key = key.replace(mod, '')
        key = key.strip('<>')

        if key:
            # Handle special key names
            key_map = {
                'Return': 'ENTER',
                'BackSpace': 'BACKSPACE',
                'Escape': 'ESC',
                'space': 'SPACE',
                'Space': 'SPACE',
                'Tab': 'TAB',
                'Page_Up': 'PAGEUP',
                'Page_Down': 'PAGEDOWN',
                'Prior': 'PAGEUP',
                'Next': 'PAGEDOWN',
            }
            key = key_map.get(key, key)

            # Check if it's a hardware key (XF86*)
            # These don't get KEY_ prefix
            if key.startswith('XF86'):
                key_part = key  # Use as-is: XF86AudioLowerVolume
            else:
                key_part = f"KEY_{key.upper()}"

            if modifiers:
                # Join modifiers with space, then add key at the end
                return ' '.join(modifiers) + ' ' + key_part
            else:
                return key_part
        return ''

    @staticmethod
    def sanitize_name(name: str) -> str:
        """Sanitize custom keybinding name for use in config"""
        import re
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        sanitized = sanitized.lower().strip('_')
        return sanitized or 'custom'

    @staticmethod
    def kb_repeat_rate(value: int) -> int:
        """Transform keyboard repeat interval (ms) to repeat rate (chars/sec)"""
        # GNOME uses repeat-interval in milliseconds between repeats
        # Wayfire uses kb_repeat_rate as characters per second
        # Rate = 1000 / interval
        if value > 0:
            return max(1, int(1000 / value))
        return 30  # Default fallback

    @staticmethod
    def xkb_layout(value: Any) -> str:
        """Transform GNOME input sources to XKB layout"""
        # GNOME format: [('xkb', 'gb'), ('xkb', 'us')]
        # Wayfire format: gb,us
        try:
            if not value:
                return 'us'  # Default fallback

            layouts = []
            variants = []

            for source in value:
                if len(source) >= 2 and source[0] == 'xkb':
                    layout_str = source[1]
                    # Check if variant is specified (e.g., 'us+dvorak')
                    if '+' in layout_str:
                        layout, variant = layout_str.split('+', 1)
                        layouts.append(layout)
                        variants.append(variant)
                    else:
                        layouts.append(layout_str)

            if layouts:
                return ','.join(layouts)
            return 'us'
        except Exception as e:
            print(f"Error parsing xkb layout: {e}")
            return 'us'

    @staticmethod
    def xkb_options(value: Any) -> str:
        """Transform XKB options array to string"""
        # GNOME format: ['ctrl:nocaps', 'compose:ralt']
        # Wayfire format: ctrl:nocaps,compose:ralt
        try:
            if isinstance(value, list) and value:
                return ','.join(value)
            return ''
        except Exception:
            return ''