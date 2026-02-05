"""
Media keys handler for Wayfire Bridge
Handles static media key bindings from gsettings
"""

import sys
import gi

gi.require_version('Gio', '2.0')
from gi.repository import Gio


# Mapping of media key gsettings to Wayfire commands
# Format: gsetting_key: (command_name, wayfire_command, plugin_requirement)
MEDIA_KEY_MAPPINGS = {
    'terminal': {
        'command_name': 'launch_terminal',
        'command': 'x-terminal-emulator',
        'fallback_command': 'xfce4-terminal',
        'plugin': None
    },
    'www': {
        'command_name': 'launch_browser',
        'command': 'x-www-browser',
        'fallback_command': 'firefox',
        'plugin': None
    },
    'email': {
        'command_name': 'launch_email',
        'command': 'xdg-email',
        'fallback_command': 'thunderbird',
        'plugin': None
    },
    'home': {
        'command_name': 'launch_file_manager',
        'command': 'xdg-open ~',
        'fallback_command': 'nemo',
        'plugin': None
    },
    'calculator': {
        'command_name': 'launch_calculator',
        'command': 'mate-calc',
        'fallback_command': 'gnome-calculator',
        'plugin': None
    },
    'help': {
        'command_name': 'launch_help',
        'command': '',
        'fallback_command': '',
        'plugin': None
    },
    'search': {
        'command_name': 'launch_search',
        'command': '',
        'fallback_command': '',
        'plugin': None
    },
    'magnifier': {
        'command_name': 'toggle_magnifier',
        'command': 'wf-mag',  # Wayfire magnifier toggle script
        'fallback_command': '',
        'plugin': 'mag'  # Requires mag plugin
    },
    'magnifier-zoom-in': {
        'command_name': 'magnifier_zoom_in',
        'command': 'wf-mag zoom-in',
        'fallback_command': '',
        'plugin': 'mag'
    },
    'magnifier-zoom-out': {
        'command_name': 'magnifier_zoom_out',
        'command': 'wf-mag zoom-out',
        'fallback_command': '',
        'plugin': 'mag'
    },
    'screenreader': {
        'command_name': 'toggle_screenreader',
        'command': '',
        'fallback_command': '',
        'plugin': None
    },
    'screensaver': {
        'command_name': 'lock_screen',
        'command': 'dbus-send --type=method_call --dest=org.buddiesofbudgie.BudgieScreenlock /org/buddiesofbudgie/Screenlock org.buddiesofbudgie.BudgieScreenlock.Lock',
        'fallback_command': '',
        'plugin': None
    },
    'decrease-text-size': {
        'command_name': 'decrease_text_size',
        'command': '',
        'fallback_command': '',
        'plugin': None
    },
    'toggle-contrast': {
        'command_name': 'toggle_contrast',
        'command': '',
        'fallback_command': '',
        'plugin': None
    },
    'increase-text-size': {
        'command_name': 'increase_text_size',
        'command': '',
        'fallback_command': '',
        'plugin': None
    },
    'on-screen-keyboard': {
        'command_name': 'on_screen_keyboard',
        'command': '',
        'fallback_command': '',
        'plugin': None
    },
    'email': {
        'command_name': 'on_email',
        'command': 'xdg-email',
        'fallback_command': '',
        'plugin': None
    },
    'control-center': {
        'command_name': 'on_control_center',
        'command': 'budgie-desktop-settings',
        'fallback_command': '',
        'plugin': None
    },
    'eject': {
        'command_name': 'on_eject',
        'command': '',
        'fallback_command': '',
        'plugin': None
    },
    'media': {
        'command_name': 'on_media',
        'command': '',
        'fallback_command': '',
        'plugin': None
    },
    'mic-mute': {
        'command_name': 'on_mic_mute',
        'command': '',
        'fallback_command': '',
        'plugin': None
    },
    'next': {
        'command_name': 'on_next',
        'command': '',
        'fallback_command': '',
        'plugin': None
    },
    'pause': {
        'command_name': 'on_pause',
        'command': '',
        'fallback_command': '',
        'plugin': None
    },
    'play': {
        'command_name': 'on_play',
        'command': '',
        'fallback_command': '',
        'plugin': None
    },
    'previous': {
        'command_name': 'on_previous',
        'command': '',
        'fallback_command': '',
        'plugin': None
    },
    'stop': {
        'command_name': 'on_stop',
        'command': '',
        'fallback_command': '',
        'plugin': None
    },
    'volume-down': {
        'command_name': 'on_volume_down',
        'command': "wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-",
        'fallback_command': '',
        'plugin': None
    },
    'volume-mute': {
        'command_name': 'on_volume_mute',
        'command': "wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle",
        'fallback_command': '',
        'plugin': None
    },
    'volume-up': {
        'command_name': 'on_volume_up',
        'command': "wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%+",
        'fallback_command': '',
        'plugin': None
    },
    'logout': {
        'command_name': 'on_logout',
        'command': "budgie-session-quit",
        'fallback_command': '',
        'plugin': None
    },
    'keyboard-brightness-down': {
        'command_name': 'on_keyboard_brightness_down',
        'command': "budgie-brightness-helper --down",
        'fallback_command': '',
        'plugin': None
    },
    'keyboard-brightness-up': {
        'command_name': 'on_keyboard_brightness_up',
        'command': "budgie-brightness-helper --up",
        'fallback_command': '',
        'plugin': None
    },
}


