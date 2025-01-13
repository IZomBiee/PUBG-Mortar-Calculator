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
                 app.calculate()
        except ValueError: time.sleep(1)
        time.sleep(0.1)

def on_closing():
    settings_loader.save_current()
    profile_loader.save_current_profile()
    exit()

def on_setup():
    settings_loader.set_current()

grid = Grid()

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")
app = App()
app.protocol("WM_DELETE_WINDOW", on_closing)
t=threading.Thread(target=listen_for_keys, args=(app,), daemon=True)
t.start()

base_settings = {
    "last_profile_name":None,
    "last_preview_path":None,
    "autoshooting":False,
    "dictor":False,
    "draw_lines":True,
    "canny_threshold1_max":300,
    "canny_threshold2_max":300,
    "line_threshold_max":4000,
    "line_lenth_max":4000,
    "max_gap_max":200
}
settings_loader = SettingsLoader(app, 'settings.json', base_settings)

default_profile = {
            "canny_threshold1":50,
            "canny_threshold2":100,
            "line_threshold":1000,
            "line_lenth":1000,
            "max_gap":50
        }
profile_loader = ProfileLoader(app, 'sample/profiles/', default_profile)
on_setup()
app.mainloop()


    



             
    

