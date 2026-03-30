# Tests para evgamelib.text

import pytest
from evgamelib.text import FloatingText, FloatingTextManager


class TestFloatingText:
    def test_init(self):
        ft = FloatingText(100, 200, "50", duration=1.0)
        assert ft.x == 100
        assert ft.y == 200
        assert ft.text == "50"
        assert ft.timer == 1.0
        assert ft.max_timer == 1.0


class TestFloatingTextManager:
    def test_add(self):
        mgr = FloatingTextManager()
        mgr.add(100, 200, "50")
        assert len(mgr.items) == 1
        assert mgr.items[0].text == "50"

    def test_update_removes_expired(self):
        mgr = FloatingTextManager()
        mgr.add(100, 200, "50", duration=0.5)
        mgr.update(dt=0.6, rise_speed=30)
        assert len(mgr.items) == 0

    def test_update_rises(self):
        mgr = FloatingTextManager()
        mgr.add(100, 200, "50")
        initial_y = mgr.items[0].y
        mgr.update(dt=0.1, rise_speed=30)
        assert mgr.items[0].y < initial_y

    def test_update_multiple(self):
        mgr = FloatingTextManager()
        mgr.add(100, 200, "50", duration=1.0)
        mgr.add(100, 200, "100", duration=0.1)
        mgr.update(dt=0.2, rise_speed=30)
        assert len(mgr.items) == 1  # segundo expiró
        assert mgr.items[0].text == "50"

    def test_clear(self):
        mgr = FloatingTextManager()
        mgr.add(100, 200, "50")
        mgr.add(100, 200, "100")
        mgr.items.clear()
        assert len(mgr.items) == 0
