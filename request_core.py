import json
import shutil
from copy import deepcopy
from datetime import datetime
from pathlib import Path

from docx_exporter import save_docx_request
from settings_service import (
    APP_NAME,
    APP_SUBTITLE,
    APP_VERSION,
    PRODUCT_DOMAIN,
    PUBLISHER_NAME,
    SUITE_NAME,
    TOOL_FOLDER_NAME,
    ensure_case_tool_directories,
)

SCHEMA_NAME = "bytecase_digital_forensics_request_packet"
SCHEMA_VERSION = "0.7"

COMMON_ITEM_FIELDS = [
    ("item_number", "Item Number"),
    ("evidence_number", "Evidence Number"),
    ("device_or_media_type", "Device / Media Type"),
    ("short_description", "Short Description"),
    ("condition_received", "Condition Received"),
    ("packaging_seal_info", "Packaging / Seal Information"),
    ("item_notes", "Item Notes"),
]

TYPE_SPECIFIC_LABELS = {
    "make_model": "Make / Model",
    "serial_number": "Serial Number",
    "imei_meid": "IMEI / MEID",
    "phone_number": "Phone Number",
    "carrier": "Carrier",
    "sim_present": "SIM Present",
    "storage_capacity": "Storage Capacity",
    "power_lock_state": "Power / Lock State",
    "passcode_provided": "Passcode / Password Provided",
    "known_account_info": "Known Account Info",
    "serial_service_tag": "Serial / Service Tag",
    "operating_system": "Operating System",
    "storage_type": "Storage Type",
    "power_state": "Power State",
    "login_credentials_provided": "Login Credentials Provided",
    "known_user_account": "Known User Account",
    "brand_model": "Brand / Model",
    "connector_type": "Connector Type",
    "encryption_suspected": "Encryption Suspected",
    "card_type": "Card Type",
    "adapter_included": "Adapter Included",
    "connection_type": "Connection Type",
    "power_supply_included": "Power Supply Included",
    "channel_count": "Channel Count",
    "date_time_setting": "Date / Time Setting",
    "export_format": "Export Format",
    "network_info": "Network Info",
    "platform_provider": "Platform / Provider",
    "account_identifier": "Account Identifier",
    "return_export_date": "Return / Export Date",
    "source_authority": "Source Authority",
    "file_folder_location": "File / Folder Location",
    "export_date": "Export Date",
    "date_range": "Date Range",
    "producing_party": "Producing Party",
    "media_type": "Media Type",
    "source_device_platform": "Source Device / Platform",
    "file_folder_path": "File / Folder Path",
    "provided_by": "Provided By",
    "original_source_known": "Original Source Known",
    "identifier": "Identifier",
    "description": "Description",
    "capacity_size": "Capacity / Size",
    "source_origin": "Source / Origin",
    "additional_details": "Additional Details",
}

LEGACY_TYPE_FIELD_MAP = {
    "make_model": "make_model",
    "serial_number": "serial_number",
    "imei_meid": "imei_meid",
    "phone_number": "phone_number",
    "storage_capacity": "storage_capacity",
    "power_lock_state": "power_lock_state",
    "passcode_provided": "passcode_provided",
    "known_account_info": "known_account_info",
}


def safe_filename(value, fallback="request"):
    value = (value or "").strip() or fallback

    for char in '<>:"/\\|?*':
        value = value.replace(char, "_")

    value = value.replace(" ", "_")

    while "__" in value:
        value = value.replace("__", "_")

    return value.strip("_") or fallback


def clean_dict(data):
    return {key: str(value or "").strip() for key, value in data.items()}


def clean_list(values):
    return [str(value).strip() for value in values if str(value).strip()]


def unique_destination_path(folder, file_name):
    destination = folder / file_name

    if not destination.exists():
        return destination

    stem = destination.stem
    suffix = destination.suffix
    counter = 2

    while True:
        candidate = folder / f"{stem}_{counter}{suffix}"

        if not candidate.exists():
            return candidate

        counter += 1


