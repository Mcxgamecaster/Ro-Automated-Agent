import pytest

np = pytest.importorskip("numpy")
cv2 = pytest.importorskip("cv2")

from hk3_bot.vision.scaling import multi_scale_match


def test_multi_scale_match_finds_scaled_template():
    canvas = np.zeros((200, 200, 3), dtype=np.uint8)
    canvas[80:120, 80:120] = 255
    template = np.ones((20, 20, 3), dtype=np.uint8) * 255
    result = multi_scale_match(canvas, template, scales=[1.0, 2.0], threshold=0.8)
    assert result["found"]
    x, y, w, h = result["bbox"]
    assert (80 <= x <= 120) and (80 <= y <= 120)
    assert w in (20, 40)
    assert h in (20, 40)
