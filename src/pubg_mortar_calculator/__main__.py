def main():
    import customtkinter
    import keyboard
    import threading
    import time

    from .ui.app import App
    from .settings_loader import SettingsLoader
    from .logger import get_logger

    LOGGER = get_logger()

    def listen_for_keys(app: App):
        while True:
            try:
                if keyboard.is_pressed(app.get_calculation_key()):
                    app.calculate_map_in_combat()
                    time.sleep(0.5)
                elif keyboard.is_pressed(app.get_elevation_key()):
                    app.calculate_elevation_in_combat()
                    time.sleep(0.5)
                elif keyboard.is_pressed(app.get_all_in_one_key()):
                    app.calculate_map_in_combat(False)
                    app.calculate_elevation_in_combat()
            except ValueError: time.sleep(1)
            time.sleep(0.01)

    def on_closing():
        settings_loader.save()
        LOGGER.info("Goodbye!")
        exit()

    settings_loader = SettingsLoader()

    customtkinter.set_appearance_mode("System")
    customtkinter.set_default_color_theme("blue")
    LOGGER.info(f"{'='*15} PUBG-Mortar-Calculator {'='*15}")
    app = App()
    app.protocol("WM_DELETE_WINDOW", on_closing)

    LOGGER.debug("Starting keyboard listeners...")
    t=threading.Thread(target=listen_for_keys, args=(app,), daemon=True)
    t.start()

    LOGGER.debug("Starting program...")
    app.mainloop()

if __name__ == '__main__':
    main()