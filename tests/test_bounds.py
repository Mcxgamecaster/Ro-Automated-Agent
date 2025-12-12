from hk3_bot.safety import SafetyContext


def test_click_clamp():
    ctx = SafetyContext(hwnd=None, strict_focus=False, client_rect=(0, 0, 100, 100))
    clamped = ctx.clamp_point(150, -10)
    assert clamped == (99, 0)
