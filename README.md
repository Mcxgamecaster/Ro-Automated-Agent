# Ro-Automated-Agent

Windows-only, OS-level automation toolkit for the Roblox title **Humankind 3**. The bot captures the Roblox window, interprets UI pixels, and emits keyboard/mouse input without injection, memory reads, or network tampering.

## Safety & Terms of Use
- Operates strictly through screen capture + OS input (pywin32, dxcam/mss, pynput); no DLL injection or process hooks.
- Enforces bounds clamping, configurable focus guard, global rate limits, and an F8 kill-switch (immediate stop) for every action.
- Assist mode requires explicit confirmation for risky actions (e.g., purchases) before execution.

## Project Layout
```
configs/              # YAML config profiles and ROI definitions
assets/templates/     # Anchor + UI template images for OpenCV matching
src/hk3_bot/          # Core bot modules (windowing, capture, vision, control)
  controller/         # High- and low-level planners/executors
  vision/             # Template, anchor, scaling, annotation, OCR helpers
logs/                 # Rotating logs
debug/                # Latest annotated frames, ROI crops, state.json
HumankindApp/         # Optional WPF utility to launch calibration (Windows)
```

Key entry points:
- `python -m hk3_bot.run` – main agent runner.
- `python -m hk3_bot.calibration` – live calibration/tooling for ROIs + templates.
- `HumankindApp/MainWindow.xaml(.cs)` – simple WPF wrapper to start/stop calibration from a GUI.

## Prerequisites
- Windows 10/11, Python 3.11 (64-bit) with build tools for native deps.
- Roblox must stay windowed and focused while automation is active.
- Optional: Tesseract installed and on PATH to enable OCR; the bot still runs without it.

## Setup
1. Clone the repo and open a **Developer Command Prompt** or PowerShell on Windows.
2. Create & activate a virtual environment (recommended):
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. Install dependencies:
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. Ensure template PNGs exist under `assets/templates/` (collect via calibration).

## Configuration
Edit `configs/humankind3.yaml` (JSON-compatible YAML). Important sections:
- `window_patterns`: list of title/class substrings or regex to find the Roblox HWND.
- `profiles`: per-layout settings (`windowed`, `fullscreen`, etc.) with FPS, focus guard, ROIs, anchors, and risky templates.
- `default_scales`: scale pyramid for template matching.

Example (windowed profile excerpt):
```yaml
window_patterns:
  - contains: "Roblox"
profiles:
  windowed:
    strict_focus: true
    fps: 10
    anchors:
      TechTreeHeader: {file: TechTreeHeader.png, threshold: 0.8}
      ShopHeader: {file: ShopHeader.png, threshold: 0.8}
      CloseX: {file: CloseX.png, threshold: 0.85}
    rois:
      minimap: {x: 0.8, y: 0.75, w: 0.18, h: 0.22}
      counters: {x: 0.8, y: 0.05, w: 0.18, h: 0.12}
      center_screen: {x: 0.4, y: 0.4, w: 0.2, h: 0.2}
    risky_templates: [PurchaseButton, BuyPackButton]
```
- ROIs default to relative coordinates (0..1). Anchored ROIs can be defined relative to a detected anchor bounding box for UI scale/position drift.

## Running the Agent
```powershell
python -m hk3_bot.run --config configs/humankind3.yaml --profile windowed --assist --debug
```
Common flags:
- `--profile`: select a profile from the config (e.g., `windowed`, `fullscreen`).
- `--assist`: require confirmation for risky plans/actions.
- `--debug`: dump latest capture to `debug/latest_full.png` and `debug/state.json`.
- `--fps`: override capture rate.
- `--planner rules|stub`: rule-based or JSON stub planner.
- `--dry-run`: plan without emitting input.

Behavior highlights:
- Each loop re-validates the Roblox window, client rect, focus, and anchors before acting.
- Mouse coordinates are clamped to the current client rect; global rate limiting throttles inputs.
- F8 kill-switch stops all actions immediately.

## Calibration & Templates
CLI calibration (interactive OpenCV window):
```powershell
python -m hk3_bot.calibration --config configs/humankind3.yaml --profile windowed
```
- Drag to define relative ROIs; anchored ROIs can be offset from selected anchor templates.
- Save cropped templates to `assets/templates/NAME.png` for anchor/UI detection.
- Persist ROIs/templates back into the YAML profile.

WPF helper (Windows): open `HumankindApp.sln` in Visual Studio or run `dotnet build` and launch `HumankindApp.exe`. The GUI starts/stops the same calibration command and streams stdout/stderr to the window.

## Troubleshooting
- **Roblox window not detected**: verify the title substring/regex in `window_patterns` matches the current window title.
- **Black/blank captures**: install GPU drivers and `dxcam`; if unavailable, the code falls back to `mss` automatically.
- **Focus guard blocking actions**: disable `strict_focus` in the chosen profile (less safe) or ensure the Roblox window remains active.
- **Template misses**: adjust `threshold` per anchor/template and expand `default_scales` for multi-scale matches.
- **Kill immediately**: press **F8** to engage the kill switch; restart the process to clear it.

## Testing
Run the pytest suite (ROI math, clamping, template matching):
```powershell
pytest
```

## Notes on responsible use
This project is for educational prototyping. Respect Roblox Terms of Service and game community rules. Avoid disruptive automation, and prefer assist mode with manual confirmation for any in-game spending.
