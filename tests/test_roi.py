from hk3_bot.config import AnchoredROI, RelativeROI
from hk3_bot.vision.anchors import resolve_anchored_roi


def test_relative_roi_to_absolute():
    roi = RelativeROI(x=0.25, y=0.25, w=0.5, h=0.5)
    abs_roi = roi.to_absolute((200, 100))
    assert abs_roi == (50, 25, 100, 50)


def test_anchored_roi_resolution():
    anchor_bbox = (10, 10, 20, 20)
    roi = AnchoredROI(anchor="Test", offset_px=(5, -5), size_px=(15, 10), anchor_corner="top_left")
    resolved = roi.to_absolute(anchor_bbox, (200, 200))
    expected = resolve_anchored_roi(anchor_bbox, (5, -5), (15, 10), "top_left", (200, 200))
    assert resolved == expected
