import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

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
    "External Hard Drive",
    "USB Drive",
    "SD / Memory Card",
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
        "make_model": "",
        "serial_number": "",
        "imei_meid": "",
        "phone_number": "",
        "storage_capacity": "",
        "condition_received": "",
        "power_lock_state": "",
        "passcode_provided": "",
        "known_account_info": "",
        "item_notes": "",
    }


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
        theme = self.settings.get("appearance", {}).get("theme", "dark")
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        if theme == "light":
            colors = {
                "bg": "#f5f5f5",
                "text": "#111111",
                "muted": "#444444",
                "accent": "#b8860b",
                "button": "#e6e6e6",
                "field": "#ffffff",
                "field_text": "#111111",
                "tree_bg": "#ffffff",
                "heading_bg": "#e8e8e8",
                "border": "#c0c0c0",
            }
        else:
            colors = {
                "bg": "#111111",
                "text": "#f2f2f2",
                "muted": "#c0c0c0",
                "accent": "#d4af37",
                "button": "#2a2a2a",
                "field": "#202020",
                "field_text": "#f2f2f2",
                "tree_bg": "#161616",
                "heading_bg": "#2a2a2a",
                "border": "#3a3a3a",
            }

        self.colors = colors
        self.root.configure(bg=colors["bg"])

        style.configure(
            ".",
            background=colors["bg"],
            foreground=colors["text"],
            fieldbackground=colors["field"],
            font=("Segoe UI", 10),
        )
        for style_name in ["TFrame", "TLabel", "TLabelframe", "TCheckbutton", "TNotebook"]:
            style.configure(style_name, background=colors["bg"], foreground=colors["text"])

        style.configure(
            "Title.TLabel",
            background=colors["bg"],
            foreground=colors["accent"],
            font=("Segoe UI", 16, "bold"),
        )
        style.configure("Muted.TLabel", background=colors["bg"], foreground=colors["muted"])
        style.configure(
            "TLabelframe.Label",
            background=colors["bg"],
            foreground=colors["accent"],
            font=("Segoe UI", 10, "bold"),
        )
        style.configure("TButton", background=colors["button"], foreground=colors["text"], padding=6)
        style.map(
            "TButton",
            background=[("active", colors["accent"])],
            foreground=[("active", "#111111")],
        )
        style.configure("TCheckbutton", background=colors["bg"], foreground=colors["text"])
        style.map("TCheckbutton", background=[("active", colors["bg"])], foreground=[("active", colors["accent"])])
        style.configure(
            "TEntry",
            fieldbackground=colors["field"],
            foreground=colors["field_text"],
            insertcolor=colors["accent"],
        )
        style.configure(
            "TCombobox",
            fieldbackground=colors["field"],
            background=colors["button"],
            foreground=colors["field_text"],
            arrowcolor=colors["accent"],
        )
        style.map("TCombobox", fieldbackground=[("readonly", colors["field"])], foreground=[("readonly", colors["field_text"])])
        style.configure("TNotebook.Tab", background=colors["button"], foreground=colors["text"], padding=(10, 5))
        style.map(
            "TNotebook.Tab",
            background=[("selected", colors["accent"])],
            foreground=[("selected", "#111111")],
        )
        style.configure("Treeview", background=colors["tree_bg"], fieldbackground=colors["tree_bg"], foreground=colors["text"], rowheight=24)
        style.configure("Treeview.Heading", background=colors["heading_bg"], foreground=colors["accent"], font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", colors["accent"])], foreground=[("selected", "#111111")])

    def style_text(self, widget):
        widget.configure(
            background=self.colors["field"],
            foreground=self.colors["field_text"],
            insertbackground=self.colors["accent"],
            selectbackground=self.colors["accent"],
            selectforeground="#111111",
            relief="solid",
            borderwidth=1,
        )

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
        ttk.Button(bottom, text="Review Request", command=self.review_request).grid(row=0, column=1, padx=4)
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

        columns = ("item_number", "evidence_number", "type", "make_model", "serial", "phone")
        self.items_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=14)
        headings = {
            "item_number": "Item #",
            "evidence_number": "Evidence #",
            "type": "Type",
            "make_model": "Make / Model",
            "serial": "Serial",
            "phone": "Phone",
        }
        widths = {
            "item_number": 90,
            "evidence_number": 130,
            "type": 180,
            "make_model": 220,
            "serial": 180,
            "phone": 140,
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

        handoff_frame = ttk.LabelFrame(frame, text="Submission / Handoff", padding=10)
        handoff_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        handoff_frame.columnconfigure(1, weight=1)

        self.transfer_method_var = tk.StringVar()
        self.packaging_seal_info_var = tk.StringVar()
        self.include_acknowledgement_block_var = tk.BooleanVar(value=True)

        self.entry(handoff_frame, "Transfer Method", self.transfer_method_var, 0, 0)
        self.entry(handoff_frame, "Packaging / Seal Information", self.packaging_seal_info_var, 1, 0)
        ttk.Checkbutton(
            handoff_frame,
            text="Include submission acknowledgement block",
            variable=self.include_acknowledgement_block_var,
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=8)

        ttk.Label(handoff_frame, text="Handoff Notes").grid(row=3, column=0, sticky="nw", pady=5)
        self.handoff_notes_text = tk.Text(handoff_frame, height=10, width=50)
        self.handoff_notes_text.grid(row=3, column=1, sticky="nsew", pady=5)
        self.style_text(self.handoff_notes_text)

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
            self.items_tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    item.get("item_number", ""),
                    item.get("evidence_number", ""),
                    item.get("device_or_media_type", ""),
                    item.get("make_model", ""),
                    item.get("serial_number", ""),
                    item.get("phone_number", ""),
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
                "transfer_method": self.transfer_method_var.get(),
                "packaging_seal_info": self.packaging_seal_info_var.get(),
                "handoff_notes": self.handoff_notes_text.get("1.0", "end").strip(),
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
            "Click Confirm Export to create a request folder with TXT, DOCX, JSON, and copied attachments.",
        ])
        return "\n".join(lines)

    def export_request(self, packet, window):
        try:
            txt_path, docx_path, json_path, request_folder, copied_count = save_request_outputs(packet, self.settings)
            window.destroy()
            self.status_var.set("Request exported successfully.")
            messagebox.showinfo(
                "Request Exported",
                "ByteCase Intake request packet exported successfully.\n\n"
                f"Request Folder:\n{request_folder}\n\n"
                f"TXT:\n{txt_path}\n\n"
                f"DOCX:\n{docx_path}\n\n"
                f"JSON:\n{json_path}\n\n"
                f"Attachments copied: {copied_count}",
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
            self.transfer_method_var,
            self.packaging_seal_info_var,
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
        self.window.configure(bg=app.colors["bg"])

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

PLATFORM IDEOLOGY

ByteCase tools are built around a simple principle:

Bake in best practices, structure, and guidance while preserving enough flexibility for agencies to customize their workflow.

Small and medium agencies do not always have rigid digital forensics workflows, dedicated lab-management systems, or standardized request processes. ByteCase is designed to support practical documentation without forcing every agency into one model.

The tool should guide better submissions, reduce repeat typing, and create clearer handoffs between investigators and examiners.

WHAT THIS TOOL DOES NOT DO

ByteCase Intake does not perform forensic acquisition, extraction, hashing, parsing, artifact analysis, legal review, or investigative conclusions.

It creates a request packet based on information provided by the investigator or submitting party.

Legal authority, scope, and agency policy should be reviewed under the user's agency procedures and applicable law before forensic work begins.

OUTPUT PHILOSOPHY

ByteCase tools are designed to create transparent case folders.

Default root folder:
{get_default_output_root()}

Current tool folder:
{TOOL_FOLDER_NAME}

Typical structure:
{DEFAULT_ROOT_FOLDER_NAME}/<case_number>/{TOOL_FOLDER_NAME}/

Generated outputs and copied supporting documents are kept together so the request packet can travel with related warrants, consent forms, scope memos, notes, screenshots, and other supporting documents.

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
        self.window.configure(bg=app.colors["bg"])

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
        ttk.Button(button_frame, text="Save Attachment", command=self.save).pack(side="right", padx=4)
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
        self.item = item or blank_item()
        self.window = tk.Toplevel(app.root)
        self.window.title(title)
        self.window.geometry("780x560")
        self.window.transient(app.root)
        self.window.grab_set()
        self.window.configure(bg=app.colors["bg"])
        self.vars = {}
        self.build()
        self.load_item()

    def build(self):
        frame = ttk.Frame(self.window, padding=10)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(3, weight=1)

        fields = [
            ("item_number", "Item Number", 0, 0),
            ("evidence_number", "Evidence Number", 0, 2),
            ("device_or_media_type", "Device / Media Type", 1, 0),
            ("make_model", "Make / Model", 1, 2),
            ("serial_number", "Serial Number", 2, 0),
            ("imei_meid", "IMEI / MEID", 2, 2),
            ("phone_number", "Phone Number", 3, 0),
            ("storage_capacity", "Storage Capacity", 3, 2),
            ("condition_received", "Condition Received", 4, 0),
            ("power_lock_state", "Power / Lock State", 4, 2),
            ("passcode_provided", "Passcode / Password Provided", 5, 0),
            ("known_account_info", "Known Account Info", 5, 2),
        ]

        for key, label, row, column in fields:
            self.vars[key] = tk.StringVar()
            ttk.Label(frame, text=label).grid(row=row, column=column, sticky="w", pady=5)
            if key == "device_or_media_type":
                ttk.Combobox(frame, textvariable=self.vars[key], values=DEVICE_MEDIA_TYPES, state="readonly").grid(row=row, column=column + 1, sticky="ew", pady=5)
            else:
                ttk.Entry(frame, textvariable=self.vars[key]).grid(row=row, column=column + 1, sticky="ew", pady=5)

        ttk.Label(frame, text="Item Notes").grid(row=6, column=0, sticky="nw", pady=5)
        self.item_notes_text = tk.Text(frame, height=10, width=80)
        self.item_notes_text.grid(row=6, column=1, columnspan=3, sticky="nsew", pady=5)
        self.app.style_text(self.item_notes_text)

        helper = "Only capture information useful to route or scope the request. Detailed examiner work belongs in the acquisition packet."
        ttk.Label(frame, text=helper, style="Muted.TLabel", wraplength=720).grid(row=7, column=0, columnspan=4, sticky="w", pady=(8, 0))

        button_frame = ttk.Frame(self.window, padding=10)
        button_frame.pack(fill="x")
        ttk.Button(button_frame, text="Save Item", command=self.save).pack(side="right", padx=4)
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side="right", padx=4)

    def load_item(self):
        for key, variable in self.vars.items():
            variable.set(self.item.get(key, ""))
        self.item_notes_text.insert("1.0", self.item.get("item_notes", ""))

    def save(self):
        item = {key: variable.get().strip() for key, variable in self.vars.items()}
        item["item_notes"] = self.item_notes_text.get("1.0", "end").strip()
        self.app.save_item(item, self.index)
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
        self.window.configure(bg=app.colors["bg"])
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
        ).pack(side="right", padx=4)
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side="right", padx=4)


