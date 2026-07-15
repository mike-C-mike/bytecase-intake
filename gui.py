import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from bytecase_theme import (
    THEME_DISPLAY_NAMES,
    apply_theme as apply_bytecase_theme,
    configure_toplevel,
    display_theme_preference,
    style_text_widget,
    theme_preference_from_display,
)
from request_core import build_request_packet, save_request_outputs
from settings_service import (
    APP_NAME,
    APP_SUBTITLE,
    APP_VERSION,
    DEFAULT_ROOT_FOLDER_NAME,
    PRODUCT_DOMAIN,
    PUBLISHER_NAME,
    SUITE_NAME,
    TOOL_FOLDER_NAME,
    get_case_tool_paths,
    get_default_output_root,
    load_or_create_settings,
    save_settings,
)
from validators import validate_request_for_export

LEGAL_AUTHORITY_OPTIONS = [
    "",
    "Search Warrant",
    "Consent",
    "Court Order",
    "Subpoena",
    "Exigent Circumstances",
    "Owner Permission",
    "School / Administrative Authority",
    "Other",
    "Unknown / Pending",
]

DEVICE_MEDIA_TYPES = [
    "",
    "Mobile Phone",
    "Tablet",
    "Computer / Laptop",
    "External Hard Drive / SSD",
    "External Hard Drive",
    "USB Drive",
    "SD / Memory Card",
    "DVR / NVR",
    "Cloud Return",
    "Social Media Export",
    "Email Export",
    "Photo / Video Files",
    "Other Digital Media",
]

SCOPE_OPTIONS = [
    "Device search authorized",
    "Cloud/account search authorized",
    "Messages authorized",
    "Photos/videos authorized",
    "Location data authorized",
    "Call logs authorized",
    "Contacts authorized",
    "App data authorized",
    "Deleted data recovery authorized",
]

REQUESTED_ACTIONS = [
    "Mobile device extraction",
    "Computer acquisition",
    "External media copy/hash",
    "Cloud return review",
    "Photo/video extraction",
    "Chat/message review",
    "Location data review",
    "App-specific review",
    "Keyword search",
    "File listing/index",
    "Hash manifest",
    "Preservation only",
    "Other",
]

URGENCY_FLAGS = [
    "Imminent threat",
    "Missing child",
    "Threat to school",
    "Sextortion",
    "CSAM concern",
    "Suicidal ideation",
    "Violence threat",
    "Court deadline",
    "Time-sensitive warrant return",
    "Other exigency",
]

ATTACHMENT_TYPES = [
    "",
    "Search Warrant",
    "Consent Form",
    "Court Order",
    "Subpoena",
    "Photograph",
    "Screenshot",
    "Prior Report",
    "Case Notes",
    "Cloud Return",
    "Vendor Export",
    "Scope Memo",
    "Other",
]


PHYSICAL_ITEM_TYPES = {
    "Mobile Phone",
    "Tablet",
    "Computer / Laptop",
    "External Hard Drive / SSD",
    "External Hard Drive",
    "USB Drive",
    "SD / Memory Card",
    "DVR / NVR",
    "Other Digital Media",
}

PHOTO_TYPES = [
    "",
    "Front",
    "Back",
    "Screen",
    "Top",
    "Bottom",
    "Left Side",
    "Right Side",
    "Ports / Connectors",
    "Serial / Identifier",
    "Asset Tag / Label",
    "Damage",
    "Packaging / Seal",
    "Accessories",
    "Peripherals",
    "Condition / Intake",
    "Other",
]

PERIPHERAL_TYPES = [
    "",
    "Power Adapter / Charger",
    "Cable",
    "Keyboard",
    "Mouse",
    "Monitor",
    "Docking Station",
    "External Drive",
    "USB Device",
    "SD Card",
    "SIM Card",
    "Case / Cover",
    "Bluetooth Device",
    "Speaker",
    "Headset",
    "Other",
]

TRANSFER_METHOD_OPTIONS = [
    "",
    "Hand-delivered",
    "Evidence room transfer",
    "Interoffice transfer",
    "Secure file transfer",
    "Email / digital submission",
    "Cloud / portal upload",
    "External media",
    "Other",
]

CONDITION_AT_SUBMISSION_OPTIONS = [
    "",
    "Sealed",
    "Unsealed",
    "Powered off",
    "Powered on",
    "Damaged",
    "Wet / contaminated",
    "Unknown",
    "Other",
]


def blank_attachment():
    return {
        "attachment_number": "",
        "attachment_type": "",
        "source_path": "",
        "file_name": "",
        "description": "",
        "related_item": "",
        "document_date": "",
        "provided_by": "",
        "notes": "",
    }

def blank_item():
    return {
        "item_number": "",
        "evidence_number": "",
        "device_or_media_type": "",
        "short_description": "",
        "condition_received": "",
        "packaging_seal_info": "",
        "type_specific": {},
        "item_photos": [],
        "peripherals": [],
        "item_notes": "",
    }


DEVICE_FIELD_TEMPLATES = {
    "Mobile Phone": [
        ("make_model", "Make / Model"),
        ("serial_number", "Serial Number"),
        ("imei_meid", "IMEI / MEID"),
        ("phone_number", "Phone Number"),
        ("carrier", "Carrier"),
        ("sim_present", "SIM Present"),
        ("storage_capacity", "Storage Capacity"),
        ("power_lock_state", "Power / Lock State"),
        ("passcode_provided", "Passcode Provided"),
        ("known_account_info", "Known Account Info"),
    ],
    "Tablet": [
        ("make_model", "Make / Model"),
        ("serial_number", "Serial Number"),
        ("imei_meid", "IMEI / MEID"),
        ("phone_number", "Phone Number"),
        ("carrier", "Carrier"),
        ("sim_present", "SIM Present"),
        ("storage_capacity", "Storage Capacity"),
        ("power_lock_state", "Power / Lock State"),
        ("passcode_provided", "Passcode Provided"),
        ("known_account_info", "Known Account Info"),
    ],
    "Computer / Laptop": [
        ("make_model", "Make / Model"),
        ("serial_service_tag", "Serial / Service Tag"),
        ("operating_system", "Operating System"),
        ("storage_type", "Storage Type"),
        ("storage_capacity", "Storage Capacity"),
        ("power_state", "Power State"),
        ("login_credentials_provided", "Login Credentials Provided"),
        ("known_user_account", "Known User Account"),
    ],
    "USB Drive": [
        ("brand_model", "Brand / Model"),
        ("serial_number", "Serial Number"),
        ("storage_capacity", "Storage Capacity"),
        ("connector_type", "Connector Type"),
        ("encryption_suspected", "Encryption Suspected"),
    ],
    "SD / Memory Card": [
        ("brand_model", "Brand / Model"),
        ("serial_number", "Serial Number"),
        ("storage_capacity", "Storage Capacity"),
        ("card_type", "Card Type"),
        ("adapter_included", "Adapter Included"),
    ],
    "External Hard Drive": [
        ("brand_model", "Brand / Model"),
        ("serial_number", "Serial Number"),
        ("storage_capacity", "Storage Capacity"),
        ("connection_type", "Connection Type"),
        ("encryption_suspected", "Encryption Suspected"),
        ("power_supply_included", "Power Supply Included"),
    ],
    "External Hard Drive / SSD": [
        ("brand_model", "Brand / Model"),
        ("serial_number", "Serial Number"),
        ("storage_capacity", "Storage Capacity"),
        ("connection_type", "Connection Type"),
        ("encryption_suspected", "Encryption Suspected"),
        ("power_supply_included", "Power Supply Included"),
    ],
    "DVR / NVR": [
        ("brand_model", "Brand / Model"),
        ("serial_number", "Serial Number"),
        ("storage_capacity", "Storage Capacity"),
        ("channel_count", "Channel Count"),
        ("date_time_setting", "Date / Time Setting"),
        ("export_format", "Export Format"),
        ("login_credentials_provided", "Login Credentials Provided"),
        ("network_info", "Network Info"),
        ("power_supply_included", "Power Supply Included"),
    ],
    "Cloud Return": [
        ("platform_provider", "Platform / Provider"),
        ("account_identifier", "Account Identifier"),
        ("return_export_date", "Return / Export Date"),
        ("export_format", "Export Format"),
        ("source_authority", "Source Authority"),
        ("file_folder_location", "File / Folder Location"),
    ],
    "Social Media Export": [
        ("platform_provider", "Platform / Provider"),
        ("account_identifier", "Account Identifier"),
        ("export_date", "Export Date"),
        ("export_format", "Export Format"),
        ("date_range", "Date Range"),
        ("producing_party", "Producing Party"),
    ],
    "Email Export": [
        ("platform_provider", "Platform / Provider"),
        ("account_identifier", "Account Identifier"),
        ("export_date", "Export Date"),
        ("export_format", "Export Format"),
        ("date_range", "Date Range"),
        ("producing_party", "Producing Party"),
    ],
    "Photo / Video Files": [
        ("media_type", "Media Type"),
        ("source_device_platform", "Source Device / Platform"),
        ("file_folder_path", "File / Folder Path"),
        ("date_range", "Date Range"),
        ("provided_by", "Provided By"),
        ("original_source_known", "Original Source Known"),
    ],
    "Other Digital Media": [
        ("identifier", "Identifier"),
        ("description", "Description"),
        ("capacity_size", "Capacity / Size"),
        ("source_origin", "Source / Origin"),
        ("additional_details", "Additional Details"),
    ],
}


