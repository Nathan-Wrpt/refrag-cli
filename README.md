# refrag-launcher

A minimal Windows CLI to launch [Refrag](https://play.refrag.gg) CS2 servers from a terminal. When the server is ready, it copies the connect command to the clipboard.

## Requirements

- Windows
- Python 3.9 or newer (not required when using the prebuilt executable)
- A Refrag account with permission to start servers

## Installation

Clone the project, then from its directory run these commands in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

## Configuration

Create a `.env` file at the root of the project (next to `launch_refrag.py`):

```
MAIL=your@email.com
PASSWORD=yourpassword
TEAM_ID="your_team_id"
LOCATION_ID=27
```
Find `TEAM_ID` in your Refrag dashboard URL, for example `https://play.refrag.gg/dashboard/team/12345`.

`LOCATION_ID` defaults to `27` (Paris). Change it if you use another server location.
## Usage

```bash
# Start a server (defaults: de_dust2, nadr mod)
refrag

# Start with a specific map and mod
refrag --map inferno --mod nadr
refrag --map de_mirage --mod retakes
```

Map names can be given with or without the `de_` prefix. The defaults are `de_dust2` and `nadr`.

## Build the Windows executable

Create the `.env` file before building. From PowerShell, run:

```powershell
python -m PyInstaller --onefile --console --name launch_refrag --add-data ".env;." --runtime-hook hook.py launch_refrag.py
```

The executable will be created at `dist\launch_refrag.exe`. It uses the `.env` values that were present when it was built; rebuild it if you change those values.

> [!WARNING]
> The `.env` file, including your credentials, is bundled into the executable. Do not share the executable.

## Notes

- Paste the copied connect command (for example, `connect 1.2.3.4:27015; password abc`) into your CS2 console.