def normalize_attachment(attachment, index):
    source_path = str(attachment.get("source_path", "")).strip()
    file_name = str(attachment.get("file_name", "")).strip()

    if not file_name and source_path:
        file_name = Path(source_path).name

    attachment_number = str(attachment.get("attachment_number", "")).strip()

    if not attachment_number:
        attachment_number = str(index).zfill(3)

    return {
        "attachment_number": attachment_number,
        "attachment_type": str(attachment.get("attachment_type", "")).strip(),
        "source_path": source_path,
        "file_name": file_name,
        "description": str(attachment.get("description", "")).strip(),
        "related_item": str(attachment.get("related_item", "")).strip(),
        "document_date": str(attachment.get("document_date", "")).strip(),
        "provided_by": str(attachment.get("provided_by", "")).strip(),
        "notes": str(attachment.get("notes", "")).strip(),
        "copy_status": str(attachment.get("copy_status", "")).strip(),
        "copied_path": str(attachment.get("copied_path", "")).strip(),
        "copy_error": str(attachment.get("copy_error", "")).strip(),
    }


def normalize_evidence_item(item, index):
    item_number = str(item.get("item_number", "")).strip() or str(index).zfill(3)
    device_type = str(item.get("device_or_media_type", "")).strip()

    type_specific = item.get("type_specific", {})
    if not isinstance(type_specific, dict):
        type_specific = {}

    cleaned_type_specific = {}
    for key, value in type_specific.items():
        value = str(value or "").strip()
        if value:
            cleaned_type_specific[str(key).strip()] = value

    # Backward compatibility for v0.6 flat item fields.
    for legacy_key, type_key in LEGACY_TYPE_FIELD_MAP.items():
        value = str(item.get(legacy_key, "")).strip()
        if value and type_key not in cleaned_type_specific:
            cleaned_type_specific[type_key] = value

    return {
        "item_number": item_number,
        "evidence_number": str(item.get("evidence_number", "")).strip(),
        "device_or_media_type": device_type,
        "short_description": str(item.get("short_description", "")).strip(),
        "condition_received": str(item.get("condition_received", "")).strip(),
        "packaging_seal_info": str(item.get("packaging_seal_info", "")).strip(),
        "type_specific": cleaned_type_specific,
        "item_notes": str(item.get("item_notes", "")).strip(),
    }


def get_item_rows(item):
    rows = []

    for key, label in COMMON_ITEM_FIELDS:
        value = item.get(key, "")
        if value:
            rows.append((label, value))

    type_specific = item.get("type_specific", {})
    if isinstance(type_specific, dict):
        for key, value in type_specific.items():
            value = str(value or "").strip()
            if not value:
                continue
            rows.append((TYPE_SPECIFIC_LABELS.get(key, key.replace("_", " ").title()), value))

    return rows


def summarize_item_type_specific(item, max_parts=3):
    type_specific = item.get("type_specific", {})
    if not isinstance(type_specific, dict):
        return ""

    parts = []
    priority_keys = [
        "make_model", "brand_model", "platform_provider", "media_type",
        "serial_number", "serial_service_tag", "storage_capacity", "phone_number",
        "account_identifier", "file_folder_path", "file_folder_location",
    ]

    for key in priority_keys:
        value = str(type_specific.get(key, "")).strip()
        if value:
            label = TYPE_SPECIFIC_LABELS.get(key, key.replace("_", " ").title())
            parts.append(f"{label}: {value}")
        if len(parts) >= max_parts:
            break

    return "; ".join(parts)


