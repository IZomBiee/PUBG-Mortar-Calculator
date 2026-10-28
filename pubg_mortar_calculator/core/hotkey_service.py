from typing import Callable

import keyboard


class HotkeyService:
    def __init__(self):
        self._bindings: dict[str, tuple[str, object]] = {}

    def bind(self, action_name: str, key_combo: str, callback: Callable):
        key_combo = key_combo.strip().lower()

        self.unbind(action_name)

        if not key_combo:
            return True, "Hotkey disabled"
        try:
            hook = keyboard.add_hotkey(key_combo, callback)
            self._bindings[action_name] = (key_combo, hook)
            return True, f"Successfully bound to '{key_combo}'"
        except (ValueError, KeyError, Exception):
            return False, f"Invalid hotkey: '{key_combo}'"

    def unbind(self, action_name: str):
        if action_name in self._bindings:
            _, hook = self._bindings[action_name]
            try:
                keyboard.remove_hotkey(hook)
            except KeyError:
                pass
            del self._bindings[action_name]

    def unbind_all(self):
        for action in list(self._bindings.keys()):
            self.unbind(action)
