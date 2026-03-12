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
        """Transform focus mode

        Wayfire modes: click, sloppy, mouse
        - click: focus only on click
        - sloppy: focus follows mouse without raising
        - mouse: focus follows mouse and raises window
        """
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
    def touchpad_left_handed(value: str) -> str:
        """Transform touchpad left-handed mode

        GNOME uses: 'left', 'right', 'mouse' (follow mouse setting)
        Wayfire uses: true/false

        Note: When value is 'mouse', caller must check mouse left-handed setting
        """
        if value == 'left':
            return 'true'
        elif value == 'right':
            return 'false'
        # 'mouse' - caller needs to handle this specially
        return 'mouse'

    @staticmethod
    def send_events(value: str) -> str:
        """Transform touchpad send-events mode

        GNOME: enabled, disabled, disabled-on-external-mouse
        Wayfire: N/A (we handle via environment or input config if supported)
        """
        # Wayfire doesn't have direct equivalent, but we can map for future use
        return value

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
            # Handle special key names and XF86 hardware keys
            key_map = {
                # Standard keys
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

                # XF86 Hardware keys -> KEY_ equivalents
                'XF86AudioLowerVolume': 'VOLUMEDOWN',
                'XF86AudioRaiseVolume': 'VOLUMEUP',
                'XF86AudioMute': 'MUTE',
                'XF86AudioPlay': 'PLAY',
                'XF86AudioPause': 'PAUSE',
                'XF86AudioStop': 'STOP',
                'XF86AudioNext': 'NEXTSONG',
                'XF86AudioPrev': 'PREVIOUSSONG',
                'XF86AudioRewind': 'REWIND',
                'XF86AudioForward': 'FORWARD',
                'XF86AudioMedia': 'MEDIA',
                'XF86AudioRecord': 'RECORD',
                'XF86MonBrightnessUp': 'BRIGHTNESSUP',
                'XF86MonBrightnessDown': 'BRIGHTNESSDOWN',
                'XF86KbdBrightnessUp': 'BRIGHTNESSUP',
                'XF86KbdBrightnessDown': 'BRIGHTNESSDOWN',
                'XF86Display': 'DISPLAYTOGGLE',
                'XF86WLAN': 'WLAN',
                'XF86Tools': 'TOOLS',
                'XF86Search': 'SEARCH',
                'XF86LaunchA': 'LAUNCH0',
                'XF86LaunchB': 'LAUNCH1',
                'XF86Explorer': 'EXPLORER',
                'XF86Calculator': 'CALC',
                'XF86Mail': 'MAIL',
                'XF86WWW': 'WWW',
                'XF86HomePage': 'HOMEPAGE',
                'XF86Favorites': 'FAVORITES',
                'XF86Back': 'BACK',
                'XF86Forward': 'FORWARD',
                'XF86Eject': 'EJECT',
                'XF86Sleep': 'SLEEP',
                'XF86PowerOff': 'POWER',
                'XF86Battery': 'BATTERY',
                'XF86Bluetooth': 'BLUETOOTH',
            }
            key = key_map.get(key, key)

            # Build the keybinding: <modifier1> <modifier2> KEY_X
            key_part = f"KEY_{key.upper()}"

            # Modifiers FIRST (lowercase in angle brackets), key LAST
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
        """Transform GNOME input sources to XKB layout

        Note: This is only called for GSettings sources.
        If sources is empty, return empty string so bridge can use
        the priority system (locale1 or /etc/default/keyboard).
        """
        try:
            if not value:
                # Empty sources - return empty so bridge uses fallback
                return ''

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

            # No xkb sources found - return empty for fallback
            return ''

        except Exception as e:
            print(f"Error parsing xkb layout: {e}")
            return ''

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


def parse_options_string(options_string):
    """Parse comma-separated options into a set."""
    if not options_string:
        return set()
    return {opt.strip() for opt in options_string.split(',') if opt.strip()}


def normalize_xkb_options(options_set):
    """
    Normalize XKB options to avoid conflicts.
    Only certain option families are mutually exclusive.
    Other families like lv3:, compose: can have multiple options.

    Known mutually-exclusive families: grp, caps, ctrl, altwin

    Args:
        options_set: Set of XKB option strings

    Returns:
        Set of normalized options
    """
    if not options_set:
        return set()

    # Families where only one option should be kept
    exclusive_families = {'grp', 'caps', 'ctrl', 'altwin'}

    seen_exclusive = {}
    normalized = set()

    for option in sorted(options_set):  # Sort for consistent behavior
        if ':' in option:
            family = option.split(':', 1)[0]

            if family in exclusive_families:
                # Keep only first of exclusive families
                if family not in seen_exclusive:
                    seen_exclusive[family] = option
                    normalized.add(option)
                # else: skip duplicate exclusive family
            else:
                # Non-exclusive family - keep all
                normalized.add(option)
        else:
            # Options without family (rare) - keep all
            normalized.add(option)

    return normalized


def format_keyboard_layout(layout, variant=''):
    """
    Convert layout and variant strings to labwc/wayfire format.

    Args:
        layout: Comma-separated layout string
        variant: Comma-separated variant string

    Returns:
        Formatted layout string or None if no layout
    """
    if not layout:
        return None

    if not variant:
        return layout

    variants = variant.split(',')
    layouts = layout.split(',')

    combined = []
    for i, l in enumerate(layouts):
        if i < len(variants) and variants[i]:
            combined.append(f"{l}({variants[i]})")
        else:
            combined.append(l)

    return ','.join(combined)