def normalize_item_for_gui(item):
    normalized = blank_item()
    normalized.update({
        "item_number": item.get("item_number", ""),
        "evidence_number": item.get("evidence_number", ""),
        "device_or_media_type": item.get("device_or_media_type", ""),
        "short_description": item.get("short_description", ""),
        "condition_received": item.get("condition_received", ""),
        "packaging_seal_info": item.get("packaging_seal_info", ""),
        "item_notes": item.get("item_notes", ""),
    })

    type_specific = item.get("type_specific", {})
    if not isinstance(type_specific, dict):
        type_specific = {}

    normalized["type_specific"] = {key: str(value or "") for key, value in type_specific.items()}

    item_photos = item.get("item_photos", [])
    normalized["item_photos"] = item_photos if isinstance(item_photos, list) else []

    peripherals = item.get("peripherals", [])
    normalized["peripherals"] = peripherals if isinstance(peripherals, list) else []

    legacy_fields = [
        "make_model", "serial_number", "imei_meid", "phone_number", "storage_capacity",
        "power_lock_state", "passcode_provided", "known_account_info",
    ]

    for key in legacy_fields:
        value = item.get(key, "")
        if value and key not in normalized["type_specific"]:
            normalized["type_specific"][key] = value

    return normalized


def summarize_item_details(item):
    item = normalize_item_for_gui(item)
    type_specific = item.get("type_specific", {})
    priority_keys = [
        "make_model", "brand_model", "platform_provider", "media_type", "serial_number",
        "serial_service_tag", "storage_capacity", "phone_number", "account_identifier",
        "file_folder_path", "file_folder_location",
    ]
    values = []
    for key in priority_keys:
        value = str(type_specific.get(key, "")).strip()
        if value:
            values.append(value)
        if len(values) >= 3:
            break
    return " | ".join(values)


class DigitalForensicsRequestApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} - {APP_SUBTITLE} v{APP_VERSION}")
        self.root.geometry("1260x850")

        self.settings = load_or_create_settings()
        self.action_vars = {}
        self.urgency_vars = {}
        self.scope_vars = {}
        self.evidence_items = []
        self.attachments = []

        self.apply_theme()
        self.build_gui()
        self.load_defaults_from_settings()

    def apply_theme(self):
        self.theme_state = apply_bytecase_theme(self.root, self.settings)
        self.colors = self.theme_state["colors"]

    def style_text(self, widget):
        style_text_widget(widget, self.colors)

    def configure_child_window(self, window):
        configure_toplevel(window, self.colors)

    def build_gui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        top = ttk.Frame(self.root, padding=10)
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(0, weight=1)

        ttk.Label(top, text=f"{APP_NAME} v{APP_VERSION}", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            top,
            text=f"{APP_SUBTITLE} | Part of {SUITE_NAME} by {PUBLISHER_NAME}",
            style="Muted.TLabel",
        ).grid(row=1, column=0, sticky="w")

        ttk.Button(top, text="Settings", command=self.open_settings).grid(row=0, column=1, padx=4)
        ttk.Button(top, text="About", command=self.open_about).grid(row=0, column=2, padx=4)
        ttk.Button(top, text="Open Output Folder", command=self.open_output_folder).grid(row=0, column=3, padx=4)

        main = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        main.grid(row=1, column=0, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.rowconfigure(0, weight=1)

        notebook = ttk.Notebook(main)
        notebook.grid(row=0, column=0, sticky="nsew")

        self.build_case_tab(notebook)
        self.build_items_tab(notebook)
        self.build_attachments_tab(notebook)
        self.build_request_tab(notebook)
        self.build_priority_tab(notebook)

        bottom = ttk.Frame(main, padding=(0, 10, 0, 0))
        bottom.grid(row=1, column=0, sticky="ew")
        bottom.columnconfigure(0, weight=1)

        self.status_var = tk.StringVar(value="Ready.")
        ttk.Label(bottom, textvariable=self.status_var, style="Muted.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Button(bottom, text="Review Request", command=self.review_request, style="Primary.TButton").grid(row=0, column=1, padx=4)
        ttk.Button(bottom, text="Clear Form", command=self.clear_form).grid(row=0, column=2, padx=4)

    def entry(self, parent, label, variable, row, column=0):
        ttk.Label(parent, text=label).grid(row=row, column=column, sticky="w", pady=5)
        ttk.Entry(parent, textvariable=variable).grid(row=row, column=column + 1, sticky="ew", pady=5)

    def build_case_tab(self, notebook):
        frame = ttk.Frame(notebook, padding=10)
        notebook.add(frame, text="Case / Investigator")
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(3, weight=1)

        self.case_number_var = tk.StringVar()
        self.agency_case_number_var = tk.StringVar()
        self.offense_type_var = tk.StringVar()
        self.submitting_agency_var = tk.StringVar()
        self.submitting_unit_var = tk.StringVar()
        self.submitting_investigator_var = tk.StringVar()
        self.investigator_phone_var = tk.StringVar()
        self.investigator_email_var = tk.StringVar()
        self.supervisor_var = tk.StringVar()

        case_frame = ttk.LabelFrame(frame, text="Case Information", padding=10)
        case_frame.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 10))
        case_frame.columnconfigure(1, weight=1)
        case_frame.columnconfigure(3, weight=1)

        self.entry(case_frame, "Case Number", self.case_number_var, 0, 0)
        self.entry(case_frame, "Agency Case Number", self.agency_case_number_var, 0, 2)
        self.entry(case_frame, "Offense / Incident Type", self.offense_type_var, 1, 0)

        investigator_frame = ttk.LabelFrame(frame, text="Submitting Investigator", padding=10)
        investigator_frame.grid(row=1, column=0, columnspan=4, sticky="ew")
        investigator_frame.columnconfigure(1, weight=1)
        investigator_frame.columnconfigure(3, weight=1)

        self.entry(investigator_frame, "Submitting Agency", self.submitting_agency_var, 0, 0)
        self.entry(investigator_frame, "Submitting Unit", self.submitting_unit_var, 0, 2)

        ttk.Label(investigator_frame, text="Submitting Investigator").grid(row=1, column=0, sticky="w", pady=5)
        self.investigator_combo = ttk.Combobox(
            investigator_frame,
            textvariable=self.submitting_investigator_var,
            state="normal",
        )
        self.investigator_combo.grid(row=1, column=1, sticky="ew", pady=5)

        self.entry(investigator_frame, "Investigator Phone", self.investigator_phone_var, 1, 2)
        self.entry(investigator_frame, "Investigator Email", self.investigator_email_var, 2, 0)
        self.entry(investigator_frame, "Supervisor", self.supervisor_var, 2, 2)

    def build_items_tab(self, notebook):
        frame = ttk.Frame(notebook, padding=10)
        notebook.add(frame, text="Evidence Items")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        table_frame = ttk.LabelFrame(frame, text="Evidence / Device Items", padding=10)
        table_frame.grid(row=0, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("item_number", "evidence_number", "type", "description", "details", "photos", "peripherals", "condition")
        self.items_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=14)
        headings = {
            "item_number": "Item #",
            "evidence_number": "Evidence #",
            "type": "Type",
            "description": "Short Description",
            "details": "Key Details",
            "photos": "Photos",
            "peripherals": "Peripherals",
            "condition": "Condition",
        }
        widths = {
            "item_number": 90,
            "evidence_number": 130,
            "type": 170,
            "description": 260,
            "details": 260,
            "photos": 80,
            "peripherals": 90,
            "condition": 160,
        }
        for column in columns:
            self.items_tree.heading(column, text=headings[column])
            self.items_tree.column(column, width=widths[column], anchor="w")

        self.items_tree.grid(row=0, column=0, sticky="nsew")
        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.items_tree.yview)
        y_scroll.grid(row=0, column=1, sticky="ns")
        self.items_tree.configure(yscrollcommand=y_scroll.set)
        self.items_tree.bind("<Double-1>", lambda event: self.edit_selected_item())

        button_frame = ttk.Frame(frame, padding=(0, 10, 0, 0))
        button_frame.grid(row=1, column=0, sticky="ew")
        button_frame.columnconfigure(0, weight=1)

        self.item_count_var = tk.StringVar(value="Evidence items: 0")
        ttk.Label(button_frame, textvariable=self.item_count_var, style="Muted.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Button(button_frame, text="Add Item", command=self.add_item).grid(row=0, column=1, padx=4)
        ttk.Button(button_frame, text="Edit Selected", command=self.edit_selected_item).grid(row=0, column=2, padx=4)
        ttk.Button(button_frame, text="Remove Selected", command=self.remove_selected_item).grid(row=0, column=3, padx=4)

        helper = (
            "Add one or more submitted devices, media, or digital returns. "
            "Keep this practical; more detailed examiner work belongs in the acquisition packet."
        )
        ttk.Label(frame, text=helper, style="Muted.TLabel", wraplength=1100).grid(row=2, column=0, sticky="w", pady=(10, 0))

    def build_attachments_tab(self, notebook):
        frame = ttk.Frame(notebook, padding=10)
        notebook.add(frame, text="Attachments")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        table_frame = ttk.LabelFrame(frame, text="Supporting Documents / Attachment Index", padding=10)
        table_frame.grid(row=0, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("number", "type", "file_name", "related_item", "description", "source_path")
        self.attachments_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=14)

        headings = {
            "number": "Attachment #",
            "type": "Type",
            "file_name": "File Name",
            "related_item": "Related Item",
            "description": "Description",
            "source_path": "Source Path",
        }

        widths = {
            "number": 110,
            "type": 160,
            "file_name": 220,
            "related_item": 140,
            "description": 300,
            "source_path": 420,
        }

        for column in columns:
            self.attachments_tree.heading(column, text=headings[column])
            self.attachments_tree.column(column, width=widths[column], anchor="w")

        self.attachments_tree.grid(row=0, column=0, sticky="nsew")

        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.attachments_tree.yview)
        y_scroll.grid(row=0, column=1, sticky="ns")
        self.attachments_tree.configure(yscrollcommand=y_scroll.set)
        self.attachments_tree.bind("<Double-1>", lambda event: self.edit_selected_attachment())

        button_frame = ttk.Frame(frame, padding=(0, 10, 0, 0))
        button_frame.grid(row=1, column=0, sticky="ew")
        button_frame.columnconfigure(0, weight=1)

        self.attachment_count_var = tk.StringVar(value="Attachments: 0")
        ttk.Label(button_frame, textvariable=self.attachment_count_var, style="Muted.TLabel").grid(row=0, column=0, sticky="w")

        ttk.Button(button_frame, text="Add Attachment", command=self.add_attachment).grid(row=0, column=1, padx=4)
        ttk.Button(button_frame, text="Edit Selected", command=self.edit_selected_attachment).grid(row=0, column=2, padx=4)
        ttk.Button(button_frame, text="Remove Selected", command=self.remove_selected_attachment).grid(row=0, column=3, padx=4)

        helper = (
            "Add supporting documents such as warrants, consent forms, scope memos, screenshots, "
            "prior reports, or notes. On export, listed files are copied into the request packet's "
            "attachments folder when possible."
        )
        ttk.Label(frame, text=helper, style="Muted.TLabel", wraplength=1100).grid(row=2, column=0, sticky="w", pady=(10, 0))

    def build_request_tab(self, notebook):
        frame = ttk.Frame(notebook, padding=10)
        notebook.add(frame, text="Request / Scope")
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(2, weight=1)

        authority_frame = ttk.LabelFrame(frame, text="Legal Authority", padding=10)
        authority_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        authority_frame.columnconfigure(1, weight=1)

        self.authority_type_var = tk.StringVar()
        self.authority_date_var = tk.StringVar()
        self.authority_reference_var = tk.StringVar()

        ttk.Label(authority_frame, text="Authority Type").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Combobox(
            authority_frame,
            textvariable=self.authority_type_var,
            values=LEGAL_AUTHORITY_OPTIONS,
            state="readonly",
        ).grid(row=0, column=1, sticky="ew", pady=5)
        self.entry(authority_frame, "Authority Date", self.authority_date_var, 1, 0)
        self.entry(authority_frame, "Authority Reference / Document #", self.authority_reference_var, 2, 0)

        ttk.Label(authority_frame, text="Authority Notes").grid(row=3, column=0, sticky="nw", pady=5)
        self.authority_notes_text = tk.Text(authority_frame, height=5, width=55)
        self.authority_notes_text.grid(row=3, column=1, sticky="nsew", pady=5)
        self.style_text(self.authority_notes_text)

        actions_frame = ttk.LabelFrame(frame, text="Requested Forensic Actions", padding=10)
        actions_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        for index, action in enumerate(REQUESTED_ACTIONS):
            self.action_vars[action] = tk.BooleanVar(value=False)
            ttk.Checkbutton(actions_frame, text=action, variable=self.action_vars[action]).grid(
                row=index,
                column=0,
                sticky="w",
            )

        scope_frame = ttk.LabelFrame(frame, text="Legal Authority / Scope Builder", padding=10)
        scope_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        scope_frame.columnconfigure(0, weight=1)
        scope_frame.columnconfigure(1, weight=1)

        left_scope = ttk.Frame(scope_frame)
        left_scope.grid(row=0, column=0, sticky="nw")
        right_scope = ttk.Frame(scope_frame)
        right_scope.grid(row=0, column=1, sticky="new", padx=(16, 0))
        right_scope.columnconfigure(1, weight=1)

        for index, option in enumerate(SCOPE_OPTIONS):
            self.scope_vars[option] = tk.BooleanVar(value=False)
            ttk.Checkbutton(left_scope, text=option, variable=self.scope_vars[option]).grid(row=index, column=0, sticky="w")

        self.date_range_limited_var = tk.BooleanVar(value=False)
        self.specific_apps_limited_var = tk.BooleanVar(value=False)
        self.specific_accounts_limited_var = tk.BooleanVar(value=False)
        self.keyword_limited_var = tk.BooleanVar(value=False)

        self.authorized_date_range_var = tk.StringVar()
        self.authorized_apps_platforms_var = tk.StringVar()
        self.authorized_accounts_var = tk.StringVar()
        self.authorized_keywords_var = tk.StringVar()

        ttk.Checkbutton(right_scope, text="Date range limitation applies", variable=self.date_range_limited_var).grid(row=0, column=0, sticky="w", pady=3)
        ttk.Entry(right_scope, textvariable=self.authorized_date_range_var).grid(row=0, column=1, sticky="ew", pady=3)

        ttk.Checkbutton(right_scope, text="Specific app/platform limitation applies", variable=self.specific_apps_limited_var).grid(row=1, column=0, sticky="w", pady=3)
        ttk.Entry(right_scope, textvariable=self.authorized_apps_platforms_var).grid(row=1, column=1, sticky="ew", pady=3)

        ttk.Checkbutton(right_scope, text="Specific account limitation applies", variable=self.specific_accounts_limited_var).grid(row=2, column=0, sticky="w", pady=3)
        ttk.Entry(right_scope, textvariable=self.authorized_accounts_var).grid(row=2, column=1, sticky="ew", pady=3)

        ttk.Checkbutton(right_scope, text="Keyword limitation applies", variable=self.keyword_limited_var).grid(row=3, column=0, sticky="w", pady=3)
        ttk.Entry(right_scope, textvariable=self.authorized_keywords_var).grid(row=3, column=1, sticky="ew", pady=3)

        scope_helper = (
            "These fields guide scope documentation. They do not provide legal advice or decide whether a search is authorized."
        )
        ttk.Label(scope_frame, text=scope_helper, style="Muted.TLabel", wraplength=1050).grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))

        self.investigative_objective_text = self.bigbox(
            frame,
            "Investigative Objective / Requested Information",
            2,
            0,
            2,
            7,
            "Describe what you are trying to locate, prove, disprove, preserve, or clarify. Avoid broad requests unless the authority and case facts support them.",
        )
        self.known_facts_text = self.bigbox(frame, "Known Facts / Context for Examiner", 3, 0, 2, 5, "")
        self.scope_notes_text = self.bigbox(frame, "Additional Scope Notes", 4, 0, 2, 4, "")

    def bigbox(self, parent, title, row, column, columnspan, height, helper):
        frame = ttk.LabelFrame(parent, text=title, padding=10)
        frame.grid(row=row, column=column, columnspan=columnspan, sticky="nsew", pady=5)
        frame.columnconfigure(0, weight=1)
        if helper:
            ttk.Label(frame, text=helper, style="Muted.TLabel", wraplength=1050).grid(row=0, column=0, sticky="w")
        text = tk.Text(frame, height=height, width=110)
        text.grid(row=1, column=0, sticky="nsew", pady=(6, 0))
        self.style_text(text)
        return text

    def build_priority_tab(self, notebook):
        frame = ttk.Frame(notebook, padding=10)
        notebook.add(frame, text="Priority / Handoff")
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(0, weight=1)

        priority_frame = ttk.LabelFrame(frame, text="Priority / Urgency", padding=10)
        priority_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        priority_frame.columnconfigure(1, weight=1)

        self.priority_var = tk.StringVar()
        self.requested_due_date_var = tk.StringVar()

        ttk.Label(priority_frame, text="Priority").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Combobox(
            priority_frame,
            textvariable=self.priority_var,
            values=["", "Routine", "Priority", "Urgent", "Emergency"],
            state="readonly",
        ).grid(row=0, column=1, sticky="ew", pady=5)
        self.entry(priority_frame, "Requested Due Date", self.requested_due_date_var, 1, 0)

        for index, flag in enumerate(URGENCY_FLAGS, start=2):
            self.urgency_vars[flag] = tk.BooleanVar(value=False)
            ttk.Checkbutton(priority_frame, text=flag, variable=self.urgency_vars[flag]).grid(
                row=index,
                column=0,
                columnspan=2,
                sticky="w",
            )

        ttk.Label(priority_frame, text="Priority Notes").grid(row=20, column=0, sticky="nw", pady=5)
        self.priority_notes_text = tk.Text(priority_frame, height=5, width=50)
        self.priority_notes_text.grid(row=20, column=1, sticky="nsew", pady=5)
        self.style_text(self.priority_notes_text)

        handoff_frame = ttk.LabelFrame(frame, text="Submission / Handoff Receipt", padding=10)
        handoff_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        handoff_frame.columnconfigure(1, weight=1)
        handoff_frame.columnconfigure(3, weight=1)

        self.submitted_by_var = tk.StringVar()
        self.submitted_by_title_unit_var = tk.StringVar()
        self.submitted_date_time_var = tk.StringVar()
        self.submitted_to_var = tk.StringVar()
        self.receiving_unit_lab_var = tk.StringVar()
        self.transfer_method_var = tk.StringVar()
        self.packaging_seal_info_var = tk.StringVar()
        self.condition_at_submission_var = tk.StringVar()
        self.received_by_var = tk.StringVar()
        self.received_date_time_var = tk.StringVar()
        self.include_acknowledgement_block_var = tk.BooleanVar(value=True)

        self.entry(handoff_frame, "Submitted By", self.submitted_by_var, 0, 0)
        self.entry(handoff_frame, "Title / Unit", self.submitted_by_title_unit_var, 0, 2)
        self.entry(handoff_frame, "Submitted Date / Time", self.submitted_date_time_var, 1, 0)
        self.entry(handoff_frame, "Submitted To", self.submitted_to_var, 1, 2)
        self.entry(handoff_frame, "Receiving Unit / Lab", self.receiving_unit_lab_var, 2, 0)

        ttk.Label(handoff_frame, text="Transfer Method").grid(row=2, column=2, sticky="w", pady=5)
        ttk.Combobox(
            handoff_frame,
            textvariable=self.transfer_method_var,
            values=TRANSFER_METHOD_OPTIONS,
            state="readonly",
        ).grid(row=2, column=3, sticky="ew", pady=5)

        self.entry(handoff_frame, "Packaging / Seal Information", self.packaging_seal_info_var, 3, 0)

        ttk.Label(handoff_frame, text="Condition at Submission").grid(row=3, column=2, sticky="w", pady=5)
        ttk.Combobox(
            handoff_frame,
            textvariable=self.condition_at_submission_var,
            values=CONDITION_AT_SUBMISSION_OPTIONS,
            state="readonly",
        ).grid(row=3, column=3, sticky="ew", pady=5)

        self.entry(handoff_frame, "Received By", self.received_by_var, 4, 0)
        self.entry(handoff_frame, "Received Date / Time", self.received_date_time_var, 4, 2)

        ttk.Checkbutton(
            handoff_frame,
            text="Include submission acknowledgement block",
            variable=self.include_acknowledgement_block_var,
        ).grid(row=5, column=0, columnspan=4, sticky="w", pady=8)

        ttk.Label(handoff_frame, text="Receiving / Handoff Notes").grid(row=6, column=0, sticky="nw", pady=5)
        self.handoff_notes_text = tk.Text(handoff_frame, height=8, width=60)
        self.handoff_notes_text.grid(row=6, column=1, columnspan=3, sticky="nsew", pady=5)
        self.style_text(self.handoff_notes_text)

        helper = (
            "This section documents intake/submission details only. It does not replace the agency's official "
            "evidence management system, chain-of-custody record, property record, legal review, or forensic report."
        )
        ttk.Label(handoff_frame, text=helper, style="Muted.TLabel", wraplength=680).grid(
            row=7,
            column=0,
            columnspan=4,
            sticky="w",
            pady=(8, 0),
        )

    def add_item(self):
        ItemWindow(self, title="Add Evidence Item")

    def edit_selected_item(self):
        selected = self.items_tree.selection()
        if not selected:
            messagebox.showinfo("Edit Item", "Select an item to edit.")
            return
        index = int(selected[0])
        ItemWindow(self, title="Edit Evidence Item", item=self.evidence_items[index].copy(), index=index)

    def remove_selected_item(self):
        selected = self.items_tree.selection()
        if not selected:
            messagebox.showinfo("Remove Item", "Select an item to remove.")
            return
        index = int(selected[0])
        confirm = messagebox.askyesno("Remove Item", "Remove the selected evidence item?")
        if not confirm:
            return
        self.evidence_items.pop(index)
        self.refresh_items_table()

    def save_item(self, item, index=None):
        if index is None:
            if not item.get("item_number", "").strip():
                item["item_number"] = str(len(self.evidence_items) + 1).zfill(3)
            self.evidence_items.append(item)
        else:
            self.evidence_items[index] = item
        self.refresh_items_table()
        self.status_var.set(f"Evidence items: {len(self.evidence_items)}")

    def refresh_items_table(self):
        for row in self.items_tree.get_children():
            self.items_tree.delete(row)

        for index, item in enumerate(self.evidence_items):
            item = normalize_item_for_gui(item)
            self.items_tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    item.get("item_number", ""),
                    item.get("evidence_number", ""),
                    item.get("device_or_media_type", ""),
                    item.get("short_description", ""),
                    summarize_item_details(item),
                    len(item.get("item_photos", [])),
                    len(item.get("peripherals", [])),
                    item.get("condition_received", ""),
                ),
            )

        self.item_count_var.set(f"Evidence items: {len(self.evidence_items)}")

    def add_attachment(self):
        AttachmentWindow(self, title="Add Attachment")

    def edit_selected_attachment(self):
        selected = self.attachments_tree.selection()
        if not selected:
            messagebox.showinfo("Edit Attachment", "Select an attachment to edit.")
            return

        index = int(selected[0])
        AttachmentWindow(
            self,
            title="Edit Attachment",
            attachment=self.attachments[index].copy(),
            index=index,
        )

    def remove_selected_attachment(self):
        selected = self.attachments_tree.selection()
        if not selected:
            messagebox.showinfo("Remove Attachment", "Select an attachment to remove.")
            return

        index = int(selected[0])
        confirm = messagebox.askyesno("Remove Attachment", "Remove the selected attachment?")
        if not confirm:
            return

        self.attachments.pop(index)
        self.refresh_attachments_table()

    def save_attachment(self, attachment, index=None):
        if index is None:
            if not attachment.get("attachment_number", "").strip():
                attachment["attachment_number"] = str(len(self.attachments) + 1).zfill(3)

            if not attachment.get("file_name", "").strip() and attachment.get("source_path", "").strip():
                attachment["file_name"] = os.path.basename(attachment["source_path"].strip())

            self.attachments.append(attachment)
        else:
            if not attachment.get("file_name", "").strip() and attachment.get("source_path", "").strip():
                attachment["file_name"] = os.path.basename(attachment["source_path"].strip())

            self.attachments[index] = attachment

        self.refresh_attachments_table()
        self.status_var.set(f"Attachments: {len(self.attachments)}")

    def refresh_attachments_table(self):
        for row in self.attachments_tree.get_children():
            self.attachments_tree.delete(row)

        for index, attachment in enumerate(self.attachments):
            self.attachments_tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    attachment.get("attachment_number", ""),
                    attachment.get("attachment_type", ""),
                    attachment.get("file_name", ""),
                    attachment.get("related_item", ""),
                    attachment.get("description", ""),
                    attachment.get("source_path", ""),
                ),
            )

        self.attachment_count_var.set(f"Attachments: {len(self.attachments)}")

    def get_actions(self):
        return [action for action, variable in self.action_vars.items() if variable.get()]

    def get_flags(self):
        return [flag for flag, variable in self.urgency_vars.items() if variable.get()]

    def get_scope_options(self):
        return [option for option, variable in self.scope_vars.items() if variable.get()]

    def load_defaults_from_settings(self):
        self.submitting_agency_var.set(self.settings.get("agency_name", ""))
        self.submitting_unit_var.set(self.settings.get("unit_name", ""))
        self.submitting_investigator_var.set(self.settings.get("default_investigator", ""))
        self.investigator_combo["values"] = self.settings.get("investigators", [])
        self.include_acknowledgement_block_var.set(
            bool(self.settings.get("report_defaults", {}).get("include_acknowledgement_block", True))
        )

    def build_packet(self):
        return build_request_packet(
            self.settings,
            {
                "case_number": self.case_number_var.get(),
                "agency_case_number": self.agency_case_number_var.get(),
                "offense_type": self.offense_type_var.get(),
            },
            {
                "submitting_agency": self.submitting_agency_var.get(),
                "submitting_unit": self.submitting_unit_var.get(),
                "submitting_investigator": self.submitting_investigator_var.get(),
                "investigator_phone": self.investigator_phone_var.get(),
                "investigator_email": self.investigator_email_var.get(),
                "supervisor": self.supervisor_var.get(),
            },
            {
                "authority_type": self.authority_type_var.get(),
                "authority_date": self.authority_date_var.get(),
                "authority_reference": self.authority_reference_var.get(),
                "authority_notes": self.authority_notes_text.get("1.0", "end").strip(),
            },
            {
                "scope_options": self.get_scope_options(),
                "date_range_limited": self.date_range_limited_var.get(),
                "specific_apps_limited": self.specific_apps_limited_var.get(),
                "specific_accounts_limited": self.specific_accounts_limited_var.get(),
                "keyword_limited": self.keyword_limited_var.get(),
                "authorized_date_range": self.authorized_date_range_var.get(),
                "authorized_apps_platforms": self.authorized_apps_platforms_var.get(),
                "authorized_accounts": self.authorized_accounts_var.get(),
                "authorized_keywords": self.authorized_keywords_var.get(),
                "scope_notes": self.scope_notes_text.get("1.0", "end").strip(),
            },
            self.evidence_items,
            self.attachments,
            {
                "requested_actions": self.get_actions(),
                "investigative_objective": self.investigative_objective_text.get("1.0", "end").strip(),
                "known_facts_for_examiner": self.known_facts_text.get("1.0", "end").strip(),
            },
            {
                "priority": self.priority_var.get(),
                "requested_due_date": self.requested_due_date_var.get(),
                "urgency_flags": self.get_flags(),
                "priority_notes": self.priority_notes_text.get("1.0", "end").strip(),
            },
            {
                "submitted_by": self.submitted_by_var.get(),
                "submitted_by_title_unit": self.submitted_by_title_unit_var.get(),
                "submitted_date_time": self.submitted_date_time_var.get(),
                "submitted_to": self.submitted_to_var.get(),
                "receiving_unit_lab": self.receiving_unit_lab_var.get(),
                "transfer_method": self.transfer_method_var.get(),
                "packaging_seal_info": self.packaging_seal_info_var.get(),
                "condition_at_submission": self.condition_at_submission_var.get(),
                "received_by": self.received_by_var.get(),
                "received_date_time": self.received_date_time_var.get(),
                "receiving_notes": self.handoff_notes_text.get("1.0", "end").strip(),
            },
            self.include_acknowledgement_block_var.get(),
        )

    def review_request(self):
        packet = self.build_packet()
        errors, warnings = validate_request_for_export(packet)
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return
        ReviewWindow(self, packet, warnings)

    def review_text(self, packet, warnings):
        case = packet.get("case_info", {})
        investigator = packet.get("investigator_info", {})
        authority = packet.get("legal_authority", {})
        scope = packet.get("scope", {})
        details = packet.get("request_details", {})
        priority = packet.get("priority_info", {})
        options = packet.get("report_options", {})
        handoff = packet.get("handoff_info", {})

        photo_count = sum(len(item.get("item_photos", []) or []) for item in packet.get("evidence_items", []))
        peripheral_count = sum(len(item.get("peripherals", []) or []) for item in packet.get("evidence_items", []))

        lines = [
            "BYTECASE INTAKE REQUEST REVIEW",
            "=" * 80,
            "",
            f"Case Number: {case.get('case_number', '')}",
            f"Agency Case Number: {case.get('agency_case_number', '')}",
            f"Submitting Investigator: {investigator.get('submitting_investigator', '')}",
            f"Legal Authority: {authority.get('authority_type', '')}",
            f"Evidence Items: {len(packet.get('evidence_items', []))}",
            f"Attachments: {len(packet.get('attachments', []))}",
            f"Item Photos: {photo_count}",
            f"Peripherals / Accessories: {peripheral_count}",
            f"Transfer Method: {handoff.get('transfer_method', '')}",
            f"Condition at Submission: {handoff.get('condition_at_submission', '')}",
            f"Requested Actions: {', '.join(details.get('requested_actions', [])) or 'None selected'}",
            f"Scope Options: {', '.join(scope.get('scope_options', [])) or 'None selected'}",
            f"Priority: {priority.get('priority', '')}",
            f"Acknowledgement Block Included: {'Yes' if options.get('include_acknowledgement_block') else 'No'}",
            "",
        ]

        if warnings:
            lines.extend(["WARNINGS", "-" * 80])
            lines.extend([f"- {warning}" for warning in warnings])
            lines.append("")

        lines.extend([
            "This review has not written output files yet.",
            "Click Confirm Export to create a request folder with TXT, DOCX, JSON, copied attachments, and item photo folders.",
        ])
        return "\n".join(lines)

    def export_request(self, packet, window):
        try:
            export_result = save_request_outputs(packet, self.settings)

            if len(export_result) == 6:
                txt_path, docx_path, json_path, request_folder, copied_count, copied_photo_count = export_result
            elif len(export_result) == 5:
                txt_path, docx_path, json_path, request_folder, copied_count = export_result
                copied_photo_count = 0
            else:
                raise ValueError(f"Unexpected export result format: {len(export_result)} values returned.")

            window.destroy()
            self.status_var.set("Request exported successfully.")
            messagebox.showinfo(
                "Request Exported",
                "ByteCase Intake request packet exported successfully.\n\n"
                f"Request Folder:\n{request_folder}\n\n"
                f"TXT:\n{txt_path}\n\n"
                f"DOCX:\n{docx_path}\n\n"
                f"JSON:\n{json_path}\n\n"
                f"Attachments copied: {copied_count}\n"
                f"Item photos copied: {copied_photo_count}",
            )
        except Exception as exc:
            messagebox.showerror("Export Error", f"The request could not be exported.\n\nDetails:\n{exc}")

    def clear_form(self):
        confirm = messagebox.askyesno("Clear Form", "Clear all request fields and reset defaults?")
        if not confirm:
            return

        string_vars = [
            self.case_number_var,
            self.agency_case_number_var,
            self.offense_type_var,
            self.investigator_phone_var,
            self.investigator_email_var,
            self.supervisor_var,
            self.authority_type_var,
            self.authority_date_var,
            self.authority_reference_var,
            self.authorized_date_range_var,
            self.authorized_apps_platforms_var,
            self.authorized_accounts_var,
            self.authorized_keywords_var,
            self.priority_var,
            self.requested_due_date_var,
            self.submitted_by_var,
            self.submitted_by_title_unit_var,
            self.submitted_date_time_var,
            self.submitted_to_var,
            self.receiving_unit_lab_var,
            self.transfer_method_var,
            self.packaging_seal_info_var,
            self.condition_at_submission_var,
            self.received_by_var,
            self.received_date_time_var,
        ]
        for variable in string_vars:
            variable.set("")

        for text_box in [
            self.authority_notes_text,
            self.investigative_objective_text,
            self.known_facts_text,
            self.scope_notes_text,
            self.priority_notes_text,
            self.handoff_notes_text,
        ]:
            text_box.delete("1.0", "end")

        for variable in self.action_vars.values():
            variable.set(False)
        for variable in self.urgency_vars.values():
            variable.set(False)
        for variable in self.scope_vars.values():
            variable.set(False)

        self.date_range_limited_var.set(False)
        self.specific_apps_limited_var.set(False)
        self.specific_accounts_limited_var.set(False)
        self.keyword_limited_var.set(False)

        self.evidence_items = []
        self.attachments = []
        self.refresh_items_table()
        self.refresh_attachments_table()
        self.load_defaults_from_settings()
        self.status_var.set("Form cleared.")

    def open_output_folder(self):
        case_number = self.case_number_var.get().strip() if hasattr(self, "case_number_var") else ""

        try:
            if case_number:
                path = get_case_tool_paths(self.settings, case_number)["tool_dir"]
            else:
                path = get_default_output_root()

            path.mkdir(parents=True, exist_ok=True)
            os.startfile(path)
        except OSError as exc:
            messagebox.showerror("Open Output Folder Error", str(exc))

    def open_about(self):
        AboutWindow(self)

    def open_settings(self):
        SettingsWindow(self)

    def refresh_settings(self):
        self.settings = load_or_create_settings()
        self.apply_theme()
        self.load_defaults_from_settings()
        for widget in [
            self.authority_notes_text,
            self.investigative_objective_text,
            self.known_facts_text,
            self.scope_notes_text,
            self.priority_notes_text,
            self.handoff_notes_text,
        ]:
            self.style_text(widget)

