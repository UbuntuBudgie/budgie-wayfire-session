"""
Core bridge logic for Wayfire Bridge
"""

import sys
from typing import Dict
import gi

gi.require_version('Gio', '2.0')
gi.require_version('GLib', '2.0')
from gi.repository import Gio, GLib

from .config_manager import ConfigManager
from .keybindings import CustomKeybindingsHandler
from .media_keys import MediaKeysHandler
from .mappings import GSETTINGS_MAPPINGS
from .transforms import TransformFunctions
from .budgie_wm_actions import BudgieWMActionsHandler


class WayfireBridge:
    """Main bridge coordinator"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.transforms = TransformFunctions()
        self.settings_objects: Dict[str, Gio.Settings] = {}
        
        # Initialize handlers
        self.keybindings_handler = CustomKeybindingsHandler(
            self.config_manager, 
            self.transforms
        )
        self.media_keys_handler = MediaKeysHandler(
            self.config_manager,
            self.transforms
        )

        self.budgie_wm_handler = BudgieWMActionsHandler(
            self.config_manager,
            self.transforms
        )
        
        # Setup all gsettings monitoring
        self.setup_gsettings()
        self.keybindings_handler.setup()
        self.media_keys_handler.setup()
        self.budgie_wm_handler.setup()
    
    def setup_gsettings(self):
        """Setup gsettings monitoring for all mapped keys"""
        for (schema, key), mapping in GSETTINGS_MAPPINGS.items():
            try:
                section = mapping['section']
                option = mapping['option']
                transform_name = mapping.get('transform', 'str')
                
                # Get transform function
                transform = getattr(self.transforms, transform_name)
                
                # Check if schema exists
                source = Gio.SettingsSchemaSource.get_default()
                if not source.lookup(schema, True):
                    print(f"Schema {schema} not found, skipping", file=sys.stderr)
                    continue
                
                # Create settings object if not exists
                if schema not in self.settings_objects:
                    self.settings_objects[schema] = Gio.Settings.new(schema)
                
                settings = self.settings_objects[schema]
                
                # Apply initial value
                self._apply_setting(schema, key, section, option, transform)
                
                # Connect change signal
                settings.connect(
                    f'changed::{key}',
                    lambda s, k, sc=schema, se=section, o=option, t=transform: 
                        self._on_setting_changed(sc, k, se, o, t)
                )
                
            except Exception as e:
                print(f"Error setting up {schema}::{key}: {e}", file=sys.stderr)
    
    def _apply_setting(self, schema: str, key: str, section: str, 
                       option: str, transform):
        """Apply a gsettings value to wayfire config"""
        try:
            settings = self.settings_objects[schema]
            value = settings.get_value(key).unpack()
            transformed_value = transform(value)
            
            # Debug: Show what we're setting
            print(f"Applying {schema}::{key}")
            print(f"  → Raw value: {value} (type: {type(value).__name__})")
            print(f"  → Transformed: {transformed_value} (type: {type(transformed_value).__name__})")
            print(f"  → Target: [{section}] {option}")
            
            self.config_manager.set_value(section, option, str(transformed_value))
            
            # Verify it was set
            check_value = self.config_manager.get_value(section, option)
            print(f"  → Verified in config: {check_value}")
            
            print(f"✓ Applied {schema}::{key} -> [{section}] {option} = {transformed_value}")
            
        except Exception as e:
            print(f"Error applying {schema}::{key}: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
    
    def _on_setting_changed(self, schema: str, key: str, section: str, 
                           option: str, transform):
        """Handle gsettings change"""
        print(f"Setting changed: {schema}::{key}")
        self._apply_setting(schema, key, section, option, transform)
        self.config_manager.save()
        self.config_manager.reload_wayfire()
    
    def run(self):
        """Run the bridge (blocking)"""
        print("=" * 60)
        print("Wayfire Bridge started")
        print("=" * 60)
        print(f"Config file: {self.config_manager.config_path}")
        print(f"Monitoring {len(GSETTINGS_MAPPINGS)} gsettings keys")
        print(f"Custom keybindings: enabled")
        print(f"Media keys: enabled")
        print("=" * 60)
        
        # Save initial configuration
        self.config_manager.save()
        
        # Run main loop
        try:
            loop = GLib.MainLoop()
            loop.run()
        except KeyboardInterrupt:
            print("\nShutting down Wayfire Bridge...")