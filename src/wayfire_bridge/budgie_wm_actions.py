"""
Budgie WM action keybindings handler
Handles hardcoded Budgie WM actions with their keybindings
"""

import gi

gi.require_version('Gio', '2.0')
from gi.repository import Gio

from .logging_config import get_logger

log = get_logger(__name__)


# Mapping of Budgie WM gsettings keys to hardcoded commands
# Format: gsetting_key: {command_name, command}
BUDGIE_WM_ACTION_MAPPINGS = {
    'clear-notifications': {
        'command_name': 'budgie_clear_notifications',
        'command': (
            'dbus-send --type=method_call '
            '--dest=org.budgie_desktop.Raven '
            '/org/budgie_desktop/Raven '
            'org.budgie_desktop.Raven.ClearNotifications'
        ),
    },
    'show-power-dialog': {
        'command_name': 'budgie_show_power_dialog',
        'command': (
            'dbus-send --type=method_call '
            '--dest=org.buddiesofbudgie.PowerDialog '
            '/org/buddiesofbudgie/PowerDialog '
            'org.buddiesofbudgie.PowerDialog.Toggle'
        ),
    },
    'take-full-screenshot': {
        'command_name': 'budgie_take_full_screenshot',
        'command': (
            'dbus-send --type=method_call '
            '--dest=org.buddiesofbudgie.BudgieScreenshotControl '
            '/org/buddiesofbudgie/ScreenshotControl '
            'org.buddiesofbudgie.BudgieScreenshotControl.StartFullScreenshot'
        ),
    },
    'take-region-screenshot': {
        'command_name': 'budgie_take_region_screenshot',
        'command': (
            'dbus-send --type=method_call '
            '--dest=org.buddiesofbudgie.BudgieScreenshotControl '
            '/org/buddiesofbudgie/ScreenshotControl '
            'org.buddiesofbudgie.BudgieScreenshotControl.StartAreaSelect'
        ),
    },
    'toggle-notifications': {
        'command_name': 'budgie_toggle_notifications',
        'command': (
            'dbus-send --type=method_call '
            '--dest=org.budgie_desktop.Raven '
            '/org/budgie_desktop/Raven '
            'org.budgie_desktop.Raven.ToggleNotificationsView'
        ),
    },
    'toggle-raven': {
        'command_name': 'budgie_toggle_raven',
        'command': (
            'dbus-send --type=method_call '
            '--dest=org.budgie_desktop.Raven '
            '/org/budgie_desktop/Raven '
            'org.budgie_desktop.Raven.ToggleAppletView'
        ),
    },
}


class BudgieWMActionsHandler:
    """Handles Budgie WM action keybindings"""

    def __init__(self, config_manager, transforms):
        self.config_manager = config_manager
        self.transforms = transforms
        self.schema = 'com.solus-project.budgie-wm'
        self.settings = None

    def setup(self):
        """Setup monitoring for Budgie WM action keys"""
        try:
            source = Gio.SettingsSchemaSource.get_default()
            if not source.lookup(self.schema, True):
                log.warning("Budgie WM schema %s not found", self.schema)
                return

            self.settings = Gio.Settings.new(self.schema)

            for key, mapping in BUDGIE_WM_ACTION_MAPPINGS.items():
                try:
                    self._apply_action_key(key, mapping)
                    self.settings.connect(
                        f'changed::{key}',
                        lambda s, k, m=mapping, gk=key: self._on_action_key_changed(gk, m),
                    )
                except Exception:
                    log.exception("Error setting up Budgie WM action %s", key)

            log.info(
                "Budgie WM actions monitoring enabled (%d actions)",
                len(BUDGIE_WM_ACTION_MAPPINGS),
            )

        except Exception:
            log.exception("Error setting up Budgie WM actions")

    def _apply_action_key(self, gsettings_key: str, mapping: dict):
        """Apply a Budgie WM action keybinding"""
        try:
            if not self.settings:
                return

            try:
                value = self.settings.get_value(gsettings_key).unpack()
            except Exception:
                log.debug("Could not read Budgie WM action %s", gsettings_key)
                return

            log.debug(
                "Budgie WM action %s: raw value = %r (%s)",
                gsettings_key, value, type(value).__name__,
            )

            # Normalise to a list of non-empty binding strings
            if isinstance(value, list):
                keybindings = [k for k in value if k and k not in ('', 'disabled')]
            elif isinstance(value, str) and value and value not in ('', 'disabled'):
                keybindings = [value]
            else:
                keybindings = []

            if not keybindings:
                log.debug("%s: no binding set", gsettings_key)
                self._remove_action_binding(mapping['command_name'])
                return

            # Convert each keybinding to Wayfire format
            wayfire_bindings = [
                wb for kb in keybindings
                if (wb := self.transforms.convert_keybinding(kb))
            ]

            if not wayfire_bindings:
                log.debug("%s: could not convert any keybindings to Wayfire format", gsettings_key)
                self._remove_action_binding(mapping['command_name'])
                return

            wayfire_binding = ' | '.join(wayfire_bindings)

            binding_option = f"binding_{mapping['command_name']}"
            command_option = f"command_{mapping['command_name']}"

            self.config_manager.set_value('command', binding_option, wayfire_binding)
            self.config_manager.set_value('command', command_option, mapping['command'])

            log.debug(
                "Applied Budgie WM action: %s = %s -> %s",
                gsettings_key, wayfire_binding, mapping['command'],
            )

        except Exception:
            log.exception("Error applying Budgie WM action %s", gsettings_key)

    def _remove_action_binding(self, command_name: str):
        """Remove a Budgie WM action binding from config"""
        self.config_manager.remove_option('command', f'binding_{command_name}')
        self.config_manager.remove_option('command', f'command_{command_name}')

    def _on_action_key_changed(self, key: str, mapping: dict):
        """Handle a Budgie WM action key change event"""
        log.debug("Budgie WM action changed: %s", key)
        self._apply_action_key(key, mapping)
        self.config_manager.save()
        self.config_manager.reload_wayfire()