class AboutWindow:
    def __init__(self, app):
        self.app = app

        self.window = tk.Toplevel(app.root)
        self.window.title(f"About {APP_NAME}")
        self.window.geometry("840x660")
        self.window.transient(app.root)
        self.window.grab_set()
        self.window.configure(bg=app.colors["app_background"])

        self.build()

    def build(self):
        frame = ttk.Frame(self.window, padding=14)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        ttk.Label(frame, text=f"{APP_NAME} v{APP_VERSION}", style="Title.TLabel").grid(row=0, column=0, sticky="w")

        about_text = tk.Text(frame, wrap="word", height=28)
        about_text.grid(row=1, column=0, sticky="nsew", pady=(10, 10))
        self.app.style_text(about_text)

        content = f"""BYTECASE INTAKE

{APP_SUBTITLE}

Part of the {SUITE_NAME} toolset by {PUBLISHER_NAME}
Product domain: {PRODUCT_DOMAIN}

PURPOSE

ByteCase Intake helps investigators create clear, scoped, well-documented digital forensic request packets before forensic work begins.

The tool is designed to help capture:
- Case and investigator information
- Evidence or device items being submitted
- Legal authority and scope information
- Requested forensic actions
- Investigative objective and known facts
- Supporting documents and attachment indexes
- Submission and handoff information
- Physical item intake photos and peripherals/accessories

PLATFORM IDEOLOGY

ByteCase tools are built around a simple principle:

Bake in best practices, structure, and guidance while preserving enough flexibility for agencies to customize their workflow.

Small and medium agencies do not always have rigid digital forensics workflows, dedicated lab-management systems, or standardized request processes. ByteCase is designed to support practical documentation without forcing every agency into one model.

The tool should guide better submissions, reduce repeat typing, and create clearer handoffs between investigators and examiners.

WHAT THIS TOOL DOES NOT DO

ByteCase Intake does not perform forensic acquisition, extraction, hashing, parsing, artifact analysis, legal review, or investigative conclusions.

It creates a request packet based on information provided by the investigator or submitting party. Item photos are intake reference images only and do not replace official evidence photographs, chain-of-custody documentation, or examiner documentation.

Legal authority, scope, and agency policy should be reviewed under the user's agency procedures and applicable law before forensic work begins.

OUTPUT PHILOSOPHY

ByteCase tools are designed to create transparent case folders.

Default root folder:
{get_default_output_root()}

Current tool folder:
{TOOL_FOLDER_NAME}

Typical structure:
{DEFAULT_ROOT_FOLDER_NAME}/<case_number>/{TOOL_FOLDER_NAME}/

Item folders use this structure:
{DEFAULT_ROOT_FOLDER_NAME}/<case_number>/{TOOL_FOLDER_NAME}/items/item_001_mobile_phone/photos/

Generated outputs, copied supporting documents, item-level photo folders, and related indexes are kept together so the request packet can travel with related warrants, consent forms, scope memos, notes, screenshots, and other supporting documents.

ATTRIBUTION

Created by Matt McBride.
Published under the Forensics Byte brand.

Suite: {SUITE_NAME}
Tool: {APP_NAME}
Domain: {PRODUCT_DOMAIN}
"""

        about_text.insert("1.0", content)
        about_text.configure(state="disabled")

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, sticky="e")
        ttk.Button(button_frame, text="Close", command=self.window.destroy).pack(side="right")


