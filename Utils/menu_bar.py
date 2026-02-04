import customtkinter as ctk

class MenuBar(ctk.CTkFrame):
    def __init__(
        self,
        master,
        icons,
        callbacks,
        bg_color="#FFFFFF",
        hover_color="#595957"
    ):
        super().__init__(master, fg_color=bg_color, height=50)

        # layout config
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        # LEFT MENU
        left = ctk.CTkFrame(self, fg_color=bg_color)
        left.grid(row=0, column=0, sticky="w", padx=10)

        ctk.CTkButton(left, image=icons["save"],
                      text="", fg_color=bg_color,
                      hover_color=hover_color,
                      command=callbacks["save"]).grid(row=0, column=0, padx=4)

        ctk.CTkButton(left, image=icons["clear"],
                      text="", fg_color=bg_color,
                      hover_color=hover_color,
                      command=callbacks["clear"]).grid(row=0, column=1, padx=4)

        ctk.CTkButton(left, image=icons["undo"],
                      text="", fg_color=bg_color,
                      hover_color=hover_color,
                      command=callbacks["undo"]).grid(row=0, column=2, padx=4)

        ctk.CTkButton(left, image=icons["redo"],
                      text="", fg_color=bg_color,
                      hover_color=hover_color,
                      command=callbacks["redo"]).grid(row=0, column=3, padx=4)

        # RIGHT MENU
        right = ctk.CTkFrame(self, fg_color=bg_color)
        right.grid(row=0, column=1, sticky="e", padx=10)

        ctk.CTkButton(right, image=icons["help"],
                      text="", fg_color=bg_color,
                      hover_color=hover_color,
                      command=callbacks["help"]).pack(side="left", padx=4)

        ctk.CTkButton(right, image=icons["settings"],
                      text="", fg_color=bg_color,
                      hover_color=hover_color,
                      command=callbacks["settings"]).pack(side="left", padx=4)

        ctk.CTkButton(right, image=icons["about"],
                      text="", fg_color=bg_color,
                      hover_color=hover_color,
                      command=callbacks["about"]).pack(side="left", padx=4)
