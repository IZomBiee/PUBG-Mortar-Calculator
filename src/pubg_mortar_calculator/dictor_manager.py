import time
from threading import Thread

import pyttsx3

from .utils import singleton


@singleton
class DictorManager:
    def __init__(self, rate=150, volume=0.5) -> None:
        self.queue = []
        self.rate = rate
        self.volume = volume
        self.thread = Thread(target=self.__loop, daemon=True)

    def add(self, text: str | float | int | None) -> None:
        if isinstance(text, float):
            text = round(text)
        self.queue.append(str(text))

    def start(self):
        self.thread.start()

    def __loop(self):
        while True:
            if len(self.queue):
                self.text_to_speech(self.queue.pop(0), self.rate, self.volume)
            time.sleep(0.01)

    @staticmethod
    def text_to_speech(
        text,
        rate: int,
        volume: float,
        voice_id=None,
    ):
        engine = pyttsx3.init()

        engine.setProperty("rate", rate)
        engine.setProperty("volume", volume)

        voices = engine.getProperty("voices")
        if voice_id:
            engine.setProperty("voice", voice_id)
        else:
            engine.setProperty("voice", voices[0].id)

        engine.say(str(text))
        engine.runAndWait()
