import json
from .utils import singleton, paths

@singleton
class SettingsLoader:
    def __init__(self):
        self.path = paths.settings()
        self._load()
    
    def get(self, key:str) -> object | None:
        return self.settings.get(key, None)

    def set(self, key:str, value):
        self.settings[key] = value
        self.save()
    
    def save(self):
        with open(self.path, 'w') as file:
            json.dump(self.settings, file, indent=4)

    def _load(self):
        try:
            with open(self.path, 'r') as file:
                self.settings: dict = json.load(file)
        except FileNotFoundError:
            self.settings = {}