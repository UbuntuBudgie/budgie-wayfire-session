"""
Budgie WM action keybindings handler
Handles hardcoded Budgie WM actions with their keybindings
"""

import sys
import gi

gi.require_version('Gio', '2.0')
from gi.repository import Gio


# Mapping of Budgie WM gsettings keys to hardcoded commands
# Format: gsetting_key: (command_name, wayfire_command)
BUDGIE_WM_ACTION_MAPPINGS = {
    'clear-notifications': {
        'command_name': 'budgie_clear_notifications',
        'command': 'dbus-send --type=method_call --dest=org.budgie_desktop.Raven /org/budgie_desktop/Raven org.budgie_desktop.Raven.ClearNotifications',
    },
    'show-power-dialog': {
        'command_name': 'budgie_show_power_dialog',
        'command': 'dbus-send --type=method_call --dest=org.buddiesofbudgie.PowerDialog /org/buddiesofbudgie/PowerDialog org.buddiesofbudgie.PowerDialog.Toggle',
    },
    'take-full-screenshot': {
        'command_name': 'budgie_take_full_screenshot',
        'command': 'dbus-send --type=method_call --dest=org.buddiesofbudgie.BudgieScreenshotControl /org/buddiesofbudgie/ScreenshotControl org.buddiesofbudgie.BudgieScreenshotControl.StartFullScreenshot',
    },
    'take-region-screenshot': {
        'command_name': 'budgie_take_region_screenshot',
        'command': 'dbus-send --type=method_call --dest=org.buddiesofbudgie.BudgieScreenshotControl /org/buddiesofbudgie/ScreenshotControl org.buddiesofbudgie.BudgieScreenshotControl.StartAreaSelect',
    },
    'toggle-notifications': {
        'command_name': 'budgie_toggle_notifications',
        'command': 'dbus-send --type=method_call --dest=org.budgie_desktop.Raven /org/budgie_desktop/Raven org.budgie_desktop.Raven.ToggleNotificationsView',
    },
    'toggle-raven': {
        'command_name': 'budgie_toggle_raven',
        'command': 'dbus-send --type=method_call --dest=org.budgie_desktop.Raven /org/budgie_desktop/Raven org.budgie_desktop.Raven.ToggleAppletView',
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
                print(f"Budgie WM schema not found", file=sys.stderr)
                return
            
            self.settings = Gio.Settings.new(self.schema)
            
            # Setup monitoring for each action
            for key, mapping in BUDGIE_WM_ACTION_MAPPINGS.items():
                try:
                    # Apply initial value
                    self._apply_action_key(key, mapping)
                    
                    # Monitor changes
                    self.settings.connect(
                        f'changed::{key}',
                        lambda s, k, m=mapping, gk=key: self._on_action_key_changed(gk, m)
                    )
                except Exception as e:
                    print(f"Error setting up Budgie WM action {key}: {e}", file=sys.stderr)
            
            print(f"Budgie WM actions monitoring enabled ({len(BUDGIE_WM_ACTION_MAPPINGS)} actions)")
            
        except Exception as e:
            print(f"Error setting up Budgie WM actions: {e}", file=sys.stderr)
    
    def _apply_action_key(self, gsettings_key: str, mapping: dict):
        """Apply a Budgie WM action keybinding"""
        try:
            if not self.settings:
                return
            
            # Get the keybinding (it's a string, not an array like media keys)
            try:
                keybinding = self.settings.get_string(gsettings_key)
            except Exception as e:
                print(f"Could not read Budgie WM action {gsettings_key}: {e}", file=sys.stderr)
                return
            
            print(f"Budgie WM action {gsettings_key}: raw value = '{keybinding}' (type: str)")
            
            # Check if empty or disabled
            if not keybinding or keybinding == '' or keybinding == 'disabled':
                print(f"  → {gsettings_key}: disabled or empty")
                self._remove_action_binding(mapping['command_name'])
                return
            
            print(f"  → {gsettings_key}: keybinding = '{keybinding}'")
            
            # Convert to Wayfire format
            wayfire_binding = self.transforms.convert_keybinding(keybinding)
            print(f"  → {gsettings_key}: wayfire format = '{wayfire_binding}'")
            
            if wayfire_binding:
                # Set binding and command
                binding_option = f"binding_{mapping['command_name']}"
                command_option = f"command_{mapping['command_name']}"
                
                self.config_manager.set_value('command', binding_option, wayfire_binding)
                self.config_manager.set_value('command', command_option, mapping['command'])
                
                # Verify it was set
                check_binding = self.config_manager.get_value('command', binding_option)
                check_command = self.config_manager.get_value('command', command_option)
                print(f"  → Set in config: {binding_option} = {check_binding}")
                print(f"  → Set in config: {command_option} = {check_command}")
                
                print(f"✓ Applied Budgie WM action: {gsettings_key} = {wayfire_binding} -> {mapping['command']}")
            else:
                print(f"  → {gsettings_key}: could not convert keybinding '{keybinding}'")
                self._remove_action_binding(mapping['command_name'])
        
        except Exception as e:
            print(f"Error applying Budgie WM action {gsettings_key}: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
    
    def _remove_action_binding(self, command_name: str):
        """Remove a Budgie WM action binding"""
        binding_option = f"binding_{command_name}"
        command_option = f"command_{command_name}"
        
        self.config_manager.remove_option('command', binding_option)
        self.config_manager.remove_option('command', command_option)
    
    def _on_action_key_changed(self, key: str, mapping: dict):
        """Handle Budgie WM action key change"""
        print(f"Budgie WM action changed: {key}")
        self._apply_action_key(key, mapping)
        self.config_manager.save()
        self.config_manager.reload_wayfire()