class AttachmentWindow:
    def __init__(self, app, title, attachment=None, index=None):
        self.app = app
        self.index = index
        self.attachment = attachment or blank_attachment()

        self.window = tk.Toplevel(app.root)
        self.window.title(title)
        self.window.geometry("860x620")
        self.window.transient(app.root)
        self.window.grab_set()
        self.window.configure(bg=app.colors["app_background"])

        self.vars = {}
        self.build()
        self.load_attachment()

    def build(self):
        frame = ttk.Frame(self.window, padding=10)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(3, weight=1)

        fields = [
            ("attachment_number", "Attachment Number", 0, 0),
            ("attachment_type", "Attachment Type", 0, 2),
            ("source_path", "Source File Path", 1, 0),
            ("file_name", "File Name", 2, 0),
            ("related_item", "Related Evidence Item", 2, 2),
            ("document_date", "Document Date", 3, 0),
            ("provided_by", "Provided By", 3, 2),
            ("description", "Short Description", 4, 0),
        ]

        for key, label, row, column in fields:
            self.vars[key] = tk.StringVar()
            ttk.Label(frame, text=label).grid(row=row, column=column, sticky="w", pady=5)

            if key == "attachment_type":
                ttk.Combobox(
                    frame,
                    textvariable=self.vars[key],
                    values=ATTACHMENT_TYPES,
                    state="readonly",
                ).grid(row=row, column=column + 1, sticky="ew", pady=5)
            else:
                ttk.Entry(frame, textvariable=self.vars[key]).grid(row=row, column=column + 1, sticky="ew", pady=5)

        ttk.Button(frame, text="Browse", command=self.browse_source_file).grid(row=1, column=4, padx=4, pady=5)

        ttk.Label(frame, text="Notes").grid(row=5, column=0, sticky="nw", pady=5)
        self.notes_text = tk.Text(frame, height=10, width=80)
        self.notes_text.grid(row=5, column=1, columnspan=3, sticky="nsew", pady=5)
        self.app.style_text(self.notes_text)

        helper = (
            "Attachments are copied into the exported request folder when possible. "
            "The original source files are not modified."
        )
        ttk.Label(frame, text=helper, style="Muted.TLabel", wraplength=780).grid(
            row=6,
            column=0,
            columnspan=4,
            sticky="w",
            pady=(8, 0),
        )

        button_frame = ttk.Frame(self.window, padding=10)
        button_frame.pack(fill="x")
        ttk.Button(button_frame, text="Save Attachment", command=self.save, style="Primary.TButton").pack(side="right", padx=4)
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side="right", padx=4)

    def browse_source_file(self):
        path = filedialog.askopenfilename(
            title="Select Supporting Document",
            filetypes=[
                ("All Files", "*.*"),
                ("PDF Files", "*.pdf"),
                ("Word Documents", "*.docx *.doc"),
                ("Image Files", "*.png *.jpg *.jpeg"),
                ("Text Files", "*.txt"),
            ],
        )

        if not path:
            return

        self.vars["source_path"].set(path)

        if not self.vars["file_name"].get().strip():
            self.vars["file_name"].set(os.path.basename(path))

    def load_attachment(self):
        for key, variable in self.vars.items():
            variable.set(self.attachment.get(key, ""))

        self.notes_text.insert("1.0", self.attachment.get("notes", ""))

    def save(self):
        attachment = {key: variable.get().strip() for key, variable in self.vars.items()}
        attachment["notes"] = self.notes_text.get("1.0", "end").strip()

        if not attachment.get("file_name") and attachment.get("source_path"):
            attachment["file_name"] = os.path.basename(attachment["source_path"])

        self.app.save_attachment(attachment, self.index)
        self.window.destroy()

