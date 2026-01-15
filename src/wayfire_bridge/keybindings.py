"""
Custom keybindings handler for Wayfire Bridge
Manages dynamic custom keybindings from budgie-control-center
"""

import sys
from typing import Dict
import gi

gi.require_version('Gio', '2.0')
from gi.repository import Gio


class CustomKeybindingsHandler:
    """Handles custom keybindings from gsettings"""
    
    def __init__(self, config_manager, transforms):
        self.config_manager = config_manager
        self.transforms = transforms
        self.schema = 'org.gnome.settings-daemon.plugins.media-keys'
        self.custom_schema = 'org.gnome.settings-daemon.plugins.media-keys.custom-keybinding'
        self.settings = None
        
        # Track custom keybindings: path -> {name, sanitized_name, command, binding}
        self.custom_keybindings: Dict[str, Dict] = {}
        # Track settings objects: path -> Gio.Settings
        self.custom_keybinding_settings: Dict[str, Gio.Settings] = {}
    
    def setup(self):
        """Setup monitoring for custom keybindings"""
        try:
            source = Gio.SettingsSchemaSource.get_default()
            
            if not source.lookup(self.schema, True):
                print(f"Custom keybindings schema not found", file=sys.stderr)
                return
            
            self.settings = Gio.Settings.new(self.schema)
            
            # Apply initial custom keybindings
            self._sync_custom_keybindings(self.settings)
            
            # Monitor changes to the custom-keybindings list
            self.settings.connect('changed::custom-keybindings', 
                                lambda s, k: self._sync_custom_keybindings(s))
            
            print("Custom keybindings monitoring enabled")
            
        except Exception as e:
            print(f"Error setting up custom keybindings: {e}", file=sys.stderr)
    
    def _sync_custom_keybindings(self, settings: Gio.Settings):
        """Sync all custom keybindings from gsettings"""
        try:
            # Get list of custom keybinding paths
            paths = settings.get_value('custom-keybindings').unpack()
            current_paths = set(paths)
            previous_paths = set(self.custom_keybindings.keys())
            
            # Remove deleted keybindings
            deleted_paths = previous_paths - current_paths
            for path in deleted_paths:
                self._remove_custom_keybinding(path)
            
            # Add or update existing keybindings
            for path in current_paths:
                if path in previous_paths:
                    self._update_custom_keybinding(path)
                else:
                    self._add_custom_keybinding(path)
            
            if deleted_paths or current_paths:
                self.config_manager.save()
                self.config_manager.reload_wayfire()
        
        except Exception as e:
            print(f"Error syncing custom keybindings: {e}", file=sys.stderr)
    
    def _add_custom_keybinding(self, path: str):
        """Add a new custom keybinding"""
        try:
            # Create settings object for this custom keybinding
            settings = Gio.Settings.new_with_path(self.custom_schema, path)
            
            # Get values
            name = settings.get_string('name')
            command = settings.get_string('command')
            binding = settings.get_string('binding')
            
            if not name or not command:
                print(f"Incomplete custom keybinding at {path}, skipping")
                return
            
            # Store tracking info
            sanitized_name = self.transforms.sanitize_name(name)
            self.custom_keybindings[path] = {
                'name': name,
                'sanitized_name': sanitized_name,
                'command': command,
                'binding': binding
            }
            self.custom_keybinding_settings[path] = settings
            
            # Apply to config
            self._apply_custom_keybinding(path)
            
            # Monitor changes
            settings.connect('changed::name', lambda s, k, p=path: self._update_custom_keybinding(p))
            settings.connect('changed::command', lambda s, k, p=path: self._update_custom_keybinding(p))
            settings.connect('changed::binding', lambda s, k, p=path: self._update_custom_keybinding(p))
            
            print(f"Added custom keybinding: {name} -> {command}")
            
        except Exception as e:
            print(f"Error adding custom keybinding {path}: {e}", file=sys.stderr)
    
    def _update_custom_keybinding(self, path: str):
        """Update an existing custom keybinding"""
        try:
            if path not in self.custom_keybinding_settings:
                return
            
            settings = self.custom_keybinding_settings[path]
            
            # Get updated values
            name = settings.get_string('name')
            command = settings.get_string('command')
            binding = settings.get_string('binding')
            
            # Get old sanitized name to remove old entries if name changed
            old_sanitized = self.custom_keybindings[path]['sanitized_name']
            new_sanitized = self.transforms.sanitize_name(name)
            
            # Update tracking
            self.custom_keybindings[path] = {
                'name': name,
                'sanitized_name': new_sanitized,
                'command': command,
                'binding': binding
            }
            
            # If name changed, remove old entries
            if old_sanitized != new_sanitized:
                self._remove_custom_keybinding_entries(old_sanitized)
            
            # Apply updated config
            self._apply_custom_keybinding(path)
            
            self.config_manager.save()
            self.config_manager.reload_wayfire()
            
            print(f"Updated custom keybinding: {name} -> {command}")
            
        except Exception as e:
            print(f"Error updating custom keybinding {path}: {e}", file=sys.stderr)
    
    def _remove_custom_keybinding(self, path: str):
        """Remove a custom keybinding"""
        try:
            if path in self.custom_keybindings:
                sanitized_name = self.custom_keybindings[path]['sanitized_name']
                self._remove_custom_keybinding_entries(sanitized_name)
                
                del self.custom_keybindings[path]
                if path in self.custom_keybinding_settings:
                    del self.custom_keybinding_settings[path]
                
                print(f"Removed custom keybinding: {sanitized_name}")
                
        except Exception as e:
            print(f"Error removing custom keybinding {path}: {e}", file=sys.stderr)
    
    def _remove_custom_keybinding_entries(self, sanitized_name: str):
        """Remove entries from config for a custom keybinding"""
        binding_key = f'binding_{sanitized_name}'
        command_key = f'command_{sanitized_name}'
        
        self.config_manager.remove_option('command', binding_key)
        self.config_manager.remove_option('command', command_key)
    
    def _apply_custom_keybinding(self, path: str):
        """Apply a custom keybinding to the config"""
        try:
            kb = self.custom_keybindings[path]
            sanitized_name = kb['sanitized_name']
            command = kb['command']
            binding = kb['binding']
            
            # Convert binding to Wayfire format
            wayfire_binding = self.transforms.convert_keybinding(binding) if binding else ''
            
            # Set binding and command
            if wayfire_binding:
                binding_key = f'binding_{sanitized_name}'
                command_key = f'command_{sanitized_name}'
                
                self.config_manager.set_value('command', binding_key, wayfire_binding)
                self.config_manager.set_value('command', command_key, command)
                
                print(f"Applied custom keybinding: {sanitized_name} = {wayfire_binding} -> {command}")
            else:
                # If no binding, remove entries
                self._remove_custom_keybinding_entries(sanitized_name)
                print(f"Removed binding for {sanitized_name} (no keybinding set)")
            
        except Exception as e:
            print(f"Error applying custom keybinding {path}: {e}", file=sys.stderr)