import customtkinter as ct
from src.customtkinter_widgets import *
from src.customtkinter_widgets import TitledBlock

class CalculationDataBlock(TitledBlock):
    def __init__(self, master, title: str, fields: list[str], *args, **kwargs):
        super().__init__(master, title, *args, **kwargs)
        grid = self.get_grid()

        self.labels = {}
        row = 0
        for field in fields:
            field_label = ct.CTkLabel(grid, text=field + ":")
            field_label.grid(row=row, column=0, padx=5, pady=2, sticky="w")

            value_label = ct.CTkLabel(grid, text="")
            value_label.grid(row=row, column=1, padx=5, pady=2, sticky="w")

            self.labels[field] = value_label
            row += 1

    def set_value(self, field: str, value: str):
        if field in self.labels:
            self.labels[field].configure(text=value)

    def get_value(self, field: str) -> str | None:
        if field in self.labels:
            return self.labels[field].cget("text")
        return None
