from pubg_mortar_calculator.logger import get_logger
from pubg_mortar_calculator.ui.app import App
from pubg_mortar_calculator.utils.screenshot import take_screenshot


def main():
    LOGGER = get_logger()

    LOGGER.info(f"{'=' * 15} PUBG-Mortar-Calculator {'=' * 15}")
    LOGGER.info("Loading settings...")

    app = App()

    LOGGER.debug("Starting program...")
    app.mainloop()


if __name__ == "__main__":
    main()
