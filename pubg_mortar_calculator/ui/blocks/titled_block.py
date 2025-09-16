import customtkinter as ct

class TitledBlock(ct.CTkFrame):
    def __init__(self, master, title:str, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        
        title_font = ct.CTkFont('Arial', 15, 'bold')

        self.edit_frame = ct.CTkFrame(self, fg_color='transparent')
        self.edit_frame.grid(row=1, column=0, stick="wesn")

        ct.CTkLabel(self, text=title,
            font=title_font).grid(row=0, column=0)

    def grid(self, **kwargs):
        return super().grid(padx=5, pady=5, stick="wesn", **kwargs)

    def get_grid(self) -> ct.CTkFrame:
        return self.edit_frame
    