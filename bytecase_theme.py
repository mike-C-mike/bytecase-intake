"""
Shared ByteCase desktop theme system.

This module is intentionally dependency-free so it remains easy to package with
PyInstaller and reuse across ByteCase Intake, Acquire, Verify, Notes, and Hub.
"""

from __future__ import annotations

import os
import platform
import subprocess
from typing import Any, Callable, Dict, Mapping, MutableMapping, Optional

import tkinter as tk
from tkinter import ttk


THEME_LIGHT = "light"
THEME_DARK = "dark"
THEME_SYSTEM = "system"

VALID_THEME_PREFERENCES = {THEME_LIGHT, THEME_DARK, THEME_SYSTEM}
THEME_DISPLAY_NAMES = ["Dark", "Light", "System Default"]

DARK_PALETTE: Dict[str, str] = {
    "app_background": "#0E1116",
    "panel_background": "#151B22",
    "elevated_surface": "#1B2128",
    "input_background": "#10161D",
    "border": "#2D3742",
    "border_strong": "#3A4654",
    "text_primary": "#F5F7FA",
    "text_secondary": "#C5CDD6",
    "text_muted": "#8D98A5",
    "accent": "#10B981",
    "accent_hover": "#18C98D",
    "accent_pressed": "#0D9668",
    "accent_soft": "#123B32",
    "selection": "#164C40",
    "focus_ring": "#34D399",
    "success": "#22C55E",
    "warning": "#F59E0B",
    "error": "#EF4444",
    "info": "#3B82F6",
    "disabled_background": "#202731",
    "disabled_text": "#66717E",
    "blue_dark": "#162536",
    "blue_mid": "#24415A",
    "blue_light": "#DCE8F1",
}

LIGHT_PALETTE: Dict[str, str] = {
    "app_background": "#F4F7F9",
    "panel_background": "#FFFFFF",
    "elevated_surface": "#EAF0F4",
    "input_background": "#FFFFFF",
    "border": "#CBD5DF",
    "border_strong": "#9EABB8",
    "text_primary": "#17212B",
    "text_secondary": "#364656",
    "text_muted": "#667585",
    "accent": "#07875F",
    "accent_hover": "#069B6C",
    "accent_pressed": "#056B4C",
    "accent_soft": "#DDF5EB",
    "selection": "#C9EDDF",
    "focus_ring": "#0EA875",
    "success": "#15803D",
    "warning": "#B45309",
    "error": "#B91C1C",
    "info": "#1D4ED8",
    "disabled_background": "#E4E9ED",
    "disabled_text": "#8B97A3",
    "blue_dark": "#162536",
    "blue_mid": "#24415A",
    "blue_light": "#DCE8F1",
}

PALETTES: Dict[str, Dict[str, str]] = {
    THEME_DARK: DARK_PALETTE,
    THEME_LIGHT: LIGHT_PALETTE,
}

FONT_FAMILY = "Segoe UI"
FONT_SIZE = 10
TITLE_FONT_SIZE = 16
SMALL_FONT_SIZE = 9


def normalize_theme_preference(value: Any) -> str:
    text = str(value or THEME_SYSTEM).strip().lower().replace("_", "-")

    if text in {"system", "system default", "default", "os", "os default"}:
        return THEME_SYSTEM
    if text in {"light", "light mode"}:
        return THEME_LIGHT
    if text in {"dark", "dark mode"}:
        return THEME_DARK

    return THEME_SYSTEM


def display_theme_preference(value: Any) -> str:
    preference = normalize_theme_preference(value)

    if preference == THEME_LIGHT:
        return "Light"
    if preference == THEME_DARK:
        return "Dark"
    return "System Default"


def theme_preference_from_display(value: Any) -> str:
    return normalize_theme_preference(value)


def resolve_system_theme() -> str:
    """
    Best-effort OS theme resolver.

    Windows is supported through the standard-library winreg module. macOS and
    Linux fall back safely when the platform does not expose a reliable value.
    """
    system = platform.system().lower()

    if system == "windows":
        try:
            import winreg  # type: ignore

            key_path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                apps_use_light_theme, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return THEME_LIGHT if int(apps_use_light_theme) == 1 else THEME_DARK
        except Exception:
            return THEME_DARK

    if system == "darwin":
        try:
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True,
                text=True,
                timeout=1,
                check=False,
            )
            return THEME_DARK if "dark" in result.stdout.strip().lower() else THEME_LIGHT
        except Exception:
            return THEME_LIGHT

    desktop_theme = os.environ.get("GTK_THEME", "").lower()
    color_scheme = os.environ.get("COLOR_SCHEME", "").lower()

    if "dark" in desktop_theme or "dark" in color_scheme:
        return THEME_DARK

    return THEME_DARK


