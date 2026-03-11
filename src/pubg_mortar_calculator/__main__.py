def main():
    import threading
    import time

    import customtkinter
    import keyboard

    from src.app_overlay import Clear

    from .logger import get_logger
    from .settings_loader import SettingsLoader
    from .ui.app import App
    from .utils.screenshot import take_game_screenshot

    LOGGER = get_logger()

    def listen_for_keys(app: App):
        while True:
            try:
                if keyboard.is_pressed(app.get_calculation_key()):
                    if app.overlay is not None:
                        app.overlay.add_command(Clear())
                    time.sleep(0.1)
                    app.set_map_image(
                        take_game_screenshot(
                            app.app_ui.general_settings_block.title_entry.get()
                        )
                    )
                    time.sleep(0.5)
                elif keyboard.is_pressed(app.get_elevation_key()):
                    app.set_elevation_image(
                        take_game_screenshot(
                            app.app_ui.general_settings_block.title_entry.get()
                        )
                    )
                    time.sleep(0.5)
                elif keyboard.is_pressed(app.get_all_in_one_key()):
                    if app.overlay is not None:
                        app.overlay.add_command(Clear())
                    time.sleep(0.1)

                    screenshot = take_game_screenshot(
                        app.app_ui.general_settings_block.title_entry.get()
                    )
                    app.set_map_image(screenshot, False)
                    app.set_elevation_image(screenshot)

            except ValueError:
                time.sleep(1)
            time.sleep(0.01)

    def on_closing():
        settings_loader.save()
        LOGGER.info("Goodbye!")
        exit()

    LOGGER.info(f"{'=' * 15} PUBG-Mortar-Calculator {'=' * 15}")

    LOGGER.info("Loading settings...")
    settings_loader = SettingsLoader()

    customtkinter.set_appearance_mode("System")
    customtkinter.set_default_color_theme("blue")
    app = App()
    app.protocol("WM_DELETE_WINDOW", on_closing)

    LOGGER.debug("Starting keyboard listeners...")
    t = threading.Thread(target=listen_for_keys, args=(app,), daemon=True)
    t.start()

    LOGGER.debug("Starting program...")
    app.mainloop()


if __name__ == "__main__":
    main()
