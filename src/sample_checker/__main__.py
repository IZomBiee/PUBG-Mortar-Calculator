def main():
    import customtkinter
    import threading

    from .ui.app import App

    def on_closing():
        exit("Goodbye!")


    customtkinter.set_appearance_mode("System")
    customtkinter.set_default_color_theme("blue")
    print("Loading app...")
    app = App()
    app.protocol("WM_DELETE_WINDOW", on_closing)

    print("Starting program...")
    app.mainloop()

if __name__ == '__main__':
    main()