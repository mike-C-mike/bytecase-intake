# ByteCase Intake

**Digital Forensics Request Builder**  
Part of the **ByteCase** toolset by **Forensics Byte**  
Product domain: `byte-case.com`

ByteCase Intake is a desktop application for building structured digital forensics intake/request packets. It helps investigators and examiners document case details, legal authority, scope, submitted evidence items, supporting attachments, physical item photos, peripherals/accessories, priority, and submission/handoff information before forensic work begins.

## Current release

```text
ByteCase Intake v0.9.0 Release Candidate
```

This release candidate is intended for early testing, feedback, and workflow validation.

## What this tool does

ByteCase Intake helps create a packet containing:

- Case and submitting investigator information
- Legal authority and scope information
- Requested forensic actions
- Evidence/device item descriptions
- Device/media-specific item fields
- Physical item photo cataloging
- Peripherals/accessories lists
- Supporting document attachment index
- Submission and handoff receipt information
- TXT, DOCX, and JSON outputs
- Copied attachments and copied item photos in organized folders

## What this tool does not do

ByteCase Intake does **not** perform forensic acquisition, extraction, hashing, parsing, artifact analysis, legal review, or investigative conclusions.

It creates a structured request and intake packet from user-provided information. Legal authority, scope, agency policy, evidence handling, and chain-of-custody requirements remain the responsibility of the user and their agency.

ByteCase Intake does not replace:

- Official evidence management systems
- Official chain-of-custody records
- Property/evidence room records
- Legal review processes
- Forensic examination reports
- Agency policy requirements

## Default output structure

By default, ByteCase Intake writes to a local ByteCase folder under the current user's profile:

```text
C:\Users\<currentuser>\ByteCase\<case_number>\intake\
```

Example:

```text
C:\Users\Matt\ByteCase\26001234\intake\
  26001234_2026-07-15_14-30-00_bytecase_intake.txt
  26001234_2026-07-15_14-30-00_bytecase_intake.docx
  26001234_2026-07-15_14-30-00_bytecase_intake.json
  attachments\
  items\
    item_001_mobile_phone\
      photos\
        front_001.jpg
        back_001.jpg
        serial_identifier_001.jpg
```

A custom ByteCase output root can be set in **Settings**. When a custom root is selected, case folders are created directly inside that custom root:

```text
<custom_output_root>\<case_number>\intake\
```

The app does not add an extra `ByteCase` folder inside a custom root.

## Themes

ByteCase Intake supports:

- Dark
- Light
- System Default

The visual theme is based on the ByteCase desktop design system using deep blue, charcoal, cool gray, and emerald green. The selected preference is saved in `settings.json`.

To switch themes:

```text
Settings -> Appearance -> Theme
```

Some operating-system-controlled dialogs, such as native file pickers and message boxes, may not fully follow the app theme because they are controlled by the OS and Tkinter runtime.

## Installation from source

Recommended Python version:

```text
Python 3.10+
```

Install dependencies:

```powershell
py -m pip install -r requirements.txt
```

Run from source:

```powershell
py .\main.py
```

## Packaging

Packaging instructions are in:

```text
BUILD.md
```

The project includes a PyInstaller spec and PowerShell build script for Windows release builds.

## Dependencies and licensing

Dependency and license notes are in:

```text
DEPENDENCIES.md
```

No new third-party dependency was added for the ByteCase visual theme system or item photo cataloging.

## Known limitations

Known limitations are tracked in:

```text
KNOWN_LIMITATIONS.md
```

## Release checklist

Before publishing a release, complete:

```text
RELEASE_CHECKLIST.md
```

## Suggested GitHub topics

```text
digital-forensics
dfir
forensics
evidence
law-enforcement
documentation
python
tkinter
bytecase
forensics-byte
```

## License

Use the repository license file for the governing project license. Dependency licenses are documented separately in `DEPENDENCIES.md`.
