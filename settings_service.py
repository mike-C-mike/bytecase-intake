import json
import sys
from pathlib import Path

APP_NAME = "Digital Forensics Request Builder"
APP_VERSION = "0.4.0"


def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent


BASE_DIR = get_base_dir()
SETTINGS_PATH = BASE_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "agency_name": "",
    "unit_name": "",
    "default_investigator": "",
    "investigators": [],
    "appearance": {"theme": "dark"},
    "output_paths": {
        "base_output_dir": "",
        "requests_folder_name": "output",
        "saved_requests_folder_name": "saved_requests"
    },
    "report_branding": {"patch_image_path": ""},
    "report_defaults": {"include_acknowledgement_block": True}
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
    investigators = settings.get("investigators", [])
    if not isinstance(investigators, list):
        investigators = []

    cleaned = []
    seen = set()
    for investigator in investigators:
        investigator = str(investigator).strip()
        if not investigator:
            continue
        key = investigator.lower()
        if key not in seen:
            cleaned.append(investigator)
            seen.add(key)

    default_investigator = str(settings.get("default_investigator", "")).strip()
    if default_investigator and default_investigator.lower() not in seen:
        cleaned.insert(0, default_investigator)

    settings["investigators"] = cleaned

    appearance = settings.get("appearance", {})
    if not isinstance(appearance, dict):
        appearance = {}
    theme = str(appearance.get("theme", "dark")).strip().lower()
    if theme not in {"dark", "light"}:
        theme = "dark"
    settings["appearance"] = {"theme": theme}

    report_defaults = settings.get("report_defaults", {})
    if not isinstance(report_defaults, dict):
        report_defaults = {}
    report_defaults["include_acknowledgement_block"] = bool(
        report_defaults.get("include_acknowledgement_block", True)
    )
    settings["report_defaults"] = report_defaults

    branding = settings.get("report_branding", {})
    if not isinstance(branding, dict):
        branding = {}
    branding["patch_image_path"] = str(branding.get("patch_image_path", "")).strip()
    settings["report_branding"] = branding

    return settings


def load_or_create_settings():
    if not SETTINGS_PATH.exists():
        save_settings(DEFAULT_SETTINGS.copy())
        return DEFAULT_SETTINGS.copy()

    try:
        loaded = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        return normalize_settings(deep_merge(DEFAULT_SETTINGS, loaded))
    except (json.JSONDecodeError, OSError):
        return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    settings = normalize_settings(settings)
    SETTINGS_PATH.write_text(json.dumps(settings, indent=2), encoding="utf-8")


def get_output_paths(settings):
    output = settings.get("output_paths", {})
    base_output_dir = str(output.get("base_output_dir", "")).strip()
    requests_folder_name = str(output.get("requests_folder_name", "output")).strip() or "output"
    saved_requests_folder_name = str(output.get("saved_requests_folder_name", "saved_requests")).strip() or "saved_requests"

    base_dir = Path(base_output_dir) if base_output_dir else BASE_DIR
    return {
        "base_dir": base_dir,
        "requests_dir": base_dir / requests_folder_name,
        "saved_requests_dir": base_dir / saved_requests_folder_name
    }


def ensure_directories(settings):
    paths = get_output_paths(settings)
    paths["base_dir"].mkdir(parents=True, exist_ok=True)
    paths["requests_dir"].mkdir(parents=True, exist_ok=True)
    paths["saved_requests_dir"].mkdir(parents=True, exist_ok=True)
    return paths