class ItemWindow:
    def __init__(self, app, title, item=None, index=None):
        self.app = app
        self.index = index
        self.item = normalize_item_for_gui(item or blank_item())
        self.item_photos = [photo.copy() for photo in self.item.get("item_photos", [])]
        self.peripherals = [peripheral.copy() for peripheral in self.item.get("peripherals", [])]
        self.photo_tab_visible = False
        self.peripheral_tab_visible = False

        self.window = tk.Toplevel(app.root)
        self.window.title(title)
        self.window.geometry("980x760")
        self.window.transient(app.root)
        self.window.grab_set()
        self.window.configure(bg=app.colors["app_background"])
        self.vars = {}
        self.type_specific_vars = {}
        self.build()
        self.load_item()
        self.rebuild_type_fields()
        self.refresh_photos_table()
        self.refresh_peripherals_table()

    def build(self):
        outer = ttk.Frame(self.window, padding=10)
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(0, weight=1)

        self.notebook = ttk.Notebook(outer)
        self.notebook.grid(row=0, column=0, sticky="nsew")

        self.details_tab = ttk.Frame(self.notebook, padding=10)
        self.photos_tab = ttk.Frame(self.notebook, padding=10)
        self.peripherals_tab = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.details_tab, text="Item Details")

        self.build_details_tab()
        self.build_photos_tab()
        self.build_peripherals_tab()

        helper = (
            "Photos and peripherals are available only for physical evidence item types. "
            "Item photos are copied and indexed during export; they are not embedded into the DOCX report."
        )
        ttk.Label(outer, text=helper, style="Muted.TLabel", wraplength=920).grid(row=1, column=0, sticky="w", pady=(8, 0))

        button_frame = ttk.Frame(self.window, padding=10)
        button_frame.pack(fill="x")
        ttk.Button(button_frame, text="Save Item", command=self.save, style="Primary.TButton").pack(side="right", padx=4)
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side="right", padx=4)

    def build_details_tab(self):
        frame = self.details_tab
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(3, weight=1)
        frame.rowconfigure(3, weight=1)

        fields = [
            ("item_number", "Item Number", 0, 0),
            ("evidence_number", "Evidence Number", 0, 2),
            ("device_or_media_type", "Device / Media Type", 1, 0),
            ("short_description", "Short Description", 1, 2),
            ("condition_received", "Condition Received", 2, 0),
            ("packaging_seal_info", "Packaging / Seal Information", 2, 2),
        ]

        for key, label, row, column in fields:
            self.vars[key] = tk.StringVar()
            ttk.Label(frame, text=label).grid(row=row, column=column, sticky="w", pady=5)
            if key == "device_or_media_type":
                combo = ttk.Combobox(frame, textvariable=self.vars[key], values=DEVICE_MEDIA_TYPES, state="readonly")
                combo.grid(row=row, column=column + 1, sticky="ew", pady=5)
                combo.bind("<<ComboboxSelected>>", lambda event: self.rebuild_type_fields())
            else:
                ttk.Entry(frame, textvariable=self.vars[key]).grid(row=row, column=column + 1, sticky="ew", pady=5)

        self.type_frame = ttk.LabelFrame(frame, text="Type-Specific Details", padding=10)
        self.type_frame.grid(row=3, column=0, columnspan=4, sticky="nsew", pady=(8, 4))
        self.type_frame.columnconfigure(1, weight=1)
        self.type_frame.columnconfigure(3, weight=1)

        ttk.Label(frame, text="Item Notes").grid(row=4, column=0, sticky="nw", pady=5)
        self.item_notes_text = tk.Text(frame, height=8, width=80)
        self.item_notes_text.grid(row=4, column=1, columnspan=3, sticky="nsew", pady=5)
        self.app.style_text(self.item_notes_text)

    def build_photos_tab(self):
        frame = self.photos_tab
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        entry_frame = ttk.LabelFrame(frame, text="Add Item Photo", padding=10)
        entry_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        entry_frame.columnconfigure(1, weight=1)
        entry_frame.columnconfigure(3, weight=1)

        self.photo_type_var = tk.StringVar()
        self.photo_description_var = tk.StringVar()

        ttk.Label(entry_frame, text="Photo Type").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Combobox(entry_frame, textvariable=self.photo_type_var, values=PHOTO_TYPES, state="readonly").grid(row=0, column=1, sticky="ew", pady=5)
        ttk.Label(entry_frame, text="Description").grid(row=0, column=2, sticky="w", pady=5, padx=(12, 0))
        ttk.Entry(entry_frame, textvariable=self.photo_description_var).grid(row=0, column=3, sticky="ew", pady=5)
        ttk.Button(entry_frame, text="Upload Photo", command=self.add_photo).grid(row=0, column=4, padx=6)

        table_frame = ttk.LabelFrame(frame, text="Item Photo Index", padding=10)
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("number", "type", "description", "source_path")
        self.photos_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        headings = {"number": "Photo #", "type": "Type", "description": "Description", "source_path": "Source Path"}
        widths = {"number": 90, "type": 180, "description": 260, "source_path": 420}
        for column in columns:
            self.photos_tree.heading(column, text=headings[column])
            self.photos_tree.column(column, width=widths[column], anchor="w")
        self.photos_tree.grid(row=0, column=0, sticky="nsew")

        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.photos_tree.yview)
        y_scroll.grid(row=0, column=1, sticky="ns")
        self.photos_tree.configure(yscrollcommand=y_scroll.set)

        buttons = ttk.Frame(frame, padding=(0, 8, 0, 0))
        buttons.grid(row=2, column=0, sticky="ew")
        buttons.columnconfigure(0, weight=1)
        self.photo_count_var = tk.StringVar(value="Photos: 0")
        ttk.Label(buttons, textvariable=self.photo_count_var, style="Muted.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Button(buttons, text="Remove Selected", command=self.remove_selected_photo).grid(row=0, column=1, padx=4)

    def build_peripherals_tab(self):
        frame = self.peripherals_tab
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        table_frame = ttk.LabelFrame(frame, text="Peripherals / Accessories", padding=10)
        table_frame.grid(row=0, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("number", "type", "description", "serial", "condition")
        self.peripherals_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        headings = {"number": "#", "type": "Type", "description": "Description", "serial": "Serial / Identifier", "condition": "Condition"}
        widths = {"number": 70, "type": 180, "description": 300, "serial": 180, "condition": 160}
        for column in columns:
            self.peripherals_tree.heading(column, text=headings[column])
            self.peripherals_tree.column(column, width=widths[column], anchor="w")
        self.peripherals_tree.grid(row=0, column=0, sticky="nsew")
        self.peripherals_tree.bind("<Double-1>", lambda event: self.edit_selected_peripheral())

        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.peripherals_tree.yview)
        y_scroll.grid(row=0, column=1, sticky="ns")
        self.peripherals_tree.configure(yscrollcommand=y_scroll.set)

        buttons = ttk.Frame(frame, padding=(0, 8, 0, 0))
        buttons.grid(row=1, column=0, sticky="ew")
        buttons.columnconfigure(0, weight=1)
        self.peripheral_count_var = tk.StringVar(value="Peripherals: 0")
        ttk.Label(buttons, textvariable=self.peripheral_count_var, style="Muted.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Button(buttons, text="Add Peripheral", command=self.add_peripheral).grid(row=0, column=1, padx=4)
        ttk.Button(buttons, text="Edit Selected", command=self.edit_selected_peripheral).grid(row=0, column=2, padx=4)
        ttk.Button(buttons, text="Remove Selected", command=self.remove_selected_peripheral).grid(row=0, column=3, padx=4)

    def is_physical_item(self):
        return self.vars.get("device_or_media_type", tk.StringVar()).get() in PHYSICAL_ITEM_TYPES

    def update_physical_tabs(self):
        is_physical = self.is_physical_item()

        def show_tab(frame, label):
            try:
                state = self.notebook.tab(frame, "state")
            except tk.TclError:
                self.notebook.add(frame, text=label)
                return

            if state == "hidden":
                self.notebook.add(frame, text=label)

        def hide_tab(frame):
            try:
                self.notebook.hide(frame)
            except tk.TclError:
                pass

        if is_physical:
            show_tab(self.photos_tab, "Photos")
            show_tab(self.peripherals_tab, "Peripherals")
        else:
            hide_tab(self.photos_tab)
            hide_tab(self.peripherals_tab)

    def rebuild_type_fields(self):
        existing_values = {
            key: variable.get()
            for key, variable in self.type_specific_vars.items()
        }

        for child in self.type_frame.winfo_children():
            child.destroy()

        self.type_specific_vars = {}
        device_type = self.vars.get("device_or_media_type", tk.StringVar()).get()
        fields = DEVICE_FIELD_TEMPLATES.get(device_type, [])

        if not fields:
            ttk.Label(
                self.type_frame,
                text="Select a device/media type to show relevant fields.",
                style="Muted.TLabel",
            ).grid(row=0, column=0, columnspan=4, sticky="w")
            self.update_physical_tabs()
            return

        for index, (key, label) in enumerate(fields):
            row = index // 2
            column = 0 if index % 2 == 0 else 2
            self.type_specific_vars[key] = tk.StringVar(value=existing_values.get(key, self.item.get("type_specific", {}).get(key, "")))

            ttk.Label(self.type_frame, text=label).grid(row=row, column=column, sticky="w", pady=5)
            ttk.Entry(self.type_frame, textvariable=self.type_specific_vars[key]).grid(row=row, column=column + 1, sticky="ew", pady=5)

        self.update_physical_tabs()

    def load_item(self):
        for key, variable in self.vars.items():
            variable.set(self.item.get(key, ""))

        self.item_notes_text.insert("1.0", self.item.get("item_notes", ""))

    def add_photo(self):
        if not self.is_physical_item():
            messagebox.showinfo("Item Photos", "Photos can only be added to physical evidence item types.")
            return

        photo_type = self.photo_type_var.get().strip()
        if not photo_type:
            messagebox.showinfo("Item Photos", "Select what the photo is of before uploading.")
            return

        path = filedialog.askopenfilename(
            title="Select Item Photo",
            filetypes=[
                ("Image Files", "*.png *.jpg *.jpeg *.webp *.bmp *.tif *.tiff"),
                ("All Files", "*.*"),
            ],
        )

        if not path:
            return

        self.item_photos.append({
            "photo_number": str(len(self.item_photos) + 1).zfill(3),
            "photo_type": photo_type,
            "source_path": path,
            "file_name": os.path.basename(path),
            "description": self.photo_description_var.get().strip(),
        })
        self.photo_description_var.set("")
        self.refresh_photos_table()

    def remove_selected_photo(self):
        selected = self.photos_tree.selection()
        if not selected:
            messagebox.showinfo("Remove Photo", "Select a photo to remove.")
            return
        index = int(selected[0])
        self.item_photos.pop(index)
        for photo_index, photo in enumerate(self.item_photos, start=1):
            photo["photo_number"] = str(photo_index).zfill(3)
        self.refresh_photos_table()

    def refresh_photos_table(self):
        for row in self.photos_tree.get_children():
            self.photos_tree.delete(row)
        for index, photo in enumerate(self.item_photos):
            self.photos_tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    photo.get("photo_number", ""),
                    photo.get("photo_type", ""),
                    photo.get("description", ""),
                    photo.get("source_path", ""),
                ),
            )
        self.photo_count_var.set(f"Photos: {len(self.item_photos)}")

    def add_peripheral(self):
        if not self.is_physical_item():
            messagebox.showinfo("Peripherals", "Peripherals can only be added to physical evidence item types.")
            return
        PeripheralWindow(self, title="Add Peripheral / Accessory")

    def edit_selected_peripheral(self):
        selected = self.peripherals_tree.selection()
        if not selected:
            messagebox.showinfo("Edit Peripheral", "Select a peripheral/accessory to edit.")
            return
        index = int(selected[0])
        PeripheralWindow(
            self,
            title="Edit Peripheral / Accessory",
            peripheral=self.peripherals[index].copy(),
            index=index,
        )

    def remove_selected_peripheral(self):
        selected = self.peripherals_tree.selection()
        if not selected:
            messagebox.showinfo("Remove Peripheral", "Select a peripheral/accessory to remove.")
            return
        index = int(selected[0])
        self.peripherals.pop(index)
        for peripheral_index, peripheral in enumerate(self.peripherals, start=1):
            peripheral["peripheral_number"] = str(peripheral_index).zfill(3)
        self.refresh_peripherals_table()

    def save_peripheral(self, peripheral, index=None):
        if index is None:
            if not peripheral.get("peripheral_number", "").strip():
                peripheral["peripheral_number"] = str(len(self.peripherals) + 1).zfill(3)
            self.peripherals.append(peripheral)
        else:
            self.peripherals[index] = peripheral
        self.refresh_peripherals_table()

    def refresh_peripherals_table(self):
        for row in self.peripherals_tree.get_children():
            self.peripherals_tree.delete(row)
        for index, peripheral in enumerate(self.peripherals):
            self.peripherals_tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    peripheral.get("peripheral_number", ""),
                    peripheral.get("peripheral_type", ""),
                    peripheral.get("description", ""),
                    peripheral.get("serial_identifier", ""),
                    peripheral.get("condition", ""),
                ),
            )
        self.peripheral_count_var.set(f"Peripherals: {len(self.peripherals)}")

    def save(self):
        item = {
            "item_number": self.vars["item_number"].get().strip(),
            "evidence_number": self.vars["evidence_number"].get().strip(),
            "device_or_media_type": self.vars["device_or_media_type"].get().strip(),
            "short_description": self.vars["short_description"].get().strip(),
            "condition_received": self.vars["condition_received"].get().strip(),
            "packaging_seal_info": self.vars["packaging_seal_info"].get().strip(),
            "type_specific": {
                key: variable.get().strip()
                for key, variable in self.type_specific_vars.items()
                if variable.get().strip()
            },
            "item_photos": self.item_photos if self.is_physical_item() else [],
            "peripherals": self.peripherals if self.is_physical_item() else [],
            "item_notes": self.item_notes_text.get("1.0", "end").strip(),
        }

        self.app.save_item(item, self.index)
        self.window.destroy()


