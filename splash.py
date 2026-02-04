import customtkinter as ctk
import tkinter as tk

class SplashScreen(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.overrideredirect(True)   # remove title bar
        self.geometry("400x250")
        self.configure(fg_color="#1E1E2F")

        # center on screen
        self.update_idletasks()
        w, h = 400, 250
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        # UI
        frame = ctk.CTkFrame(self, fg_color="#EC7A6F", corner_radius=15)
        frame.pack(expand=True, fill="both", padx=15, pady=15)

        ctk.CTkLabel(
            frame,
            text="Paint App",
            font=("Arial", 26, "bold")
        ).pack(pady=(40, 10))

        ctk.CTkLabel(
            frame,
            text="Loading...",
            font=("Arial", 14)
        ).pack()

        self.after(2500, self.close_splash)  # 2.5 seconds

    def close_splash(self):
        self.destroy()
