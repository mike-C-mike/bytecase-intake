# Release Checklist - ByteCase Intake v0.9.0

Complete this checklist before publishing the GitHub release.

## Version checks

- [ ] `APP_VERSION` is `0.9.0` in `settings_service.py`.
- [ ] `SCHEMA_VERSION` is `0.9` in `request_core.py`.
- [ ] README references `v0.9.0`.
- [ ] Release notes reference `v0.9.0`.

## Source run checks

- [ ] `py .\main.py` launches successfully.
- [ ] App title shows `ByteCase Intake v0.9.0`.
- [ ] About window opens and shows ByteCase / Forensics Byte attribution.
- [ ] Settings window opens.
- [ ] Theme can be changed to Dark.
- [ ] Theme can be changed to Light.
- [ ] Theme can be changed to System Default.
- [ ] Settings save and reload after restart.

## Functional checks

- [ ] Create a packet with one mobile phone item.
- [ ] Add at least one item photo.
- [ ] Add at least one peripheral/accessory.
- [ ] Add at least one supporting attachment.
- [ ] Select requested forensic actions.
- [ ] Add legal authority and scope information.
- [ ] Add priority/handoff information.
- [ ] Review window opens.
- [ ] Validation warnings are readable and useful.
- [ ] Export completes without error.

## Output checks

- [ ] Default output path creates `C:\Users\<user>\ByteCase\<case_number>\intake\`.
- [ ] Custom output root creates `<custom_root>\<case_number>\intake\`.
- [ ] TXT output is created.
- [ ] DOCX output is created.
- [ ] JSON output is created.
- [ ] Attachments are copied into `attachments\`.
- [ ] Item photos are copied into `items\item_<number>_<type>\photos\`.
- [ ] JSON contains item photo records.
- [ ] JSON contains peripheral/accessory records.
- [ ] TXT and DOCX include photo indexes.
- [ ] TXT and DOCX include peripheral/accessory sections.

## Theme/readability checks

- [ ] Light mode table headers are readable.
- [ ] Dark mode table headers are readable.
- [ ] Tab hover does not make text unreadable.
- [ ] Selected tabs are readable.
- [ ] Selected table rows are readable.
- [ ] Disabled controls remain legible.
- [ ] Buttons have visible hover/focus states.
- [ ] Text boxes are readable.
- [ ] Scrollbars are usable.
- [ ] Status text is not color-only.

## Build checks

- [ ] `py -m pip install -r requirements.txt` completes.
- [ ] `py -m pip install pyinstaller` completes.
- [ ] `.\build_release.ps1` completes.
- [ ] EXE launches from release folder.
- [ ] EXE can export a packet.
- [ ] EXE ZIP is created.
- [ ] EXE SHA-256 checksum is created.
- [ ] ZIP SHA-256 checksum is created.

## GitHub checks

- [ ] Repository description is current.
- [ ] Topics are current.
- [ ] README is current.
- [ ] License file exists.
- [ ] Release ZIP uploaded.
- [ ] ZIP checksum uploaded or included.
- [ ] Release notes include unsigned executable warning.
- [ ] Release notes include known limitations.

## Post-release checks

- [ ] Download release ZIP from GitHub.
- [ ] Verify ZIP checksum.
- [ ] Extract ZIP.
- [ ] Run EXE.
- [ ] Confirm release notes and docs are included.
