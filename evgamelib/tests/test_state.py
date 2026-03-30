# Tests para evgamelib.state

import pytest
from evgamelib.state import GameState, StateMachine


class MockState(GameState):
    def __init__(self):
        self.entered = False
        self.exited = False
        self.updated = False
        self.rendered = False
        self.last_dt = None

    def enter(self, game):
        self.entered = True

    def exit(self, game):
        self.exited = True

    def update(self, dt, game):
        self.updated = True
        self.last_dt = dt

    def render(self, game):
        self.rendered = True


class TestStateMachine:
    def test_add_and_switch(self):
        sm = StateMachine()
        state = MockState()
        sm.add("play", state)
        sm.switch("play")
        assert sm.current_name == "play"
        assert state.entered == True

    def test_exit_called_on_switch(self):
        sm = StateMachine()
        s1 = MockState()
        s2 = MockState()
        sm.add("s1", s1)
        sm.add("s2", s2)
        sm.switch("s1")
        sm.switch("s2")
        assert s1.exited == True
        assert s2.entered == True

    def test_update_delegates(self):
        sm = StateMachine()
        state = MockState()
        sm.add("play", state)
        sm.switch("play")
        sm.update(0.016)
        assert state.updated == True
        assert state.last_dt == 0.016

    def test_render_delegates(self):
        sm = StateMachine()
        state = MockState()
        sm.add("play", state)
        sm.switch("play")
        sm.render()
        assert state.rendered == True

    def test_no_state(self):
        sm = StateMachine()
        sm.update(0.016)  # No deberia fallar
        sm.render()       # No deberia fallar
