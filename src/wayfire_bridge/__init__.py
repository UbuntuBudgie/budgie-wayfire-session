"""
Wayfire Bridge Package
Synchronizes gsettings to Wayfire configuration
"""

__version__ = '1.0.0'
__author__ = 'Wayfire Bridge Contributors'

from .bridge import WayfireBridge
from .config_manager import ConfigManager
from .transforms import TransformFunctions
from .keybindings import CustomKeybindingsHandler
from .media_keys import MediaKeysHandler
from .budgie_wm_actions import BudgieWMActionsHandler

__all__ = [
    'WayfireBridge',
    'ConfigManager',
    'TransformFunctions',
    'CustomKeybindingsHandler',
    'MediaKeysHandler',
    'BudgieWMActionsHandler',
]
