# Ro-Automated-Agent

This repository now includes a small Windows-only WPF companion app that wraps the Humankind automation Python commands behind a modern UI. Use it to launch `hk3_bot.calibration` without relying on the console.

## Fixing the `ModuleNotFoundError: No module named 'hk3_bot'`
1. Open a terminal in the HumankindWare project folder (where `configs/` lives).
2. Make sure the Python environment has the project installed. If the repo contains a `setup.py` or `pyproject.toml`, run:
   ```bash
   python -m pip install -e .
   ```
   Otherwise ensure that the project folder is on `PYTHONPATH` (for PowerShell):
   ```powershell
   $env:PYTHONPATH = "$PWD" + ';' + $env:PYTHONPATH
   ```
3. Re-run the command:
   ```powershell
   python -m hk3_bot.calibration --config configs/humankind3.yaml --profile windowed
   ```
   If the module still cannot be found, verify the working directory is the same folder that contains the `hk3_bot` package.

## WPF launcher
The `HumankindApp` project provides a stylized launcher for calibration:
- Fields for the config file, profile, and Python executable path.
- Start/Stop buttons to control the background process.
- Live log output from stdout and stderr.

### Building and running (Windows 10/11)
1. Install the [.NET 8 SDK](https://dotnet.microsoft.com/download) with desktop workloads.
2. Open `HumankindApp/HumankindApp.csproj` in Visual Studio 2022 (or run `dotnet build HumankindApp/HumankindApp.csproj` on Windows).
3. Press **F5** to run. When launched:
   - Set **Config file** to the path of `humankind3.yaml`.
   - Set **Profile** (e.g., `windowed`).
   - Set **Python executable** to `python` or the full path to your Python 3.12 interpreter.
   - Click **Start calibration** to execute `python -m hk3_bot.calibration --config "<config>" --profile <profile>`.

> The launcher expects the Python environment to already resolve the `hk3_bot` module. Use the steps above to fix the module path before running.