def get_current_theme(settings_or_preference: Any) -> str:
    if isinstance(settings_or_preference, Mapping):
        preference = settings_or_preference.get("appearance", {}).get("theme", THEME_SYSTEM)
    else:
        preference = settings_or_preference

    preference = normalize_theme_preference(preference)

    if preference == THEME_SYSTEM:
        return resolve_system_theme()

    return preference


def get_palette(theme_name: str) -> Dict[str, str]:
    resolved = theme_name if theme_name in PALETTES else THEME_DARK
    return PALETTES[resolved].copy()


def save_theme_preference(
    settings: MutableMapping[str, Any],
    theme_preference: Any,
    save_callback: Optional[Callable[[MutableMapping[str, Any]], None]] = None,
) -> MutableMapping[str, Any]:
    settings.setdefault("appearance", {})
    settings["appearance"]["theme"] = normalize_theme_preference(theme_preference)

    if save_callback:
        save_callback(settings)

    return settings


def _configure_root_options(root: tk.Misc, colors: Mapping[str, str]) -> None:
    # These option database values affect classic Tk widgets and menus where the
    # platform/theme allows it. Native file pickers and message boxes may ignore them.
    root.option_add("*Font", f"{{{FONT_FAMILY}}} {FONT_SIZE}")
    root.option_add("*Background", colors["app_background"])
    root.option_add("*Foreground", colors["text_primary"])
    root.option_add("*selectBackground", colors["selection"])
    root.option_add("*selectForeground", colors["text_primary"])
    root.option_add("*insertBackground", colors["focus_ring"])
    root.option_add("*Menu.background", colors["elevated_surface"])
    root.option_add("*Menu.foreground", colors["text_primary"])
    root.option_add("*Menu.activeBackground", colors["selection"])
    root.option_add("*Menu.activeForeground", colors["text_primary"])


