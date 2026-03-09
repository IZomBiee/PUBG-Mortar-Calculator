import tkinter

from customtkinter import CTkEntry, CTkFrame

from pubg_mortar_calculator.settings_loader import SettingsLoader as SL


class Entry:
    def __init__(
        self,
        master: CTkFrame,
        text: str = "",
        placeholder_text: str = "",
        state: str = "normal",
        saving_id: str = "",
        command=None,
        **kwargs,
    ):
        self.placeholder_text = placeholder_text
        self.id = saving_id
        self.text_varible = tkinter.StringVar()
        self.text_varible.set(text)
        self.use_settings = saving_id != ""
        self.entry = CTkEntry(
            master,
            textvariable=self.text_varible,
            placeholder_text=placeholder_text,
            state=state,
            **kwargs,
        )
        self.command = command
        self.entry.bind("<KeyRelease>", self.on_entry)

        if self.use_settings:
            value = SL().get(self.id)
            if value is not None and isinstance(value, str):
                self.set(value)
            else:
                SL().set(saving_id, self.get())

    def on_entry(self, _):
        if self.use_settings:
            SL().set(self.id, self.get())
        if self.command is not None:
            self.command()

    def get(self):
        return self.entry.get()

    def set(self, text: str):
        self.text_varible.set(text)

    def configure(self, **kwargs):
        self.entry.configure(**kwargs)

    def grid(self, row: int = 0, column: int = 0, **kwargs) -> "Entry":
        self.entry.grid(row=row, column=column, **kwargs)
        return self
