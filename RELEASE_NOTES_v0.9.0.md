# ByteCase Intake v0.9.0 Release Candidate

ByteCase Intake is a digital forensics request builder for creating structured intake packets with case details, legal authority, scope, evidence items, attachments, physical item photo indexes, peripherals/accessories, and submission/handoff documentation.

This is a release-candidate build intended for early testing and workflow feedback.

## Highlights

- ByteCase branding and `byte-case.com` attribution
- Shared ByteCase output structure
- Dark, Light, and System Default themes
- Device/media-specific evidence item templates
- Physical item photo cataloging
- Peripherals/accessories list per physical item
- Supporting document attachment index
- Expanded submission/handoff receipt fields
- TXT, DOCX, and JSON output
- Organized export folders under each case number

## Default output structure

```text
C:\Users\<currentuser>\ByteCase\<case_number>\intake\
```

Example:

```text
ByteCase\26001234\intake\
  26001234_2026-07-15_14-30-00_bytecase_intake.txt
  26001234_2026-07-15_14-30-00_bytecase_intake.docx
  26001234_2026-07-15_14-30-00_bytecase_intake.json
  attachments\
  items\
    item_001_mobile_phone\
      photos\
        front_001.jpg
```

## Important scope note

ByteCase Intake does not perform forensic acquisition, extraction, hashing, parsing, artifact analysis, legal review, or investigative conclusions.

It creates a structured request and intake packet from user-provided information. It does not replace agency evidence systems, property records, official chain-of-custody records, legal review, or forensic examination reports.

## Unsigned Windows executable warning

This Windows executable is not yet code-signed. Windows may display an unknown publisher warning or SmartScreen message. That is expected for this release candidate.

## Known limitations

See `KNOWN_LIMITATIONS.md` for full details.

## Verification

Release packages include SHA-256 checksums. After download, compare the provided checksum with the downloaded file before use.
