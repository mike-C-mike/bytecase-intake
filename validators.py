def validate_request_for_export(packet):
    errors = []
    warnings = []

    case = packet.get("case_info", {})
    investigator = packet.get("investigator_info", {})
    authority = packet.get("legal_authority", {})
    scope = packet.get("scope", {})
    evidence_items = packet.get("evidence_items", [])
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

    return errors, warnings