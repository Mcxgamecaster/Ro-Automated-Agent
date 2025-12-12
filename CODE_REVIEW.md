# Code Review Summary

## Overall impression
The repository captures the requested layout and basic stubs but currently implements only a minimal subset of the originally requested automation behaviors. Core safety, perception, planning, and calibration flows are present as placeholders rather than production-ready logic.

## Critical gaps vs. original requirements
- **Calibration tool is just a frame viewer.** `hk3_bot.calibration` opens the window and displays frames but offers no ROI drawing, template capture, or YAML persistence, so it cannot meet the calibration workflow described in the prompt. 【F:src/hk3_bot/calibration.py†L17-L31】
- **Safety and assist modes are incomplete.** Safety checks clamp points and rate-limit clicks but do not implement risky-action confirmation or broader rate limits (e.g., mouse px/sec), and actions run even when risky templates are configured. 【F:src/hk3_bot/safety.py†L13-L52】【F:src/hk3_bot/actions.py†L24-L83】
- **Anchored ROI handling isn’t wired into runtime.** While anchored ROI types and helpers exist, the main loop never resolves ROIs against detected anchors or uses them to drive perception/actions, so anchor detection cannot influence behavior. 【F:src/hk3_bot/config.py†L64-L153】【F:src/hk3_bot/vision/anchors.py†L12-L57】【F:src/hk3_bot/run.py†L62-L87】
- **Planner/controller logic is minimal.** The rule-based planner only clicks a `CloseX` anchor when seen and does not implement higher-level tech tree/shop behaviors or recovery flows. There is no validation of action schemas or assist-mode prompts beyond a single flag check. 【F:src/hk3_bot/controller/high_level.py†L12-L31】【F:src/hk3_bot/run.py†L77-L84】
- **Capture loop lacks robustness.** The runner locates the Roblox window once and exits if a frame is missing; it does not retry window discovery or handle resizing/movement beyond periodic rect refresh. 【F:src/hk3_bot/run.py†L44-L87】

## Notable positives
- Safety guardrails (focus check, kill switch, point clamping, click cooldown) are present in the action layer to prevent out-of-bounds input. 【F:src/hk3_bot/safety.py†L23-L47】【F:src/hk3_bot/actions.py†L21-L71】
- Multi-scale template matching and anchor detection scaffolding are in place, matching the requested APIs for future expansion. 【F:src/hk3_bot/vision/scaling.py†L13-L35】【F:src/hk3_bot/vision/anchors.py†L12-L33】
- The WPF helper cleanly wraps the calibration CLI, streaming stdout/stderr and offering stop/start controls with basic validation. 【F:HumankindApp/MainWindow.xaml.cs†L27-L139】

## Recommendations
1. Implement full calibration UX (ROI drawing, template capture, YAML updates) so profiles and anchors can be authoritatively produced from the UI.
2. Extend safety/assist to respect risky templates and mouse speed caps, and require confirmations for flagged actions before execution.
3. Wire anchored ROI resolution into the capture/vision pipeline and use detected anchors to drive UI-mode inference and planner logic.
4. Expand the rule-based planner and low-level executor to include recovery behaviors, schema validation, and verification steps between actions.
5. Harden the main loop with window re-discovery, client-rect validation each iteration, and fallback capture strategies when dxcam/mss are unavailable.

## Test status
- Current suite only covers ROI math and click clamping; all three tests pass (one skipped) on the existing codebase. 【F:tests/test_bounds.py†L1-L29】【F:tests/test_roi.py†L1-L58】【7faf74†L1-L9】
