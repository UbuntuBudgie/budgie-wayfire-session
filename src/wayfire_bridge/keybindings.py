"""
Custom keybindings handler for Wayfire Bridge
Manages dynamic custom keybindings from budgie-control-center
"""

from typing import Dict
import gi

gi.require_version('Gio', '2.0')
from gi.repository import Gio

from .logging_config import get_logger

log = get_logger(__name__)


class CustomKeybindingsHandler:
    """Handles custom keybindings from gsettings"""

    def __init__(self, config_manager, transforms):
        self.config_manager = config_manager
        self.transforms = transforms
        self.schema = 'org.buddiesofbudgie.settings-daemon.plugins.media-keys'
        self.custom_schema = (
            'org.buddiesofbudgie.settings-daemon.plugins.media-keys.custom-keybinding'
        )
        self.settings = None

        # path -> {name, sanitized_name, command, binding}
        self.custom_keybindings: Dict[str, Dict] = {}
        # path -> Gio.Settings
        self.custom_keybinding_settings: Dict[str, Gio.Settings] = {}

    def setup(self):
        """Setup monitoring for custom keybindings"""
        try:
            source = Gio.SettingsSchemaSource.get_default()

            if not source.lookup(self.schema, True):
                log.warning("Custom keybindings schema %s not found", self.schema)
                return

            self.settings = Gio.Settings.new(self.schema)

            # Apply initial custom keybindings
            self._sync_custom_keybindings(self.settings)

            # Monitor changes to the custom-keybindings list
            self.settings.connect(
                'changed::custom-keybindings',
                lambda s, k: self._sync_custom_keybindings(s),
            )

            log.info("Custom keybindings monitoring enabled")

        except Exception:
            log.exception("Error setting up custom keybindings")

    def _sync_custom_keybindings(self, settings: Gio.Settings):
        """Sync all custom keybindings from gsettings"""
        try:
            paths = settings.get_value('custom-keybindings').unpack()
            current_paths = set(paths)
            previous_paths = set(self.custom_keybindings.keys())

            # Remove deleted keybindings
            for path in previous_paths - current_paths:
                self._remove_custom_keybinding(path)

            # Add or update keybindings
            for path in current_paths:
                if path in previous_paths:
                    self._update_custom_keybinding(path)
                else:
                    self._add_custom_keybinding(path)

            if previous_paths or current_paths:
                self.config_manager.save()
                self.config_manager.reload_wayfire()

        except Exception:
            log.exception("Error syncing custom keybindings")

    def _add_custom_keybinding(self, path: str):
        """Add a new custom keybinding"""
        try:
            settings = Gio.Settings.new_with_path(self.custom_schema, path)

            name = settings.get_string('name')
            command = settings.get_string('command')
            binding = settings.get_string('binding')

            if not name or not command:
                log.debug("Incomplete custom keybinding at %s (no name/command), skipping", path)
                return

            sanitized_name = self.transforms.sanitize_name(name)
            self.custom_keybindings[path] = {
                'name': name,
                'sanitized_name': sanitized_name,
                'command': command,
                'binding': binding,
            }
            self.custom_keybinding_settings[path] = settings

            self._apply_custom_keybinding(path)

            settings.connect('changed::name',    lambda s, k, p=path: self._update_custom_keybinding(p))
            settings.connect('changed::command', lambda s, k, p=path: self._update_custom_keybinding(p))
            settings.connect('changed::binding', lambda s, k, p=path: self._update_custom_keybinding(p))

            log.info("Added custom keybinding: %r -> %s", name, command)

        except Exception:
            log.exception("Error adding custom keybinding %s", path)

    def _update_custom_keybinding(self, path: str):
        """Update an existing custom keybinding"""
        try:
            if path not in self.custom_keybinding_settings:
                return

            settings = self.custom_keybinding_settings[path]

            name = settings.get_string('name')
            command = settings.get_string('command')
            binding = settings.get_string('binding')

            old_sanitized = self.custom_keybindings[path]['sanitized_name']
            new_sanitized = self.transforms.sanitize_name(name)

            self.custom_keybindings[path] = {
                'name': name,
                'sanitized_name': new_sanitized,
                'command': command,
                'binding': binding,
            }

            # If name changed, remove the old config entries
            if old_sanitized != new_sanitized:
                self._remove_custom_keybinding_entries(old_sanitized)

            self._apply_custom_keybinding(path)

            self.config_manager.save()
            self.config_manager.reload_wayfire()

            log.info("Updated custom keybinding: %r -> %s", name, command)

        except Exception:
            log.exception("Error updating custom keybinding %s", path)

    def _remove_custom_keybinding(self, path: str):
        """Remove a custom keybinding"""
        try:
            if path in self.custom_keybindings:
                sanitized_name = self.custom_keybindings[path]['sanitized_name']
                self._remove_custom_keybinding_entries(sanitized_name)

                del self.custom_keybindings[path]
                self.custom_keybinding_settings.pop(path, None)

                log.info("Removed custom keybinding: %s", sanitized_name)

        except Exception:
            log.exception("Error removing custom keybinding %s", path)

    def _remove_custom_keybinding_entries(self, sanitized_name: str):
        """Remove config entries for a custom keybinding"""
        self.config_manager.remove_option('command', f'binding_{sanitized_name}')
        self.config_manager.remove_option('command', f'command_{sanitized_name}')

    def _apply_custom_keybinding(self, path: str):
        """Apply a custom keybinding to the config"""
        try:
            kb = self.custom_keybindings[path]
            sanitized_name = kb['sanitized_name']
            command = kb['command']
            binding = kb['binding']

            wayfire_binding = (
                self.transforms.convert_keybinding(binding) if binding else ''
            )

            if wayfire_binding:
                self.config_manager.set_value('command', f'binding_{sanitized_name}', wayfire_binding)
                self.config_manager.set_value('command', f'command_{sanitized_name}', command)
                log.debug(
                    "Applied custom keybinding: %s = %s -> %s",
                    sanitized_name, wayfire_binding, command,
                )
            else:
                # No valid binding – remove entries
                self._remove_custom_keybinding_entries(sanitized_name)
                log.debug("Removed binding for %s (no keybinding set)", sanitized_name)

        except Exception:
            log.exception("Error applying custom keybinding %s", path)
