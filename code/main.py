import customtkinter
import keyboard
import threading
import time
from grid import Grid
from app import App
from settings_loader import SettingsLoader
from profile_loader import ProfileLoader

def listen_for_keys(app: App):
    while True:
        try:
            if keyboard.is_pressed(app.get_calculate_key()):
                 app.process_preview_image(combat_mode=True)
        except ValueError: time.sleep(1)
        time.sleep(0.1)

def on_closing():
    settings_loader.save_current_settings()
    profile_loader.save_all_profiles()
    exit()

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")
app = App()
app.protocol("WM_DELETE_WINDOW", on_closing)

grid = Grid()

base_profile = {
    "canny_threshold1": 100,
    "canny_threshold2": 100,
    "line_threshold": 1000,
    "line_lenth": 200,
    "max_gap": 200
}

profile_loader = ProfileLoader(app, 'profiles.json', base_profile)

base_settings = {
    "last_profile_name":None,
    "last_preview_path":None,
    "autoshooting":False,
    "dictor":False,
    "draw_lines":True,
    "hotkey":"ctrl+k",
    "last_color":"orange"
}
settings_loader = SettingsLoader(app, profile_loader, 'settings.json', base_settings)
settings_loader.load_settings()

t=threading.Thread(target=listen_for_keys, args=(app,), daemon=True)
t.start()
app.mainloop()


    



             
    

