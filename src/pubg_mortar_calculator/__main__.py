
def main():
    import customtkinter
    import keyboard
    import threading
    import time

    from .ui.app import App
    from .settings_loader import SettingsLoader

    def listen_for_keys(app: App):
        while True:
            try:
                if keyboard.is_pressed(app.get_calculation_key()):
                    app.calculate_map_in_combat()
                elif keyboard.is_pressed(app.get_elevation_key()):
                    app.calculate_elevation_in_combat()
            except ValueError: time.sleep(1)
            time.sleep(0.001)

    def on_closing():
        settings_loader.save()
        exit("Goodbye!")

    settings_loader = SettingsLoader()

    customtkinter.set_appearance_mode("System")
    customtkinter.set_default_color_theme("blue")
    print("Loading app...")
    app = App()
    app.protocol("WM_DELETE_WINDOW", on_closing)

    print("Starting keyboard listeners...")
    t=threading.Thread(target=listen_for_keys, args=(app,), daemon=True)
    t.start()

    print("Starting program...")
    app.mainloop()

if __name__ == '__main__':
    main()