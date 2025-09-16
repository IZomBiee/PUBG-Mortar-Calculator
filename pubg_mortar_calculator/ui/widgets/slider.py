from pubg_mortar_calculator.settings_loader import SettingsLoader as SL
from customtkinter import CTkFrame, CTkLabel, CTkSlider

class Slider(CTkFrame):
    def __init__(self,
        master, title:str, saving_id:str="", from_:int=0, to:int=100, default:int=0,
        command=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.saving_id = saving_id
        self.command = command

        self.min, self.max = from_, to

        self.describe_label = CTkLabel(self, text=title)
        self.describe_label.grid(row=0, column=0)

        self.slider = CTkSlider(self, from_=from_,
                                to=to, number_of_steps=to-from_)
        self.slider.bind("<ButtonRelease-1>", self.on_slider)
        self.slider.grid(row=0, column=1)

        self.label = CTkLabel(self, text=f'{self.slider.get()}')
        self.label.grid(row=0, column=2)
        
        value = SL().get(self.saving_id)
        if not isinstance(value, int):
            value = default
        self.set(value)
            
    def set(self, value:int):
        print(f"Was {value}")
        if value > self.max: value = self.max
        elif value < self.min: value = self.min
        SL().set(self.saving_id, value)
        print(f"Become {value}")
        self.slider.set(value)
        self.label.configure(text=str(value))
    
    def get(self) -> int:
        return int(self.slider.get())

    def on_slider(self, _):
        value = self.get()
        self.label.configure(text=value)
        if self.saving_id != "":
            SL().set(self.saving_id, value)
        if self.command is not None:
            self.command(value)