class SettingsWindow:
    def __init__(self, app):
        self.app = app
        self.settings = app.settings.copy()
        self.window = tk.Toplevel(app.root)
        self.window.title("ByteCase Intake Settings")
        self.window.geometry("780x660")
        self.window.transient(app.root)
        self.window.grab_set()
        self.window.configure(bg=app.colors["bg"])
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
        self.theme_var = tk.StringVar(value="dark")
        self.ack_var = tk.BooleanVar()

        self.row(frame, "Agency / Department Name", self.agency_var, 0)
        self.row(frame, "Unit Name", self.unit_var, 1)
        self.row(frame, "Default Investigator", self.default_investigator_var, 2)

        ttk.Label(frame, text="Investigator List").grid(row=3, column=0, sticky="nw", pady=5)
        self.investigators_text = tk.Text(frame, height=8, width=50)
        self.investigators_text.grid(row=3, column=1, sticky="nsew", pady=5)
        self.app.style_text(self.investigators_text)

        self.row(frame, "Base Output Folder", self.base_output_var, 4)
        ttk.Button(frame, text="Browse", command=self.browse_output).grid(row=4, column=2, padx=4)

        self.row(frame, "DOCX Branding Image", self.patch_image_var, 5)
        ttk.Button(frame, text="Browse", command=self.browse_patch).grid(row=5, column=2, padx=4)
        ttk.Button(frame, text="Clear", command=lambda: self.patch_image_var.set("")).grid(row=5, column=3, padx=4)

        appearance_frame = ttk.LabelFrame(frame, text="Appearance", padding=10)
        appearance_frame.grid(row=6, column=0, columnspan=4, sticky="ew", pady=(12, 4))
        appearance_frame.columnconfigure(1, weight=1)

        ttk.Label(appearance_frame, text="Theme").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Combobox(
            appearance_frame,
            textvariable=self.theme_var,
            values=["dark", "light"],
            state="readonly",
        ).grid(row=0, column=1, sticky="ew", pady=5)

        ttk.Label(
            appearance_frame,
            text="Theme changes apply after saving settings.",
            style="Muted.TLabel",
        ).grid(row=1, column=0, columnspan=2, sticky="w")

        ttk.Checkbutton(
            frame,
            text="Include submission acknowledgement block by default",
            variable=self.ack_var,
        ).grid(row=7, column=0, columnspan=2, sticky="w", pady=8)

        note = (
            "The branding image is optional and is used only in DOCX output. "
            "Supported formats: PNG, JPG, JPEG. "
            f"If Base Output Folder is blank, exports default to {get_default_output_root()} with one folder per case number."
        )
        ttk.Label(frame, text=note, style="Muted.TLabel", wraplength=680).grid(
            row=8,
            column=0,
            columnspan=4,
            sticky="w",
            pady=(8, 0),
        )

        button_frame = ttk.Frame(self.window, padding=10)
        button_frame.pack(fill="x")
        ttk.Button(button_frame, text="Save", command=self.save).pack(side="right", padx=4)
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
        self.theme_var.set(settings.get("appearance", {}).get("theme", "dark"))
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
                "appearance": {"theme": self.theme_var.get()},
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