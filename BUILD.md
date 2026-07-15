# Build Guide - ByteCase Intake

This document describes how to build a Windows release package for ByteCase Intake.

## Build target

```text
ByteCase Intake v0.9.0 Release Candidate
```

## Prerequisites

- Windows 10 or Windows 11
- Python 3.10+
- PowerShell
- Project dependencies installed from `requirements.txt`
- PyInstaller installed in the active Python environment

Install runtime dependencies:

```powershell
py -m pip install -r requirements.txt
```

Install PyInstaller:

```powershell
py -m pip install pyinstaller
```

## Build command

From the repository root:

```powershell
.\build_release.ps1
```

The script will:

1. Confirm required files exist.
2. Remove old `build` and `dist` folders.
3. Run PyInstaller with `ByteCase_Intake.spec`.
4. Create a release folder.
5. Copy the executable and documentation.
6. Generate a SHA-256 checksum for the executable.
7. Create a ZIP archive.
8. Generate a SHA-256 checksum for the ZIP.

## Expected output

```text
dist\release\
  ByteCase_Intake_v0.9.0\
    ByteCase_Intake.exe
    README.md
    BUILD.md
    DEPENDENCIES.md
    KNOWN_LIMITATIONS.md
    RELEASE_CHECKLIST.md
    RELEASE_NOTES_v0.9.0.md
    settings.example.json
    ByteCase_Intake.exe.sha256
  ByteCase_Intake_v0.9.0.zip
  ByteCase_Intake_v0.9.0.zip.sha256
```

## Unsigned Windows executable warning

Until the application is code-signed, Windows SmartScreen and antivirus products may warn users that the executable is from an unknown publisher. That is expected for unsigned first-release Windows tools.

For release notes, clearly state:

```text
This Windows executable is not yet code-signed. Windows may display an unknown publisher warning.
```

## Clean build tips

If the build behaves oddly:

```powershell
Remove-Item -Recurse -Force .\build, .\dist -ErrorAction SilentlyContinue
py -m pip install --upgrade pyinstaller
.\build_release.ps1
```

## Source run test

Before packaging, run:

```powershell
py .\main.py
```

Test dark, light, and system themes before building the executable.
