from pubg_mortar_calculator.settings_loader import SettingsLoader as SL
from customtkinter import CTkFrame, CTkComboBox

class Combobox:
    def __init__(self, master: CTkFrame, current_value:str|None=None,values:list[str]=[],
                 state='readonly', command=None, command_args:tuple=(),
                 return_value:bool=True, use_settings:bool=True, saving_id:str="Combobox",**kwargs):
        self.master = master
        self.command = command
        self.command_args = command_args
        self.return_value = return_value
        self.use_settings = use_settings
        self.id = saving_id
        self.combobox = CTkComboBox(self.master, command=self.on_combobox,
                                                  state=state, values=list(values), **kwargs)
        if current_value is not None:
            self.add_values(current_value)
        elif len(values) > 0: self.set(values[-1])

        if use_settings:
            value = SL().get(saving_id)
            if value is not None and isinstance(value, str):
                self.set(value)
        
    def grid(self, row=0, column=0, **kwargs) -> "Combobox":
        self.combobox.grid(row=row, column=column, **kwargs)
        return self
    
    def on_combobox(self, value:str):
        SL().set(self.id, value)

        if self.command is not None:
            if self.return_value:
                self.command(value, *self.command_args)
            else:
                self.command(*self.command_args)
        
    def add_values(self, values:str | list[str], select=True):
        if type(values) == str:
            values = [values]
        else:
            values = list(values)
        current_values = self.combobox.cget("values")
        current_values.extend(values)
        self.combobox.configure(values=current_values)
        if select:
            self.combobox.set(values[-1])

    def remove_value(self, value:str):
        current_values = self.combobox.cget("values")
        index = current_values.index(value)

        if index != None:
            current_values.pop(index)
        self.combobox.configure(values=current_values)
        if len(current_values) != 0:
            self.combobox.set(current_values[-1])
        else:self.combobox.set('')
    
    def set_values(self, values: str | list[str]):
        if type(values) == str:
            values = [values]
        else: values = list(values)
        self.combobox.configure(values=values)

    def set(self, value:str):
        self.combobox.set(value)
    
    def get(self) -> str:
        return self.combobox.get()