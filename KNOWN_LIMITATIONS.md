# Known Limitations - ByteCase Intake v0.9.0

ByteCase Intake v0.9.0 is a release candidate for early testing and feedback.

## Scope limitations

ByteCase Intake does not perform:

- Forensic acquisition
- Mobile extraction
- Computer imaging
- Hashing
- File parsing
- Artifact analysis
- Investigative conclusions
- Legal review
- Evidence management system updates
- Chain-of-custody system updates

It creates request/intake documentation from user-provided information.

## Legal authority and scope

The tool can document legal authority and scope information, but it cannot determine whether a search, extraction, review, or analysis is legally authorized.

Users must follow agency policy, prosecutor/legal advisor guidance, court orders, consent limits, warrants, and applicable law.

## Chain of custody

The submission/handoff section is an intake receipt aid. It does not replace official chain-of-custody records, property/evidence records, evidence management systems, or agency required forms.

## Photos

Physical item photos are copied and cataloged for intake reference. They are not automatically embedded in the DOCX report.

Current photo behavior:

- Photos are copied to item-specific folders when possible.
- Photo records are indexed in TXT, DOCX, and JSON output.
- The tool does not alter, enhance, resize, hash, or analyze photos.
- Native image metadata is not parsed or validated.

## Attachments

Attachments are copied into the exported packet folder when possible. The app does not parse, validate, convert, redact, or combine attachment files.

## DOCX output

DOCX output is generated using `python-docx`. Very large packets, long tables, or unusually long field values may require manual formatting cleanup in Microsoft Word or compatible software.

## Theme limitations

The app themes Tkinter/ttk widgets where the framework permits. Native operating-system dialogs, such as file picker dialogs and message boxes, may not fully follow the ByteCase dark/light theme.

## Unsigned executable

The Windows executable is not yet code-signed. Windows SmartScreen or endpoint protection tools may display unknown-publisher warnings.

## No database or multi-user workflow

This release writes local packet folders and files. It does not include:

- Shared database
- Multi-user review
- Role-based access control
- Audit log
- Case queue
- Network synchronization
- Cloud sync

## Backward compatibility

The JSON schema is still pre-v1.0. Future releases may change the schema before v1.0.

## Recommended use

Use this release for testing, workflow feedback, packet review, and documentation design validation before operational adoption.
