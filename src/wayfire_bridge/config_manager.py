"""
Configuration file management for Wayfire Bridge
"""

import subprocess
import configparser
from pathlib import Path


class ConfigManager:
    """Manages wayfire.ini configuration file"""
    
    def __init__(self, config_path=None):
        if config_path is None:
            self.config_path = Path.home() / '.config' / 'budgie-desktop' / 'wayfire' / 'wayfire.ini'
        else:
            self.config_path = Path(config_path)
        
        self.config = configparser.ConfigParser()
        self.config.optionxform = str  # Preserve case sensitivity
        
        # Load existing config or create new one
        if self.config_path.exists():
            self.config.read(self.config_path)
            print(f"Loaded existing config from {self.config_path}")
        else:
            print(f"Will create new config at {self.config_path}")
        
        # Ensure critical autostart section exists for budgie-desktop
        self._ensure_autostart_section()
    
    def set_value(self, section: str, option: str, value: str):
        """Set a configuration value"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][option] = value
    
    def get_value(self, section: str, option: str, default=None):
        """Get a configuration value"""
        if section in self.config and option in self.config[section]:
            return self.config[section][option]
        return default
    
    def remove_option(self, section: str, option: str):
        """Remove a configuration option"""
        if section in self.config and option in self.config[section]:
            del self.config[section][option]
    
    def has_option(self, section: str, option: str) -> bool:
        """Check if an option exists"""
        return section in self.config and option in self.config[section]
    
    def _ensure_autostart_section(self):
        """Ensure critical autostart section exists for budgie-desktop"""
        if 'autostart' not in self.config:
            self.config['autostart'] = {}
        
        autostart = self.config['autostart']
        
        # Check if budgie-desktop entry exists
        if 'desktop' not in autostart or autostart['desktop'] != 'budgie-desktop':
            print("Creating/updating autostart section for budgie-desktop")
            
            # Essential entries for budgie-desktop to work
            if '0_env' not in autostart:
                autostart['0_env'] = 'dbus-update-activation-environment --systemd WAYLAND_DISPLAY DISPLAY XAUTHORITY'
            
            if 'autostart_wf_shell' not in autostart:
                autostart['autostart_wf_shell'] = 'false'
            
            if 'portal' not in autostart:
                autostart['portal'] = '/usr/libexec/xdg-desktop-portal'
            
            if 'desktop' not in autostart:
                autostart['desktop'] = 'budgie-desktop'
            
            print("Autostart section configured for budgie-desktop")
        else:
            print("Autostart section already configured")
    
    def save(self):
        """Save configuration to wayfire.ini"""
        try:
            # Ensure config directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Debug: Show what we're about to save
            print(f"Saving configuration to {self.config_path}")
            if 'input' in self.config:
                print(f"  [input] section has {len(self.config['input'])} keys")
                if 'xkb_layout' in self.config['input']:
                    print(f"    → xkb_layout in memory: '{self.config['input']['xkb_layout']}'")
            if 'command' in self.config:
                print(f"  [command] section has {len(self.config['command'])} keys")
                terminal_keys = [k for k in self.config['command'] if 'terminal' in k.lower()]
                if terminal_keys:
                    print(f"    → Terminal-related keys: {terminal_keys}")
                    for k in terminal_keys:
                        print(f"      {k} = {self.config['command'][k]}")
            
            # Write config
            with open(self.config_path, 'w') as f:
                self.config.write(f)
                f.flush()  # Ensure written to disk
            
            print(f"✓ Configuration written to {self.config_path}")
            
            # Verify what was actually written by reading it back
            print("Verifying written file...")
            with open(self.config_path, 'r') as f:
                lines = f.readlines()
                in_input = False
                in_command = False
                for line in lines:
                    if line.strip() == '[input]':
                        in_input = True
                        in_command = False
                    elif line.strip() == '[command]':
                        in_command = True
                        in_input = False
                    elif line.strip().startswith('['):
                        in_input = False
                        in_command = False
                    elif in_input and 'xkb_layout' in line and not line.strip().startswith('#'):
                        print(f"  → Found in file: {line.strip()}")
                    elif in_command and 'terminal' in line.lower() and not line.strip().startswith('#'):
                        print(f"  → Found in file: {line.strip()}")
            
        except Exception as e:
            print(f"Error saving config: {e}")
            import traceback
            traceback.print_exc()
    
    def reload_wayfire(self):
        """Wayfire automatically reloads wayfire.ini - no action needed"""
        # Wayfire watches wayfire.ini and automatically applies changes
        # No need to send SIGUSR2 signal
        print("Wayfire will auto-reload configuration")