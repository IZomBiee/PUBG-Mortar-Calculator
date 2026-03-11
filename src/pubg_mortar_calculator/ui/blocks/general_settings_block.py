import customtkinter as ct

from src.customtkinter_widgets import Checkbox, Entry


class GeneralSettingsBlock(ct.CTkFrame):
    def __init__(self, master, on_overlay_change, *args, **kwargs):
        super().__init__(master, fg_color="transparent", *args, **kwargs)

        self.grid_columnconfigure([0, 1], weight=1)
        self.grid_rowconfigure([0, 1, 2, 3, 4], weight=1)
        self.grid_columnconfigure(3, weight=0)

        self.debug_mode_checkbox = Checkbox(
            self, text="Debug Mode", saving_id="general_settings_debug_mode_checkbox"
        ).grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        ct.CTkLabel(self, text="Calculation Hotkey:").grid(
            row=1, column=0, padx=5, pady=5
        )

        self.map_hotkey_entry = Entry(
            self, text="alt+1", saving_id="general_settings_calculation_hotkey_entry"
        )
        self.map_hotkey_entry.grid(row=1, column=1, padx=5, pady=5, sticky="e")

        ct.CTkLabel(self, text="Elevation Hotkey:  ").grid(
            row=2, column=0, padx=5, pady=5
        )

        self.elevation_hotkey_entry = Entry(
            self, "alt+2", "Elevation Hotkey", saving_id="elevation_hotkey_entry"
        ).grid(row=2, column=1, padx=5, pady=5, sticky="e")

        ct.CTkLabel(self, text="All in One Hotkey:  ").grid(
            row=3, column=0, padx=5, pady=5
        )

        self.all_in_one_hotkey_entry = Entry(
            self, "alt+3", "All in One Hotkey", saving_id="all_in_one_hotkey_entry"
        ).grid(row=3, column=1, padx=5, pady=5, sticky="e")

        ct.CTkLabel(self, text="App Title:").grid(row=4, column=0)

        self.title_entry = Entry(
            self,
            text="PUBG:",
            saving_id="general_settings_title_entry",
            command=on_overlay_change,
        ).grid(row=4, column=1, padx=5, pady=5, sticky="e")
