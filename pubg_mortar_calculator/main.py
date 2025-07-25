import customtkinter
import keyboard
import threading
import time
from pubg_mortar_calculator.app import App
from pubg_mortar_calculator.settings_loader import SettingsLoader

def listen_for_keys(app: App):
    while True:
        try:
            if keyboard.is_pressed(app.get_calculate_key()):
                app.process_preview_image(combat_mode=True)
        except ValueError: time.sleep(1)
        time.sleep(0.001)

def on_closing():
    settings_loader.save_current_settings()
    exit()

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")
app = App()
app.protocol("WM_DELETE_WINDOW", on_closing)

base_settings = {
    "last_preview_path":None,
    "dictor":1,
    "draw_grid_lines":1,
    "line_threshold":1700,
    "line_gap":150,
    "gap_threshold":50,
    "show_processed_image":0,
    "canny1_threshold":20,
    "canny2_threshold":40,
    "calculation_key":"ctrl+k",
    "last_color":"orange",  
    "draw_marks":1,
    "add_to_test_samples":0,
}

settings_loader = SettingsLoader(app, 'settings.json', base_settings)
settings_loader.load_settings()

t=threading.Thread(target=listen_for_keys, args=(app,), daemon=True)
t.start()
app.mainloop()


    



             
    