def copy_attachments_to_export_folder(packet, request_folder):
    attachments = packet.get("attachments", [])
    attachments_folder = request_folder / "attachments"
    copied_count = 0

    if attachments:
        attachments_folder.mkdir(parents=True, exist_ok=True)

    updated_attachments = []

    for index, attachment in enumerate(attachments, start=1):
        record = normalize_attachment(attachment, index)
        source_path_value = record.get("source_path", "")

        if not source_path_value:
            record["copy_status"] = "Not copied"
            record["copy_error"] = "No source path provided."
            updated_attachments.append(record)
            continue

        source_path = Path(source_path_value)

        if not source_path.exists() or not source_path.is_file():
            record["copy_status"] = "Not copied"
            record["copy_error"] = "Source file was not found or is not a file."
            updated_attachments.append(record)
            continue

        try:
            destination = unique_destination_path(attachments_folder, source_path.name)
            shutil.copy2(source_path, destination)

            record["file_name"] = source_path.name
            record["copy_status"] = "Copied"
            record["copied_path"] = str(destination)
            record["copy_error"] = ""
            copied_count += 1

        except OSError as exc:
            record["copy_status"] = "Copy failed"
            record["copy_error"] = str(exc)

        updated_attachments.append(record)

    packet["attachments"] = updated_attachments
    return copied_count


def build_request_packet(
    settings,
    case,
    investigator,
    authority,
    scope,
    evidence_items,
    attachments,
    details,
    priority,
    handoff,
    include_acknowledgement_block,
):
    return {
        "app_name": APP_NAME,
        "app_subtitle": APP_SUBTITLE,
        "app_version": APP_VERSION,
        "suite_name": SUITE_NAME,
        "publisher": PUBLISHER_NAME,
        "product_domain": PRODUCT_DOMAIN,
        "tool_folder_name": TOOL_FOLDER_NAME,
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "agency": {
            "agency_name": settings.get("agency_name", ""),
            "unit_name": settings.get("unit_name", ""),
        },
        "case_info": clean_dict(case),
        "investigator_info": clean_dict(investigator),
        "legal_authority": clean_dict(authority),
        "scope": {
            "scope_options": clean_list(scope.get("scope_options", [])),
            "date_range_limited": bool(scope.get("date_range_limited", False)),
            "specific_apps_limited": bool(scope.get("specific_apps_limited", False)),
            "specific_accounts_limited": bool(scope.get("specific_accounts_limited", False)),
            "keyword_limited": bool(scope.get("keyword_limited", False)),
            "authorized_date_range": str(scope.get("authorized_date_range", "")).strip(),
            "authorized_apps_platforms": str(scope.get("authorized_apps_platforms", "")).strip(),
            "authorized_accounts": str(scope.get("authorized_accounts", "")).strip(),
            "authorized_keywords": str(scope.get("authorized_keywords", "")).strip(),
            "scope_notes": str(scope.get("scope_notes", "")).strip(),
        },
        "evidence_items": [
            normalize_evidence_item(item, index)
            for index, item in enumerate(evidence_items, start=1)
        ],
        "attachments": [
            normalize_attachment(attachment, index)
            for index, attachment in enumerate(attachments, start=1)
        ],
        "request_details": {
            "requested_actions": clean_list(details.get("requested_actions", [])),
            "investigative_objective": str(details.get("investigative_objective", "")).strip(),
            "known_facts_for_examiner": str(details.get("known_facts_for_examiner", "")).strip(),
        },
        "priority_info": {
            "priority": str(priority.get("priority", "")).strip(),
            "requested_due_date": str(priority.get("requested_due_date", "")).strip(),
            "urgency_flags": clean_list(priority.get("urgency_flags", [])),
            "priority_notes": str(priority.get("priority_notes", "")).strip(),
        },
        "handoff_info": clean_dict(handoff),
        "report_options": {
            "include_acknowledgement_block": bool(include_acknowledgement_block),
            "export_style": "bytecase_case_folder_with_adaptive_item_templates",
        },
        "disclaimer": (
            "This request packet documents information provided for a digital forensic request. "
            "It does not represent forensic findings, examiner conclusions, legal advice, or independent "
            "verification of the submitted information. Legal authority and scope should be confirmed "
            "under agency policy and applicable law before forensic work begins."
        ),
    }


def add_key_value_section(lines, title, rows):
    lines.append(title)
    lines.append("-" * 80)

    for label, value in rows:
        lines.append(f"{label}: {value}")

    lines.append("")


def add_bullet_section(lines, title, values, empty_text="None selected."):
    lines.append(title)
    lines.append("-" * 80)

    if values:
        for value in values:
            lines.append(f"- {value}")
    else:
        lines.append(empty_text)

    lines.append("")


