"""
Mappings from gsettings to Wayfire configuration
Format: (schema, key): {'section': ..., 'option': ..., 'transform': ...}
"""

GSETTINGS_MAPPINGS = {
    # ==========================================================================
    # Desktop Interface Settings
    # ==========================================================================
    ('org.gnome.desktop.interface', 'cursor-theme'): {
        'section': 'input',
        'option': 'cursor_theme',
        'transform': 'str'
    },
    ('org.gnome.desktop.interface', 'cursor-size'): {
        'section': 'input',
        'option': 'cursor_size',
        'transform': 'int'
    },
    ('org.gnome.desktop.interface', 'gtk-theme'): {
        'section': 'core',
        'option': 'gtk_theme',
        'transform': 'str'
    },
    
    # ==========================================================================
    # Window Manager Preferences
    # ==========================================================================
    ('org.gnome.desktop.wm.preferences', 'button-layout'): {
        'section': 'decoration',
        'option': 'button_order',
        'transform': 'button_layout'
    },
    ('org.gnome.desktop.wm.preferences', 'focus-mode'): {
        'section': 'core',
        'option': 'focus_mode',
        'transform': 'focus_mode'
    },
    ('org.gnome.desktop.wm.preferences', 'num-workspaces'): {
        'section': 'vswitch',
        'option': 'vwidth',
        'transform': 'int'
    },
    
    # ==========================================================================
    # Window Manager Keybindings
    # ==========================================================================
    ('org.gnome.desktop.wm.keybindings', 'close'): {
        'section': 'command',
        'option': 'binding_close',
        'transform': 'keybinding'
    },
    ('org.gnome.desktop.wm.keybindings', 'maximize'): {
        'section': 'command',
        'option': 'binding_maximize',
        'transform': 'keybinding'
    },
    ('org.gnome.desktop.wm.keybindings', 'minimize'): {
        'section': 'command',
        'option': 'binding_minimize',
        'transform': 'keybinding'
    },
    ('org.gnome.desktop.wm.keybindings', 'move-to-workspace-left'): {
        'section': 'command',
        'option': 'binding_move_left',
        'transform': 'keybinding'
    },
    ('org.gnome.desktop.wm.keybindings', 'move-to-workspace-right'): {
        'section': 'command',
        'option': 'binding_move_right',
        'transform': 'keybinding'
    },
    ('org.gnome.desktop.wm.keybindings', 'switch-to-workspace-left'): {
        'section': 'vswitch',
        'option': 'binding_left',
        'transform': 'keybinding'
    },
    ('org.gnome.desktop.wm.keybindings', 'switch-to-workspace-right'): {
        'section': 'vswitch',
        'option': 'binding_right',
        'transform': 'keybinding'
    },
    ('org.gnome.desktop.wm.keybindings', 'switch-to-workspace-up'): {
        'section': 'vswitch',
        'option': 'binding_up',
        'transform': 'keybinding'
    },
    ('org.gnome.desktop.wm.keybindings', 'switch-to-workspace-down'): {
        'section': 'vswitch',
        'option': 'binding_down',
        'transform': 'keybinding'
    },
    
    # ==========================================================================
    # Peripherals - Mouse
    # ==========================================================================
    ('org.gnome.desktop.peripherals.mouse', 'natural-scroll'): {
        'section': 'input',
        'option': 'natural_scroll',
        'transform': 'bool'
    },
    ('org.gnome.desktop.peripherals.mouse', 'accel-profile'): {
        'section': 'input',
        'option': 'mouse_accel_profile',
        'transform': 'str'
    },
    ('org.gnome.desktop.peripherals.mouse', 'speed'): {
        'section': 'input',
        'option': 'mouse_cursor_speed',
        'transform': 'float'
    },
    ('org.gnome.desktop.peripherals.mouse', 'left-handed'): {
        'section': 'input',
        'option': 'left_handed_mode',
        'transform': 'bool'
    },
    
    # ==========================================================================
    # Peripherals - Touchpad (libinput)
    # ==========================================================================
    ('org.gnome.desktop.peripherals.touchpad', 'natural-scroll'): {
        'section': 'input',
        'option': 'touchpad_natural_scroll',
        'transform': 'bool'
    },
    ('org.gnome.desktop.peripherals.touchpad', 'tap-to-click'): {
        'section': 'input',
        'option': 'tap_to_click',
        'transform': 'bool'
    },
    ('org.gnome.desktop.peripherals.touchpad', 'two-finger-scrolling-enabled'): {
        'section': 'input',
        'option': 'scroll_method',
        'transform': 'scroll_method'
    },
    ('org.gnome.desktop.peripherals.touchpad', 'speed'): {
        'section': 'input',
        'option': 'touchpad_cursor_speed',
        'transform': 'float'
    },
    ('org.gnome.desktop.peripherals.touchpad', 'left-handed'): {
        'section': 'input',
        'option': 'touchpad_left_handed_mode',
        'transform': 'bool'
    },
    ('org.gnome.desktop.peripherals.touchpad', 'disable-while-typing'): {
        'section': 'input',
        'option': 'disable_while_typing',
        'transform': 'bool'
    },
    ('org.gnome.desktop.peripherals.touchpad', 'click-method'): {
        'section': 'input',
        'option': 'click_method',
        'transform': 'str'
    },
    ('org.gnome.desktop.peripherals.touchpad', 'send-events'): {
        'section': 'input',
        'option': 'touchpad_send_events',
        'transform': 'str'
    },
    
    # ==========================================================================
    # Peripherals - Keyboard
    # ==========================================================================
    ('org.gnome.desktop.peripherals.keyboard', 'delay'): {
        'section': 'input',
        'option': 'kb_repeat_delay',
        'transform': 'int'
    },
    ('org.gnome.desktop.peripherals.keyboard', 'repeat-interval'): {
        'section': 'input',
        'option': 'kb_repeat_rate',
        'transform': 'kb_repeat_rate'
    },
    ('org.gnome.desktop.peripherals.keyboard', 'numlock-state'): {
        'section': 'input',
        'option': 'kb_numlock_default_state',
        'transform': 'bool'
    },
    
    # ==========================================================================
    # Input Sources (Keyboard Layout)
    # ==========================================================================
    ('org.gnome.desktop.input-sources', 'sources'): {
        'section': 'input',
        'option': 'xkb_layout',
        'transform': 'xkb_layout'
    },
    ('org.gnome.desktop.input-sources', 'xkb-options'): {
        'section': 'input',
        'option': 'xkb_options',
        'transform': 'xkb_options'
    },
    
    # ==========================================================================
    # Display Settings (Night Light)
    # ==========================================================================
    ('org.gnome.settings-daemon.plugins.color', 'night-light-enabled'): {
        'section': 'gamma',
        'option': 'enabled',
        'transform': 'bool'
    },
    ('org.gnome.settings-daemon.plugins.color', 'night-light-temperature'): {
        'section': 'gamma',
        'option': 'temperature',
        'transform': 'int'
    },
}