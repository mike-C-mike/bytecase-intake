# Dependencies - ByteCase Intake

This document tracks third-party dependencies and packaging tools used by ByteCase Intake.

## Runtime dependencies

### Python standard library

ByteCase Intake uses Python standard-library modules including `json`, `os`, `pathlib`, `shutil`, `datetime`, `copy`, `sys`, `tkinter`, and related Tkinter/ttk modules.

License notes:

- Python uses the Python Software Foundation License.
- Tkinter ships with Python and uses Tcl/Tk components.

### python-docx

Purpose:

```text
Generate Microsoft Word DOCX request packet output.
```

License:

```text
MIT License
```

Notes:

- `python-docx` is the only current third-party runtime dependency.
- The project should continue avoiding new dependencies unless there is a clear feature need and license/package impact review.

## Packaging dependency

### PyInstaller

Purpose:

```text
Build a standalone Windows executable for release distribution.
```

License notes:

- PyInstaller is distributed under GPL terms with an exception that allows bundling applications, including commercial applications, from your source code.
- Generated executable bundles can be shipped under the license selected for your own source code, subject to dependency licenses.

PyInstaller is a build/packaging tool, not a runtime feature of the application source.

## Dependency policy for ByteCase tools

Before adding dependencies:

1. Confirm the license.
2. Prefer MIT, BSD, Apache-2.0, PSF, or similarly permissive licenses.
3. Avoid AGPL, strong copyleft, non-commercial, source-available-only, unknown, or unclear licensing without a deliberate decision.
4. Consider Windows packaging impact.
5. Consider long-term maintenance and forensic defensibility.
6. Document the dependency in this file.

## Current dependency summary

```text
python-docx: MIT
PyInstaller: GPL with bootloader/commercial-use exception for packaging
Python/Tkinter: Python standard library / Tcl-Tk components
```
