# refrag-launcher

A minimal CLI to launch and close [Refrag](https://play.refrag.gg) CS2 servers from your terminal — no browser needed.

## Requirements

- Python 3.11+
- A Refrag account

## Installation

```bash
git clone https://github.com/your-username/refrag-launcher.git
cd refrag-launcher
```

The `refrag` command is now available inside the virtual environment.

### Make `refrag` available everywhere (outside the venv)

**Option A — install with your system Python (simplest):**

```bash
pip install -e .
```

Run this without activating the venv. pip will place `refrag` in your system Python's scripts folder, which is already on your PATH.

**Option B — in a venv, then added to PATH permanently:**
```bash
python -m venv .venv

.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

pip install -e .
```


On **Windows** (PowerShell, run once):
```powershell
$p = "$PWD\.venv\Scripts"
[Environment]::SetEnvironmentVariable("PATH", "$([Environment]::GetEnvironmentVariable('PATH','User'));$p", "User")
```

On **macOS / Linux** (add to `~/.bashrc` or `~/.zshrc`):
```bash
export PATH="$PATH:/path/to/refrag-launcher/.venv/bin"
```

Then open a new terminal — `refrag` will work from anywhere.

## Configuration

Create a `.env` file at the root of the project:

```
MAIL=your@email.com
PASSWORD=yourpassword
```

## Usage

```bash
# Start a server (defaults: de_dust2, nadr mod)
refrag

# Start with a specific map and mod (no need to write de_ for maps)
refrag --map inferno --mod nadr
refrag --map de_mirage --mod retakes
```

## Notes

- The connect string (e.g. `connect 1.2.3.4:27015; password abc`) is automatically copied to your clipboard when the server is ready. Paste it directly into your CS2 console.
- `TEAM_ID` and `LOCATION_ID` in `launch_refrag.py` may need to be adjusted to match your Refrag account. (LOCATION_ID is defaulted to 27 (Paris)).
