# evgamelib - Sistema de puntuaciones (high scores)

import json
import os


class HighScoreManager:
    """Maneja high scores persistidos en JSON."""

    def __init__(self, filepath, max_entries=10):
        self.filepath = filepath
        self.max_entries = max_entries

    def load(self):
        """Cargar scores desde JSON"""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    scores = json.load(f)
                    if isinstance(scores, list):
                        return scores
            except Exception:
                pass
        return []

    def save(self, scores):
        """Guardar scores a JSON"""
        try:
            with open(self.filepath, 'w') as f:
                json.dump(scores, f, indent=2)
        except Exception as e:
            print(f"Error saving scores: {e}")

    def add(self, name, score):
        """Agregar un score y mantener solo los top N"""
        scores = self.load()
        scores.append({"name": name, "score": score})
        scores.sort(key=lambda x: x["score"], reverse=True)
        scores = scores[:self.max_entries]
        self.save(scores)
        return scores