def build_txt_request(packet):
    agency = packet.get("agency", {})
    case = packet.get("case_info", {})
    investigator = packet.get("investigator_info", {})
    authority = packet.get("legal_authority", {})
    scope = packet.get("scope", {})
    items = packet.get("evidence_items", [])
    attachments = packet.get("attachments", [])
    details = packet.get("request_details", {})
    priority = packet.get("priority_info", {})
    handoff = packet.get("handoff_info", {})
    options = packet.get("report_options", {})

    lines = [
        "BYTECASE INTAKE",
        "Digital Forensics Request Packet",
        "=" * 80,
        f"Part of the {packet.get('suite_name', SUITE_NAME)} toolset by {packet.get('publisher', PUBLISHER_NAME)}",
        f"Product Domain: {packet.get('product_domain', PRODUCT_DOMAIN)}",
        "",
    ]

    add_key_value_section(lines, "AGENCY", [
        ("Agency / Department", agency.get("agency_name", "")),
        ("Unit", agency.get("unit_name", "")),
    ])

    add_key_value_section(lines, "REQUEST INFORMATION", [
        ("Generated By", f"{packet.get('app_name', '')} - {packet.get('app_subtitle', '')} v{packet.get('app_version', '')}"),
        ("Created At", packet.get("created_at", "")),
        ("Schema", f"{packet.get('schema_name', '')} v{packet.get('schema_version', '')}"),
    ])

    add_key_value_section(lines, "CASE INFORMATION", [
        ("Case Number", case.get("case_number", "")),
        ("Agency Case Number", case.get("agency_case_number", "")),
        ("Offense / Incident Type", case.get("offense_type", "")),
    ])

    add_key_value_section(lines, "SUBMITTING INVESTIGATOR", [
        ("Submitting Agency", investigator.get("submitting_agency", "")),
        ("Submitting Unit", investigator.get("submitting_unit", "")),
        ("Submitting Investigator", investigator.get("submitting_investigator", "")),
        ("Phone", investigator.get("investigator_phone", "")),
        ("Email", investigator.get("investigator_email", "")),
        ("Supervisor", investigator.get("supervisor", "")),
    ])

    add_key_value_section(lines, "LEGAL AUTHORITY", [
        ("Authority Type", authority.get("authority_type", "")),
        ("Authority Date", authority.get("authority_date", "")),
        ("Authority Reference / Document Number", authority.get("authority_reference", "")),
        ("Authority Notes", authority.get("authority_notes", "")),
    ])

    add_bullet_section(lines, "LEGAL AUTHORITY / SCOPE OPTIONS", scope.get("scope_options", []))

    add_key_value_section(lines, "SCOPE LIMITATIONS", [
        ("Date Range Limited", "Yes" if scope.get("date_range_limited") else "No"),
        ("Authorized Date Range", scope.get("authorized_date_range", "")),
        ("Specific Apps / Platforms Limited", "Yes" if scope.get("specific_apps_limited") else "No"),
        ("Authorized Apps / Platforms", scope.get("authorized_apps_platforms", "")),
        ("Specific Accounts Limited", "Yes" if scope.get("specific_accounts_limited") else "No"),
        ("Authorized Accounts", scope.get("authorized_accounts", "")),
        ("Keyword Limited", "Yes" if scope.get("keyword_limited") else "No"),
        ("Authorized Keywords", scope.get("authorized_keywords", "")),
        ("Additional Scope Notes", scope.get("scope_notes", "")),
    ])

    lines.extend(["EVIDENCE / DEVICE ITEMS", "-" * 80])

    if not items:
        lines.append("No evidence/device items listed.")
        lines.append("")
    else:
        for index, item in enumerate(items, start=1):
            lines.append(f"Item {index}")
            lines.append("~" * 40)

            for label, value in get_item_rows(item):
                lines.append(f"{label}: {value}")

            lines.append("")

    lines.extend(["ATTACHMENT INDEX", "-" * 80])

    if not attachments:
        lines.append("No supporting documents listed.")
        lines.append("")
    else:
        for attachment in attachments:
            lines.append(f"Attachment {attachment.get('attachment_number', '')}")
            lines.append("~" * 40)

            rows = [
                ("Type", attachment.get("attachment_type", "")),
                ("File Name", attachment.get("file_name", "")),
                ("Source Path", attachment.get("source_path", "")),
                ("Copied Path", attachment.get("copied_path", "")),
                ("Copy Status", attachment.get("copy_status", "")),
                ("Copy Error", attachment.get("copy_error", "")),
                ("Related Item", attachment.get("related_item", "")),
                ("Document Date", attachment.get("document_date", "")),
                ("Provided By", attachment.get("provided_by", "")),
                ("Description", attachment.get("description", "")),
                ("Notes", attachment.get("notes", "")),
            ]

            for label, value in rows:
                if value:
                    lines.append(f"{label}: {value}")

            lines.append("")

    add_bullet_section(
        lines,
        "REQUESTED FORENSIC ACTIONS",
        details.get("requested_actions", []),
        "No requested actions selected."
    )

    lines.extend([
        "INVESTIGATIVE OBJECTIVE / REQUESTED INFORMATION",
        "-" * 80,
        details.get("investigative_objective", ""),
        "",
        "KNOWN FACTS / CONTEXT FOR EXAMINER",
        "-" * 80,
        details.get("known_facts_for_examiner", ""),
        "",
    ])

    lines.extend([
        "PRIORITY / URGENCY",
        "-" * 80,
        f"Priority: {priority.get('priority', '')}",
        f"Requested Due Date: {priority.get('requested_due_date', '')}",
        "Urgency Flags:",
    ])

    flags = priority.get("urgency_flags", [])
    lines.extend([f"- {flag}" for flag in flags] if flags else ["None selected"])
    lines.extend([f"Priority Notes: {priority.get('priority_notes', '')}", ""])

    add_key_value_section(lines, "SUBMISSION / HANDOFF", [
        ("Transfer Method", handoff.get("transfer_method", "")),
        ("Packaging / Seal Information", handoff.get("packaging_seal_info", "")),
        ("Handoff Notes", handoff.get("handoff_notes", "")),
    ])

    lines.extend([
        "IMPORTANT SCOPE NOTE",
        "-" * 80,
        packet.get("disclaimer", ""),
        "",
    ])

    if options.get("include_acknowledgement_block"):
        lines.extend([
            "SUBMISSION ACKNOWLEDGEMENT",
            "-" * 80,
            f"Submitted By: {investigator.get('submitting_investigator', '')}",
            "Submitting Investigator Signature: _______________________________",
            "Date: ____________________",
            "",
            "Received By: _______________________________",
            "Receiving Staff Signature: _______________________________",
            "Date / Time Received: ____________________",
            "",
        ])

    lines.extend([
        "=" * 80,
        "End of ByteCase Intake Request Packet",
        "=" * 80
    ])

    return "\n".join(lines)


def save_request_outputs(packet, settings):
    case_number = packet.get("case_info", {}).get("case_number", "")
    paths = ensure_case_tool_directories(settings, case_number)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    case = safe_filename(case_number, "NO_CASE")
    base_name = f"{case}_{timestamp}_bytecase_intake"

    request_folder = paths["tool_dir"]
    request_folder.mkdir(parents=True, exist_ok=True)

    output_packet = deepcopy(packet)
    copied_count = copy_attachments_to_export_folder(output_packet, request_folder)

    txt_path = request_folder / f"{base_name}.txt"
    docx_path = request_folder / f"{base_name}.docx"
    json_path = request_folder / f"{base_name}.json"

    txt_path.write_text(build_txt_request(output_packet), encoding="utf-8")
    save_docx_request(output_packet, settings, docx_path)

    json_data = json.dumps(output_packet, indent=2)
    json_path.write_text(json_data, encoding="utf-8")

    return txt_path, docx_path, json_path, request_folder, copied_count