class MediaKeysHandler:
    """Handles static media key bindings"""

    def __init__(self, config_manager, transforms):
        self.config_manager = config_manager
        self.transforms = transforms
        self.schema = 'org.buddiesofbudgie.settings-daemon.plugins.media-keys'
        self.settings = None

    def setup(self):
        """Setup monitoring for media keys"""
        try:
            source = Gio.SettingsSchemaSource.get_default()
            if not source.lookup(self.schema, True):
                print(f"Media keys schema not found", file=sys.stderr)
                return

            self.settings = Gio.Settings.new(self.schema)

            # Setup monitoring for each media key
            for key, mapping in MEDIA_KEY_MAPPINGS.items():
                try:
                    # Apply initial value
                    self._apply_media_key(key, mapping)

                    # Monitor changes
                    self.settings.connect(
                        f'changed::{key}',
                        lambda s, k, m=mapping, gk=key: self._on_media_key_changed(gk, m)
                    )
                except Exception as e:
                    print(f"Error setting up media key {key}: {e}", file=sys.stderr)

            print(f"Media keys monitoring enabled ({len(MEDIA_KEY_MAPPINGS)} keys)")

        except Exception as e:
            print(f"Error setting up media keys: {e}", file=sys.stderr)

    def _apply_media_key(self, gsettings_key: str, mapping: dict):
        """Apply a media key binding"""
        try:
            if not self.settings:
                return

            # Get the keybinding from gsettings
            try:
                value = self.settings.get_value(gsettings_key).unpack()
            except Exception as e:
                print(f"Could not read media key {gsettings_key}: {e}", file=sys.stderr)
                return

            print(f"Media key {gsettings_key}: raw value = {value} (type: {type(value).__name__})")

            # Handle string arrays
            keybindings = []
            if isinstance(value, list):
                # Filter out empty strings
                keybindings = [k for k in value if k and k != '' and k != 'disabled']

                # If empty, try -static variant (if it exists)
                if not keybindings:
                    static_key = f"{gsettings_key}-static"

                    # Check if -static key exists in schema
                    schema_obj = self.settings.get_property('settings-schema')
                    if schema_obj and schema_obj.has_key(static_key):
                        try:
                            static_value = self.settings.get_value(static_key).unpack()
                            if isinstance(static_value, list):
                                keybindings = [k for k in static_value if k and k != '' and k != 'disabled']
                                if keybindings:
                                    print(f"  → Using {static_key} (static fallback): {keybindings}")
                        except Exception as e:
                            print(f"  → Could not read {static_key}: {e}", file=sys.stderr)
                    else:
                        print(f"  → No {static_key} key available")
            elif isinstance(value, str):
                if value and value != '' and value != 'disabled':
                    keybindings = [value]

            if not keybindings:
                print(f"  → {gsettings_key}: no binding set (empty)")
                self._remove_media_key_binding(mapping['command_name'])
                return

            print(f"  → {gsettings_key}: keybindings = {keybindings}")

            # Convert each keybinding to Wayfire format
            wayfire_bindings = []
            for kb in keybindings:
                wayfire_kb = self.transforms.convert_keybinding(kb)
                if wayfire_kb:
                    wayfire_bindings.append(wayfire_kb)

            if not wayfire_bindings:
                print(f"  → {gsettings_key}: could not convert any keybindings")
                self._remove_media_key_binding(mapping['command_name'])
                return

            # Join multiple keybindings with pipe separator
            wayfire_binding = ' | '.join(wayfire_bindings)
            print(f"  → {gsettings_key}: wayfire format = '{wayfire_binding}'")

            # Check if command is empty - if so, don't write the binding
            command = mapping['command']
            if not command or command.strip() == '':
                # Try fallback command
                command = mapping.get('fallback_command', '')
                if not command or command.strip() == '':
                    print(f"  → {gsettings_key}: no command defined, skipping")
                    self._remove_media_key_binding(mapping['command_name'])
                    return
                print(f"  → Using fallback command: {command}")

            # Set binding and command
            binding_option = f"binding_{mapping['command_name']}"
            command_option = f"command_{mapping['command_name']}"

            self.config_manager.set_value('command', binding_option, wayfire_binding)
            self.config_manager.set_value('command', command_option, command)

            # Verify it was set
            check_binding = self.config_manager.get_value('command', binding_option)
            check_command = self.config_manager.get_value('command', command_option)
            print(f"  → Set in config: {binding_option} = {check_binding}")
            print(f"  → Set in config: {command_option} = {check_command}")

            # If plugin required, add note
            if mapping.get('plugin'):
                print(f"✓ Applied media key: {gsettings_key} -> {mapping['command_name']} "
                    f"(requires {mapping['plugin']} plugin)")
            else:
                print(f"✓ Applied media key: {gsettings_key} = {wayfire_binding} -> {command}")

        except Exception as e:
            print(f"Error applying media key {gsettings_key}: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()

    def _remove_media_key_binding(self, command_name: str):
        """Remove a media key binding"""
        binding_option = f"binding_{command_name}"
        command_option = f"command_{command_name}"

        self.config_manager.remove_option('command', binding_option)
        self.config_manager.remove_option('command', command_option)

    def _on_media_key_changed(self, key: str, mapping: dict):
        """Handle media key change"""
        print(f"Media key changed: {key}")
        self._apply_media_key(key, mapping)
        self.config_manager.save()
        self.config_manager.reload_wayfire()