def apply_theme(root: tk.Misc, settings_or_preference: Any) -> Dict[str, Any]:
    """
    Apply the shared ByteCase theme to Tk/ttk widgets.

    Returns a small theme state dictionary containing the requested preference,
    resolved theme, and semantic color token map.
    """
    requested = (
        settings_or_preference.get("appearance", {}).get("theme", THEME_SYSTEM)
        if isinstance(settings_or_preference, Mapping)
        else settings_or_preference
    )
    preference = normalize_theme_preference(requested)
    resolved_theme = get_current_theme(preference)
    colors = get_palette(resolved_theme)

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    if isinstance(root, (tk.Tk, tk.Toplevel)):
        root.configure(bg=colors["app_background"])

    _configure_root_options(root, colors)

    default_font = (FONT_FAMILY, FONT_SIZE)
    title_font = (FONT_FAMILY, TITLE_FONT_SIZE, "bold")
    section_font = (FONT_FAMILY, FONT_SIZE, "bold")
    small_font = (FONT_FAMILY, SMALL_FONT_SIZE)

    style.configure(
        ".",
        background=colors["app_background"],
        foreground=colors["text_primary"],
        fieldbackground=colors["input_background"],
        bordercolor=colors["border"],
        lightcolor=colors["border"],
        darkcolor=colors["border_strong"],
        troughcolor=colors["elevated_surface"],
        font=default_font,
    )

    style.configure("TFrame", background=colors["app_background"])
    style.configure("Panel.TFrame", background=colors["panel_background"])
    style.configure("Card.TFrame", background=colors["elevated_surface"])

    style.configure("TLabel", background=colors["app_background"], foreground=colors["text_primary"])
    style.configure("Panel.TLabel", background=colors["panel_background"], foreground=colors["text_primary"])
    style.configure("Title.TLabel", background=colors["app_background"], foreground=colors["text_primary"], font=title_font)
    style.configure("Subtitle.TLabel", background=colors["app_background"], foreground=colors["text_secondary"], font=default_font)
    style.configure("Muted.TLabel", background=colors["app_background"], foreground=colors["text_muted"], font=small_font)
    style.configure("Info.TLabel", background=colors["app_background"], foreground=colors["info"], font=small_font)
    style.configure("Success.TLabel", background=colors["app_background"], foreground=colors["success"], font=small_font)
    style.configure("Warning.TLabel", background=colors["app_background"], foreground=colors["warning"], font=small_font)
    style.configure("Error.TLabel", background=colors["app_background"], foreground=colors["error"], font=small_font)

    style.configure("TLabelframe", background=colors["app_background"], foreground=colors["text_primary"], bordercolor=colors["border"])
    style.configure("TLabelframe.Label", background=colors["app_background"], foreground=colors["text_secondary"], font=section_font)

    style.configure(
        "TButton",
        background=colors["elevated_surface"],
        foreground=colors["text_primary"],
        bordercolor=colors["border_strong"],
        focusthickness=1,
        focuscolor=colors["focus_ring"],
        padding=(10, 6),
    )
    style.map(
        "TButton",
        background=[("disabled", colors["disabled_background"]), ("pressed", colors["blue_dark"]), ("active", colors["blue_mid"])],
        foreground=[("disabled", colors["disabled_text"]), ("pressed", colors["text_primary"]), ("active", colors["text_primary"])],
        bordercolor=[("focus", colors["focus_ring"])],
    )

    style.configure(
        "Primary.TButton",
        background=colors["accent"],
        foreground=colors["app_background"],
        bordercolor=colors["accent_pressed"],
        focusthickness=1,
        focuscolor=colors["focus_ring"],
        padding=(10, 6),
    )
    style.map(
        "Primary.TButton",
        background=[("disabled", colors["disabled_background"]), ("pressed", colors["accent_pressed"]), ("active", colors["accent_hover"])],
        foreground=[("disabled", colors["disabled_text"]), ("pressed", colors["app_background"]), ("active", colors["app_background"])],
        bordercolor=[("focus", colors["focus_ring"])],
    )

    style.configure("TCheckbutton", background=colors["app_background"], foreground=colors["text_primary"], focuscolor=colors["focus_ring"])
    style.map(
        "TCheckbutton",
        background=[("active", colors["app_background"]), ("disabled", colors["app_background"])],
        foreground=[("active", colors["accent"]), ("disabled", colors["disabled_text"])],
    )

    style.configure(
        "TEntry",
        fieldbackground=colors["input_background"],
        foreground=colors["text_primary"],
        bordercolor=colors["border"],
        insertcolor=colors["focus_ring"],
        lightcolor=colors["border"],
        darkcolor=colors["border_strong"],
        padding=4,
    )
    style.map(
        "TEntry",
        fieldbackground=[("disabled", colors["disabled_background"]), ("readonly", colors["elevated_surface"])],
        foreground=[("disabled", colors["disabled_text"]), ("readonly", colors["text_secondary"])],
        bordercolor=[("focus", colors["focus_ring"])],
    )

    style.configure(
        "TCombobox",
        fieldbackground=colors["input_background"],
        background=colors["elevated_surface"],
        foreground=colors["text_primary"],
        bordercolor=colors["border"],
        arrowcolor=colors["accent"],
        insertcolor=colors["focus_ring"],
        padding=4,
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", colors["input_background"]), ("disabled", colors["disabled_background"])],
        foreground=[("readonly", colors["text_primary"]), ("disabled", colors["disabled_text"])],
        background=[("active", colors["elevated_surface"])],
        bordercolor=[("focus", colors["focus_ring"])],
        arrowcolor=[("disabled", colors["disabled_text"]), ("active", colors["accent_hover"])],
    )

    is_dark = resolved_theme == THEME_DARK

    # Tabs and tables deliberately avoid high-contrast hover flips. For long
    # review sessions, a stable surface is more readable than a dramatic hover
    # state, especially on Treeview headings where some Tk themes can otherwise
    # fall back to near-white active cells.
    tab_bg = colors["elevated_surface"] if is_dark else colors["panel_background"]
    tab_selected_bg = colors["selection"] if is_dark else colors["accent_soft"]
    tab_active_bg = colors["accent_soft"] if is_dark else colors["blue_light"]
    tab_fg = colors["text_secondary"]
    tab_selected_fg = colors["text_primary"]
    tab_border = colors["border_strong"] if is_dark else colors["border"]

    style.configure("TNotebook", background=colors["app_background"], bordercolor=colors["border"])
    style.configure(
        "TNotebook.Tab",
        background=tab_bg,
        foreground=tab_fg,
        bordercolor=tab_border,
        padding=(12, 6),
    )
    style.map(
        "TNotebook.Tab",
        background=[
            ("selected", tab_selected_bg),
            ("active", tab_active_bg),
            ("!selected", tab_bg),
        ],
        foreground=[
            ("selected", tab_selected_fg),
            ("active", tab_selected_fg if is_dark else colors["text_primary"]),
            ("!selected", tab_fg),
        ],
        bordercolor=[
            ("selected", colors["accent"]),
            ("active", colors["border_strong"]),
            ("!active", tab_border),
        ],
    )

    table_header_bg = colors["elevated_surface"] if is_dark else colors["elevated_surface"]
    table_header_active_bg = table_header_bg
    table_header_fg = colors["text_primary"]
    table_header_border = colors["border_strong"] if is_dark else colors["border"]
    table_body_bg = colors["input_background"] if is_dark else colors["panel_background"]
    table_selected_bg = colors["selection"]
    table_selected_fg = colors["text_primary"]

    style.configure(
        "Treeview",
        background=table_body_bg,
        fieldbackground=table_body_bg,
        foreground=colors["text_primary"],
        bordercolor=colors["border"],
        lightcolor=colors["border"],
        darkcolor=colors["border_strong"],
        rowheight=25,
    )
    style.configure(
        "Treeview.Heading",
        background=table_header_bg,
        foreground=table_header_fg,
        bordercolor=table_header_border,
        relief="flat",
        font=section_font,
    )
    style.map(
        "Treeview.Heading",
        background=[
            ("pressed", table_header_active_bg),
            ("active", table_header_active_bg),
            ("!active", table_header_bg),
        ],
        foreground=[
            ("pressed", table_header_fg),
            ("active", table_header_fg),
            ("!active", table_header_fg),
        ],
        bordercolor=[
            ("pressed", colors["accent"]),
            ("active", colors["border_strong"]),
            ("!active", table_header_border),
        ],
    )
    style.map(
        "Treeview",
        background=[("selected", table_selected_bg), ("!selected", table_body_bg)],
        foreground=[("selected", table_selected_fg), ("!selected", colors["text_primary"])],
    )

    style.configure(
        "Vertical.TScrollbar",
        background=colors["elevated_surface"],
        troughcolor=colors["app_background"],
        bordercolor=colors["border"],
        arrowcolor=colors["text_secondary"],
    )
    style.configure(
        "Horizontal.TScrollbar",
        background=colors["elevated_surface"],
        troughcolor=colors["app_background"],
        bordercolor=colors["border"],
        arrowcolor=colors["text_secondary"],
    )
    style.map(
        "Vertical.TScrollbar",
        background=[("active", colors["blue_mid"]), ("pressed", colors["accent_pressed"])],
        arrowcolor=[("active", colors["text_primary"])],
    )
    style.map(
        "Horizontal.TScrollbar",
        background=[("active", colors["blue_mid"]), ("pressed", colors["accent_pressed"])],
        arrowcolor=[("active", colors["text_primary"])],
    )

    style.configure(
        "TProgressbar",
        background=colors["accent"],
        troughcolor=colors["elevated_surface"],
        bordercolor=colors["border"],
        lightcolor=colors["accent_hover"],
        darkcolor=colors["accent_pressed"],
    )

    return {
        "preference": preference,
        "resolved_theme": resolved_theme,
        "colors": colors,
    }


def style_text_widget(widget: tk.Text, colors: Mapping[str, str]) -> None:
    widget.configure(
        background=colors["input_background"],
        foreground=colors["text_primary"],
        insertbackground=colors["focus_ring"],
        selectbackground=colors["selection"],
        selectforeground=colors["text_primary"],
        relief="solid",
        borderwidth=1,
        highlightthickness=1,
        highlightbackground=colors["border"],
        highlightcolor=colors["focus_ring"],
    )


def configure_toplevel(window: tk.Toplevel, colors: Mapping[str, str]) -> None:
    window.configure(bg=colors["app_background"])