class PeripheralWindow:
    def __init__(self, item_window, title, peripheral=None, index=None):
        self.item_window = item_window
        self.app = item_window.app
        self.index = index
        self.peripheral = peripheral or {}

        self.window = tk.Toplevel(item_window.window)
        self.window.title(title)
        self.window.geometry("760x420")
        self.window.transient(item_window.window)
        self.window.grab_set()
        self.window.configure(bg=self.app.colors["app_background"])
        self.vars = {}
        self.build()
        self.load()

    def build(self):
        frame = ttk.Frame(self.window, padding=10)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(3, weight=1)

        fields = [
            ("peripheral_number", "Peripheral Number", 0, 0),
            ("peripheral_type", "Peripheral Type", 0, 2),
            ("description", "Description", 1, 0),
            ("serial_identifier", "Serial / Identifier", 1, 2),
            ("condition", "Condition", 2, 0),
            ("included_with_item", "Included With Item", 2, 2),
        ]

        for key, label, row, column in fields:
            self.vars[key] = tk.StringVar()
            ttk.Label(frame, text=label).grid(row=row, column=column, sticky="w", pady=5)
            if key == "peripheral_type":
                ttk.Combobox(frame, textvariable=self.vars[key], values=PERIPHERAL_TYPES, state="readonly").grid(row=row, column=column + 1, sticky="ew", pady=5)
            else:
                ttk.Entry(frame, textvariable=self.vars[key]).grid(row=row, column=column + 1, sticky="ew", pady=5)

        ttk.Label(frame, text="Notes").grid(row=3, column=0, sticky="nw", pady=5)
        self.notes_text = tk.Text(frame, height=8, width=70)
        self.notes_text.grid(row=3, column=1, columnspan=3, sticky="nsew", pady=5)
        self.app.style_text(self.notes_text)

        button_frame = ttk.Frame(self.window, padding=10)
        button_frame.pack(fill="x")
        ttk.Button(button_frame, text="Save Peripheral", command=self.save, style="Primary.TButton").pack(side="right", padx=4)
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side="right", padx=4)

    def load(self):
        for key, variable in self.vars.items():
            variable.set(self.peripheral.get(key, ""))
        self.notes_text.insert("1.0", self.peripheral.get("notes", ""))

    def save(self):
        peripheral = {key: variable.get().strip() for key, variable in self.vars.items()}
        peripheral["notes"] = self.notes_text.get("1.0", "end").strip()
        self.item_window.save_peripheral(peripheral, self.index)
        self.window.destroy()


