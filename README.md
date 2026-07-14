# Digital Forensics Request Builder

Digital Forensics Request Builder helps investigators create a clear, scoped digital forensic request packet before forensic work begins.

Current version: **v0.4.0**

## Purpose

This tool is intended for investigator-side request documentation. It helps capture what is being submitted, what is being requested, the legal authority or scope information provided, and the basic handoff details for a digital forensic request.

It is part of the Forensics Byte toolset.

## What v0.2.0 Includes

- Case and agency information
- Submitting investigator information
- Single evidence/device item section
- Legal authority section
- Requested forensic action checkboxes
- Investigative objective text area
- Known facts/context for examiner text area
- Scope notes text area
- Priority and urgency flags
- Submission/handoff notes
- Optional acknowledgement/signature block
- Review-before-export workflow
- TXT export
- DOCX export
- JSON export
- Basic settings
- Optional DOCX branding image
- Dark/light theme

## Output Files

Each export creates:

```text
TXT request packet
DOCX request packet
JSON structured request packet
```

The JSON output is designed to become the bridge for future Forensics Byte integration, such as importing request information into the Acquisition Packet Generator.

# README update for v0.4.0

Update the current version section to:

```text
v0.4.0
```

Add these feature bullets under Core Features:

- Dark and light mode setting
- Multi-item evidence/device support
- Legal authority and scope builder
- Scope limitation fields for date ranges, apps/platforms, accounts, and keywords
- Scope validation warnings before export

Update the output list if needed:

- TXT request packet
- DOCX request packet
- JSON saved request packet

Add this scope note:

```text
The legal authority and scope fields are documentation aids only. They help investigators describe the basis and scope of a request, but they do not provide legal advice or decide whether a search is authorized. Agencies should follow their own policy, prosecutor guidance, and applicable law.

## Scope Boundary

This tool does not perform acquisition, extraction, hashing, evidence analysis, artifact parsing, or investigative conclusions.

It documents information provided for a digital forensic request.

## Important Legal / Policy Note

This tool is not legal advice and does not decide whether a search, extraction, or review is legally authorized.

Agencies should review workflows, forms, language, and templates with their own policy authority, legal advisor, prosecutor, or command staff before operational use.

## Dependency Note

Runtime dependencies:

- Python standard library
- Tkinter
- python-docx

`python-docx` is used for DOCX report generation and is distributed under the MIT License.

## Run From Source

Install dependencies:

```powershell
py -m pip install -r requirements.txt
```

Run:

```powershell
py .\main.py
```

## Suggested Workflow

```text
1. Enter case and investigator information.
2. Enter the evidence/device item.
3. Select legal authority and requested forensic actions.
4. Describe what the investigator is looking for.
5. Add known facts, scope notes, and priority details.
6. Review the request.
7. Export TXT, DOCX, and JSON outputs.
```

## Roadmap

Planned future versions:

```text
v0.3.0 - Multi-item evidence support
v0.4.0 - Legal authority and scope builder
v0.5.0 - Attachment index and export folder
v0.6.0 - Submission / chain-of-custody handoff section
v0.7.0 - Consent form template packaging
v0.8.0 - Settings, agency profile, packaging docs
v0.9.0 - GitHub pre-release candidate
```
