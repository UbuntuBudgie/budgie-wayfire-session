"""
Configuration file management for Wayfire Bridge
"""

import configparser
from pathlib import Path

from .logging_config import get_logger

log = get_logger(__name__)


class ConfigManager:
    """Manages wayfire.ini configuration file"""

    def __init__(self, config_path=None):
        if config_path is None:
            self.config_path = Path.home() / '.config' / 'budgie-desktop' / 'wayfire' / 'wayfire.ini'
        else:
            self.config_path = Path(config_path)

        # Use strict=False to allow duplicate keys (last one wins)
        self.config = configparser.ConfigParser(
            interpolation=None,
            strict=False,  # Allow duplicate keys - last value wins
            allow_no_value=True  # Allow keys without values
        )
        self.config.optionxform = str  # Preserve case sensitivity

        # Load existing config or create new one
        if self.config_path.exists():
            try:
                self.config.read(self.config_path)
                log.info("Loaded existing config from %s", self.config_path)
            except configparser.Error as e:
                log.error("Error reading config file: %s", e)
                log.warning("Creating backup and starting with fresh config")
                # Backup the problematic file
                backup_path = self.config_path.with_suffix('.ini.backup')
                try:
                    self.config_path.rename(backup_path)
                    log.info("Backed up problematic config to %s", backup_path)
                except Exception:
                    log.exception("Could not backup config file")
        else:
            log.info("Will create new config at %s", self.config_path)

        # Ensure critical autostart section exists for budgie-desktop
        self._ensure_autostart_section()

    # ------------------------------------------------------------------
    # Public accessors
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_autostart_section(self):
        """Ensure the critical autostart section exists for budgie-desktop"""
        if 'autostart' not in self.config:
            self.config['autostart'] = {}

        autostart = self.config['autostart']

        if autostart.get('desktop') != 'budgie-desktop':
            log.debug("Creating/updating autostart section for budgie-desktop")

            autostart.setdefault(
                '0_env',
                'dbus-update-activation-environment --systemd WAYLAND_DISPLAY DISPLAY XAUTHORITY',
            )
            autostart.setdefault('autostart_wf_shell', 'false')
            autostart.setdefault('portal', '/usr/libexec/xdg-desktop-portal')
            autostart.setdefault('desktop', 'budgie-desktop')

            log.debug("Autostart section configured for budgie-desktop")
        else:
            log.debug("Autostart section already configured correctly")

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self):
        """Write configuration to wayfire.ini"""
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            log.debug("Saving configuration to %s", self.config_path)

            if log.isEnabledFor(10):  # DEBUG
                if 'input' in self.config:
                    log.debug(
                        "[input] section has %d keys  xkb_layout=%r",
                        len(self.config['input']),
                        self.config['input'].get('xkb_layout', '<unset>'),
                    )
                if 'command' in self.config:
                    terminal_keys = [
                        k for k in self.config['command'] if 'terminal' in k.lower()
                    ]
                    if terminal_keys:
                        for k in terminal_keys:
                            log.debug("[command] %s = %s", k, self.config['command'][k])

            with open(self.config_path, 'w') as f:
                self.config.write(f)
                f.flush()

            log.debug("Configuration written to %s", self.config_path)

        except Exception:
            log.exception("Error saving config to %s", self.config_path)

    def reload_wayfire(self):
        """Wayfire watches wayfire.ini and reloads it automatically.
        
        Note: Environment file changes require a full Wayfire restart to take effect.
        The `wayfire -r` command only reloads wayfire.ini, not environment variables.
        """
        log.debug("Wayfire will auto-reload configuration")
        # Environment variables are only read at Wayfire startup
        # A full restart is needed for XKB_DEFAULT_LAYOUT, XCURSOR_*, etc.
