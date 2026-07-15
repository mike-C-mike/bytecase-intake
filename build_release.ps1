$ErrorActionPreference = "Stop"

$AppName = "ByteCase_Intake"
$Version = "0.9.0"
$ReleaseName = "$AppName`_v$Version"
$ReleaseRoot = Join-Path "dist" "release"
$ReleaseDir = Join-Path $ReleaseRoot $ReleaseName
$ZipPath = Join-Path $ReleaseRoot "$ReleaseName.zip"

$RequiredFiles = @(
    "main.py",
    "gui.py",
    "settings_service.py",
    "bytecase_theme.py",
    "request_core.py",
    "docx_exporter.py",
    "validators.py",
    "requirements.txt",
    "README.md",
    "BUILD.md",
    "DEPENDENCIES.md",
    "KNOWN_LIMITATIONS.md",
    "RELEASE_CHECKLIST.md",
    "RELEASE_NOTES_v0.9.0.md",
    "settings.example.json",
    "ByteCase_Intake.spec"
)

Write-Host "ByteCase Intake release build v$Version"
Write-Host "Checking required files..."

foreach ($File in $RequiredFiles) {
    if (-not (Test-Path $File)) {
        throw "Required file missing: $File"
    }
}

Write-Host "Cleaning old build artifacts..."
Remove-Item -Recurse -Force "build" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "dist" -ErrorAction SilentlyContinue

Write-Host "Running PyInstaller..."
py -m PyInstaller --clean --noconfirm "ByteCase_Intake.spec"

$ExePath = Join-Path "dist" "$AppName.exe"
if (-not (Test-Path $ExePath)) {
    throw "Build failed. Executable not found: $ExePath"
}

Write-Host "Creating release folder..."
New-Item -ItemType Directory -Force -Path $ReleaseDir | Out-Null

Copy-Item $ExePath $ReleaseDir
Copy-Item "README.md" $ReleaseDir
Copy-Item "BUILD.md" $ReleaseDir
Copy-Item "DEPENDENCIES.md" $ReleaseDir
Copy-Item "KNOWN_LIMITATIONS.md" $ReleaseDir
Copy-Item "RELEASE_CHECKLIST.md" $ReleaseDir
Copy-Item "RELEASE_NOTES_v0.9.0.md" $ReleaseDir
Copy-Item "settings.example.json" $ReleaseDir

if (Test-Path "LICENSE") {
    Copy-Item "LICENSE" $ReleaseDir
}

Write-Host "Generating executable SHA-256 checksum..."
$ReleaseExe = Join-Path $ReleaseDir "$AppName.exe"
$ExeHash = Get-FileHash -Algorithm SHA256 $ReleaseExe
$ExeHashLine = "$($ExeHash.Hash)  $AppName.exe"
$ExeHashLine | Out-File -Encoding ascii (Join-Path $ReleaseDir "$AppName.exe.sha256")

Write-Host "Creating ZIP archive..."
if (Test-Path $ZipPath) {
    Remove-Item -Force $ZipPath
}
Compress-Archive -Path (Join-Path $ReleaseDir "*") -DestinationPath $ZipPath

Write-Host "Generating ZIP SHA-256 checksum..."
$ZipHash = Get-FileHash -Algorithm SHA256 $ZipPath
$ZipHashLine = "$($ZipHash.Hash)  $ReleaseName.zip"
$ZipHashLine | Out-File -Encoding ascii "$ZipPath.sha256"

Write-Host ""
Write-Host "Release build complete."
Write-Host "Release folder: $ReleaseDir"
Write-Host "Release ZIP:    $ZipPath"
Write-Host "ZIP checksum:   $ZipPath.sha256"
