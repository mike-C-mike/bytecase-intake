from pathlib import Path


def validate_request_for_export(packet):
    errors = []
    warnings = []

    case = packet.get("case_info", {})
    investigator = packet.get("investigator_info", {})
    authority = packet.get("legal_authority", {})
    scope = packet.get("scope", {})
    evidence_items = packet.get("evidence_items", [])
    attachments = packet.get("attachments", [])
    details = packet.get("request_details", {})

    if not case.get("case_number", "").strip():
        warnings.append("Case Number is blank.")

    if not investigator.get("submitting_investigator", "").strip():
        warnings.append("Submitting Investigator is blank.")

    if not authority.get("authority_type", "").strip():
        warnings.append("Legal authority type is blank.")

    if authority.get("authority_type", "") == "Unknown / Pending":
        warnings.append("Legal authority is marked Unknown / Pending. Confirm agency policy before submission.")

    if not evidence_items:
        warnings.append("No evidence/device items have been added.")

    for index, item in enumerate(evidence_items, start=1):
        item_number = item.get("item_number", "").strip() or str(index).zfill(3)
        evidence_number = item.get("evidence_number", "").strip()
        device_type = item.get("device_or_media_type", "").strip()
        short_description = item.get("short_description", "").strip()
        condition_received = item.get("condition_received", "").strip()
        type_specific = item.get("type_specific", {})

        if not evidence_number:
            warnings.append(f"Evidence item {item_number} does not have an evidence number.")

        if not device_type:
            warnings.append(f"Evidence item {item_number} does not have a device/media type selected.")

        if not short_description:
            warnings.append(f"Evidence item {item_number} does not have a short description.")

        if not condition_received:
            warnings.append(f"Evidence item {item_number} does not have condition received documented.")

        if not isinstance(type_specific, dict):
            warnings.append(f"Evidence item {item_number} has an invalid type-specific field structure.")
        elif device_type and not any(str(value or "").strip() for value in type_specific.values()):
            warnings.append(f"Evidence item {item_number} has a device/media type selected but no type-specific details entered.")

    if not details.get("requested_actions", []):
        warnings.append("No requested forensic actions were selected.")

    if not details.get("investigative_objective", "").strip():
        warnings.append("Investigative Objective / Requested Information is blank.")

    if scope.get("date_range_limited") and not scope.get("authorized_date_range", "").strip():
        warnings.append("Date range limitation is selected, but no authorized date range was entered.")

    if scope.get("specific_apps_limited") and not scope.get("authorized_apps_platforms", "").strip():
        warnings.append("Specific app/platform limitation is selected, but no app/platform was entered.")

    if scope.get("specific_accounts_limited") and not scope.get("authorized_accounts", "").strip():
        warnings.append("Specific account limitation is selected, but no account was entered.")

    if scope.get("keyword_limited") and not scope.get("authorized_keywords", "").strip():
        warnings.append("Keyword limitation is selected, but no keywords were entered.")

    for index, attachment in enumerate(attachments, start=1):
        source_path = attachment.get("source_path", "").strip()
        description = attachment.get("description", "").strip()
        attachment_type = attachment.get("attachment_type", "").strip()

        label = attachment.get("attachment_number", "").strip() or str(index).zfill(3)

        if not attachment_type:
            warnings.append(f"Attachment {label} does not have an attachment type selected.")

        if not source_path:
            warnings.append(f"Attachment {label} does not have a source file path.")
            continue

        path = Path(source_path)

        if not path.exists():
            warnings.append(f"Attachment {label} source file does not exist: {source_path}")
        elif not path.is_file():
            warnings.append(f"Attachment {label} source path is not a file: {source_path}")

        if not description:
            warnings.append(f"Attachment {label} does not have a description.")

    return errors, warnings