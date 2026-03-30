# Tests para evgamelib.scores

import os
import json
import tempfile
import pytest
from evgamelib.scores import HighScoreManager


class TestHighScoreManager:
    def setup_method(self):
        self.tmpfile = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.tmpfile.close()
        self.mgr = HighScoreManager(self.tmpfile.name, max_entries=3)

    def teardown_method(self):
        if os.path.exists(self.tmpfile.name):
            os.unlink(self.tmpfile.name)

    def test_load_empty(self):
        os.unlink(self.tmpfile.name)
        assert self.mgr.load() == []

    def test_add_and_load(self):
        self.mgr.add("ALICE", 100)
        scores = self.mgr.load()
        assert len(scores) == 1
        assert scores[0]["name"] == "ALICE"
        assert scores[0]["score"] == 100

    def test_ordering(self):
        self.mgr.add("BOB", 50)
        self.mgr.add("ALICE", 100)
        self.mgr.add("CHARLIE", 75)
        scores = self.mgr.load()
        assert scores[0]["name"] == "ALICE"
        assert scores[1]["name"] == "CHARLIE"
        assert scores[2]["name"] == "BOB"

    def test_max_entries(self):
        self.mgr.add("A", 10)
        self.mgr.add("B", 20)
        self.mgr.add("C", 30)
        self.mgr.add("D", 40)
        scores = self.mgr.load()
        assert len(scores) == 3
        assert scores[0]["score"] == 40
        assert scores[2]["score"] == 20  # A (10) fue eliminado

    def test_load_corrupted_file(self):
        with open(self.tmpfile.name, 'w') as f:
            f.write("not json")
        assert self.mgr.load() == []