class ReviewWindow:
    def __init__(self, app, packet, warnings):
        self.app = app
        self.packet = packet
        self.window = tk.Toplevel(app.root)
        self.window.title("Review Request")
        self.window.geometry("900x620")
        self.window.transient(app.root)
        self.window.grab_set()
        self.window.configure(bg=app.colors["app_background"])
        self.build(warnings)

    def build(self, warnings):
        frame = ttk.Frame(self.window, padding=10)
        frame.pack(fill="both", expand=True)

        text = tk.Text(frame, wrap="word")
        text.pack(fill="both", expand=True)
        self.app.style_text(text)
        text.insert("1.0", self.app.review_text(self.packet, warnings))
        text.configure(state="disabled")

        button_frame = ttk.Frame(self.window, padding=10)
        button_frame.pack(fill="x")
        ttk.Button(
            button_frame,
            text="Confirm Export",
            command=lambda: self.app.export_request(self.packet, self.window),
            style="Primary.TButton",
        ).pack(side="right", padx=4)
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side="right", padx=4)


class SettingsWindow:
    def __init__(self, app):
        self.app = app
        self.settings = app.settings.copy()
        self.window = tk.Toplevel(app.root)
        self.window.title("ByteCase Intake Settings")
        self.window.geometry("860x760")
        self.window.transient(app.root)
        self.window.grab_set()
        self.window.configure(bg=app.colors["app_background"])
        self.build()
        self.load()

    def build(self):
        frame = ttk.Frame(self.window, padding=10)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(1, weight=1)

        self.agency_var = tk.StringVar()
        self.unit_var = tk.StringVar()
        self.default_investigator_var = tk.StringVar()
        self.base_output_var = tk.StringVar()
        self.patch_image_var = tk.StringVar()
        self.theme_var = tk.StringVar(value="System Default")
        self.ack_var = tk.BooleanVar()

        self.row(frame, "Agency / Department Name", self.agency_var, 0)
        self.row(frame, "Unit Name", self.unit_var, 1)
        self.row(frame, "Default Investigator", self.default_investigator_var, 2)

        ttk.Label(frame, text="Investigator List").grid(row=3, column=0, sticky="nw", pady=5)
        self.investigators_text = tk.Text(frame, height=8, width=50)
        self.investigators_text.grid(row=3, column=1, sticky="nsew", pady=5)
        self.app.style_text(self.investigators_text)

        self.row(frame, "ByteCase Output Root", self.base_output_var, 4)
        ttk.Button(frame, text="Browse", command=self.browse_output).grid(row=4, column=2, padx=4)

        output_help = (
            f"Leave blank to use the default local ByteCase folder: {get_default_output_root()}\n"
            "When a custom root is selected, ByteCase creates case folders directly inside that location: "
            "<custom root>\\<case_number>\\intake\\"
        )
        ttk.Label(frame, text=output_help, style="Muted.TLabel", wraplength=720, justify="left").grid(
            row=5,
            column=0,
            columnspan=4,
            sticky="w",
            pady=(0, 8),
        )

        self.row(frame, "DOCX Branding Image", self.patch_image_var, 6)
        ttk.Button(frame, text="Browse", command=self.browse_patch).grid(row=6, column=2, padx=4)
        ttk.Button(frame, text="Clear", command=lambda: self.patch_image_var.set("")).grid(row=6, column=3, padx=4)

        appearance_frame = ttk.LabelFrame(frame, text="Appearance", padding=10)
        appearance_frame.grid(row=7, column=0, columnspan=4, sticky="ew", pady=(12, 4))
        appearance_frame.columnconfigure(1, weight=1)

        ttk.Label(appearance_frame, text="Theme").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Combobox(
            appearance_frame,
            textvariable=self.theme_var,
            values=THEME_DISPLAY_NAMES,
            state="readonly",
        ).grid(row=0, column=1, sticky="ew", pady=5)

        ttk.Label(
            appearance_frame,
            text="Theme changes apply after saving settings. System Default follows the operating system when it can be detected.",
            style="Muted.TLabel",
        ).grid(row=1, column=0, columnspan=2, sticky="w")

        ttk.Checkbutton(
            frame,
            text="Include submission acknowledgement block by default",
            variable=self.ack_var,
        ).grid(row=8, column=0, columnspan=2, sticky="w", pady=8)

        note = (
            "The branding image is optional and is used only in DOCX output. "
            "Supported formats: PNG, JPG, JPEG. "
            "The output root controls where ByteCase creates case folders; it does not change the case/tool folder pattern."
        )
        ttk.Label(frame, text=note, style="Muted.TLabel", wraplength=720).grid(
            row=9,
            column=0,
            columnspan=4,
            sticky="w",
            pady=(8, 0),
        )

        button_frame = ttk.Frame(self.window, padding=10)
        button_frame.pack(fill="x")
        ttk.Button(button_frame, text="Save", command=self.save, style="Primary.TButton").pack(side="right", padx=4)
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side="right", padx=4)

    def row(self, parent, label, variable, row):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=5)
        ttk.Entry(parent, textvariable=variable).grid(row=row, column=1, sticky="ew", pady=5)

    def load(self):
        settings = self.settings
        self.agency_var.set(settings.get("agency_name", ""))
        self.unit_var.set(settings.get("unit_name", ""))
        self.default_investigator_var.set(settings.get("default_investigator", ""))
        self.base_output_var.set(settings.get("output_paths", {}).get("base_output_dir", ""))
        self.patch_image_var.set(settings.get("report_branding", {}).get("patch_image_path", ""))
        self.theme_var.set(display_theme_preference(settings.get("appearance", {}).get("theme", "system")))
        self.ack_var.set(bool(settings.get("report_defaults", {}).get("include_acknowledgement_block", True)))
        self.investigators_text.insert("1.0", "\n".join(settings.get("investigators", [])))

    def browse_output(self):
        path = filedialog.askdirectory(title="Select Base Output Folder")
        if path:
            self.base_output_var.set(path)

    def browse_patch(self):
        path = filedialog.askopenfilename(
            title="Select DOCX Branding Image",
            filetypes=[
                ("Image Files", "*.png *.jpg *.jpeg"),
                ("PNG Files", "*.png"),
                ("JPEG Files", "*.jpg *.jpeg"),
                ("All Files", "*.*"),
            ],
        )
        if path:
            self.patch_image_var.set(path)

    def save(self):
        investigators = []
        seen = set()
        for line in self.investigators_text.get("1.0", "end").splitlines():
            investigator = line.strip()
            key = investigator.lower()
            if investigator and key not in seen:
                investigators.append(investigator)
                seen.add(key)

        default_investigator = self.default_investigator_var.get().strip()
        if default_investigator and default_investigator.lower() not in seen:
            investigators.insert(0, default_investigator)

        self.settings.update(
            {
                "agency_name": self.agency_var.get().strip(),
                "unit_name": self.unit_var.get().strip(),
                "default_investigator": default_investigator,
                "investigators": investigators,
                "appearance": {"theme": theme_preference_from_display(self.theme_var.get())},
                "output_paths": {
                    "base_output_dir": self.base_output_var.get().strip(),
                    "use_shared_bytecase_root": True,
                },
                "report_branding": {"patch_image_path": self.patch_image_var.get().strip()},
                "report_defaults": {"include_acknowledgement_block": self.ack_var.get()},
            }
        )
        save_settings(self.settings)
        self.app.refresh_settings()
        self.window.destroy()
        messagebox.showinfo("Settings Saved", "Settings saved successfully.")