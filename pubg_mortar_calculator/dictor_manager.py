import pyttsx3
import time

from threading import Thread
from .utils import singleton

@singleton
class DictorManager:
    def __init__(self) -> None:
        self.queue = []
        self.thread = Thread(target=self.__loop, daemon=True)

    def add(self, text:str) -> None:
        self.queue.append(text)

    def start(self):
        self.thread.start()

    def __loop(self):
        while True:
            if len(self.queue):
                self.text_to_speech(self.queue.pop(0))
            time.sleep(0.1)
    
    @staticmethod
    def text_to_speech(text, voice_id=None, rate=180, volume=0.5):
        engine = pyttsx3.init()

        engine.setProperty('rate', rate)
        engine.setProperty('volume', volume)

        voices = engine.getProperty('voices')
        if voice_id:
            engine.setProperty('voice', voice_id)
        else:
            engine.setProperty('voice', voices[0].id)

        engine.say(str(text))
        engine.runAndWait()