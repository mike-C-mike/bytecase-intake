import json
import sys
from pathlib import Path

from bytecase_theme import normalize_theme_preference


APP_NAME = "ByteCase Intake"
APP_SUBTITLE = "Digital Forensics Request Builder"
APP_VERSION = "0.9.0"

SUITE_NAME = "ByteCase"
PUBLISHER_NAME = "Forensics Byte"
PRODUCT_DOMAIN = "byte-case.com"

TOOL_FOLDER_NAME = "intake"
DEFAULT_ROOT_FOLDER_NAME = "ByteCase"


def get_base_dir():
    """
    Returns the directory where the app should create local settings files.

    When running from source, this is the project folder.
    When running as a PyInstaller executable, this is the folder containing the exe.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent

    return Path(__file__).parent


BASE_DIR = get_base_dir()
SETTINGS_PATH = BASE_DIR / "settings.json"


DEFAULT_SETTINGS = {
    "suite_name": SUITE_NAME,
    "publisher": PUBLISHER_NAME,
    "agency_name": "",
    "unit_name": "",
    "default_investigator": "",
    "investigators": [],
    "appearance": {
        "theme": "system"
    },
    "output_paths": {
        "base_output_dir": "",
        "use_shared_bytecase_root": True
    },
    "report_branding": {
        "patch_image_path": ""
    },
    "report_defaults": {
        "include_acknowledgement_block": True
    }
}


def deep_merge(default, loaded):
    result = default.copy()

    for key, value in loaded.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def normalize_settings(settings):
    appearance = settings.get("appearance", {})

    if not isinstance(appearance, dict):
        appearance = {}

    theme = normalize_theme_preference(appearance.get("theme", "system"))

    settings["appearance"] = {
        "theme": theme
    }

    investigators = settings.get("investigators", [])

    if not isinstance(investigators, list):
        investigators = []

    cleaned_investigators = []
    seen = set()

    for investigator in investigators:
        investigator = str(investigator).strip()

        if not investigator:
            continue

        key = investigator.lower()

        if key not in seen:
            cleaned_investigators.append(investigator)
            seen.add(key)

    default_investigator = str(settings.get("default_investigator", "")).strip()

    if default_investigator:
        key = default_investigator.lower()

        if key not in seen:
            cleaned_investigators.insert(0, default_investigator)

    settings["investigators"] = cleaned_investigators

    output_paths = settings.get("output_paths", {})

    if not isinstance(output_paths, dict):
        output_paths = {}

    settings["output_paths"] = {
        "base_output_dir": str(output_paths.get("base_output_dir", "")).strip(),
        "use_shared_bytecase_root": bool(output_paths.get("use_shared_bytecase_root", True))
    }

    report_defaults = settings.get("report_defaults", {})

    if not isinstance(report_defaults, dict):
        report_defaults = {}

    settings["report_defaults"] = {
        "include_acknowledgement_block": bool(
            report_defaults.get("include_acknowledgement_block", True)
        )
    }

    report_branding = settings.get("report_branding", {})

    if not isinstance(report_branding, dict):
        report_branding = {}

    settings["report_branding"] = {
        "patch_image_path": str(report_branding.get("patch_image_path", "")).strip()
    }

    settings["suite_name"] = str(settings.get("suite_name", SUITE_NAME)).strip() or SUITE_NAME
    settings["publisher"] = str(settings.get("publisher", PUBLISHER_NAME)).strip() or PUBLISHER_NAME
    settings["agency_name"] = str(settings.get("agency_name", "")).strip()
    settings["unit_name"] = str(settings.get("unit_name", "")).strip()
    settings["default_investigator"] = default_investigator

    return settings


def load_or_create_settings():
    if not SETTINGS_PATH.exists():
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

    try:
        with SETTINGS_PATH.open("r", encoding="utf-8") as f:
            loaded = json.load(f)

        settings = deep_merge(DEFAULT_SETTINGS, loaded)
        return normalize_settings(settings)

    except (json.JSONDecodeError, OSError):
        return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    settings = normalize_settings(settings)

    with SETTINGS_PATH.open("w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


def safe_case_folder_name(case_number):
    value = str(case_number or "").strip()

    if not value:
        value = "NO_CASE"

    for char in '<>:"/\\|?*':
        value = value.replace(char, "_")

    value = value.replace(" ", "_")

    while "__" in value:
        value = value.replace("__", "_")

    return value.strip("_") or "NO_CASE"


def get_default_output_root():
    """
    Default shared ByteCase output root.

    Example:
    C:\\Users\\Matt\\ByteCase
    """
    return Path.home() / DEFAULT_ROOT_FOLDER_NAME


def get_output_root(settings):
    output_settings = settings.get("output_paths", {})
    base_output_dir = str(output_settings.get("base_output_dir", "")).strip()

    if base_output_dir:
        return Path(base_output_dir)

    return get_default_output_root()


def get_case_tool_paths(settings, case_number):
    """
    Returns the shared ByteCase folder structure for this tool.

    Example:
    C:\\Users\\Matt\\ByteCase\\2600001\\intake
    """
    root_dir = get_output_root(settings)
    case_folder_name = safe_case_folder_name(case_number)

    case_dir = root_dir / case_folder_name
    tool_dir = case_dir / TOOL_FOLDER_NAME
    attachments_dir = tool_dir / "attachments"

    return {
        "root_dir": root_dir,
        "case_dir": case_dir,
        "tool_dir": tool_dir,
        "attachments_dir": attachments_dir
    }


def ensure_case_tool_directories(settings, case_number):
    paths = get_case_tool_paths(settings, case_number)

    paths["root_dir"].mkdir(parents=True, exist_ok=True)
    paths["case_dir"].mkdir(parents=True, exist_ok=True)
    paths["tool_dir"].mkdir(parents=True, exist_ok=True)

    return paths
