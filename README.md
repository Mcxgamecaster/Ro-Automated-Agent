# HK3 OS-level Automation Bot

> Safety note: this project only uses OS-level input and screen capture. It does **not** inject into Roblox, read memory, alter network traffic, or use exploits.

## Features
- Window discovery via configurable title/class patterns.
- DXCam (preferred) or MSS capture of the Roblox client area each loop.
- Relative and anchor-based ROIs with multi-profile YAML config.
- Multi-scale template matching plus optional OCR for text counters.
- Safety guardrails: focus requirement, bounds clamping, rate limits, risky-action confirmations, and an F8 kill switch.
- Debug dumps (annotated captures and state JSON) and a calibration preview tool.

## Quickstart
1. Install Python 3.11 and dependencies (`pip install -r requirements.txt`).
2. Launch Roblox in **windowed** mode.
3. Calibrate and collect templates:
   - `python -m hk3_bot.calibration --config configs/humankind3.yaml --profile windowed`
   - Capture anchors like headers and close buttons into `assets/templates/`.
4. Dry-run the bot to validate detection:
   - `python -m hk3_bot.run --config configs/humankind3.yaml --profile windowed --debug --dry-run`
5. Enable assist mode for any purchase/spend paths:
   - `python -m hk3_bot.run --config configs/humankind3.yaml --profile windowed --assist`

## Keeping UI Stable
- Use a consistent Roblox UI scale when possible; anchors help recover when scale shifts.
- Keep the Roblox window visible and focused; strict focus blocks inputs when unfocused.
- If captures are black, switch to the MSS fallback by uninstalling DXCam.

## Kill Switch
Press **F8** at any time to stop automation. All input primitives respect the kill-switch flag.

## Troubleshooting
- **Roblox window not detected:** adjust `window_patterns` in `configs/humankind3.yaml`.
- **Black screen capture:** try the MSS fallback; ensure the window is on the primary monitor.
- **Focus guard blocks actions:** disable `strict_focus` in the selected profile (not recommended) or keep the Roblox window active.
- **Template misses:** tune thresholds/scales in the config and recapture templates with cleaner crops.

