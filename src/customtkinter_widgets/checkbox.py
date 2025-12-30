from pubg_mortar_calculator.settings_loader import SettingsLoader as SL
from customtkinter import CTkFrame, CTkCheckBox

class Checkbox:
    def __init__(self, master:CTkFrame, 
                 text:str = 'Text', default:bool=False,
                 command=None, command_args:tuple=(), saving_id:str="", **checkbox_args):
        self.master = master
        self.id = saving_id
        self.text = text
        self.command = command
        self.command_args = list(command_args)
        self.use_settings = saving_id != ""
        self.checkbox = CTkCheckBox(self.master, text=text, command=self.on_checkbox, **checkbox_args)

        if self.use_settings:
            value = SL().get(self.id)
            if value is not None and isinstance(value, bool):
                default = value
    
        self.set(default)
    
    def on_checkbox(self):
        if self.use_settings:
            SL().set(self.id, self.get())
        if self.command is not None:
            self.command(*self.command_args)

    def grid(self, row=0, column=0, **kwargs) -> "Checkbox":
        self.checkbox.grid(row=row, column=column, **kwargs)
        return self
    
    def set(self, value:bool):
        SL().set(self.id, value)
        if value: self.checkbox.select()
        else: self.checkbox.deselect()
    
    def get(self) -> bool:
        return bool(self.checkbox.get())