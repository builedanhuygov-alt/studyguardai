; Inno Setup script for StudyGuard AI.
; Build (after PyInstaller): iscc packaging\windows\installer.iss

#define AppName "StudyGuard AI"
#define AppVersion "0.1.0"
#define AppPublisher "StudyGuard AI contributors"
#define AppExe "StudyGuardAI.exe"

[Setup]
AppId=5F2C1B84-9E2A-4C77-8E2D-STUDYGUARDAI
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\StudyGuardAI
DefaultGroupName=StudyGuard AI
OutputDir=..\..\release
OutputBaseFilename=StudyGuardAI-Setup-{#AppVersion}
SetupIconFile=..\..\desktop\assets\icon.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=lowest

[Files]
Source: "..\..\dist\StudyGuardAI\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\StudyGuard AI"; Filename: "{app}\{#AppExe}"
Name: "{userdesktop}\StudyGuard AI"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\{#AppExe}"; Description: "Launch StudyGuard AI"; Flags: nowait postinstall skipifsilent
