# In Use
import tkinter as tk

def load_icons(root):
    """Load and return all icons as a dictionary"""

    icons = {
        "pencil": tk.PhotoImage(file="Icons/Small_Pencil.png", master=root),
        "eraser": tk.PhotoImage(file="Icons/Small_Eraser.png", master=root),
        "font": tk.PhotoImage(file="Icons/Small_Font.png", master=root),
        "glass": tk.PhotoImage(file="Icons/Small_Glass.png"),
        "fill": tk.PhotoImage(file="Icons/Small_Fill.png"),
        "save": tk.PhotoImage(file="Icons/Small_Save.png"),
        "clear": tk.PhotoImage(file="Icons/Small_Clear.png"),
        "select_color": tk.PhotoImage(file="Icons/Small_MoreColorsWithPlus.png"),

        "camera": tk.PhotoImage(file="Icons/camera.png"),
        "sound_on": tk.PhotoImage(file="Icons/Volume.png"),
        "sound_off": tk.PhotoImage(file="Icons/Mute.png"),
        "undo": tk.PhotoImage(file="Icons/Icon_Undo.png"),
        "redo": tk.PhotoImage(file="Icons/Icon_Redo.png"),
        "settings": tk.PhotoImage(file="Icons/Icon_Setting.png"),
        "about": tk.PhotoImage(file="Icons/Icon_About.png"),
        "help": tk.PhotoImage(file="Icons/Icon_Help.png"),

        "zoom_in": tk.PhotoImage(file="Icons/Small_Zoom_In.png"),
        "zoom_out": tk.PhotoImage(file="Icons/Small_Zoom_Out.png"),

        "rectangle": tk.PhotoImage(file="Icons/Small_Shape_Rectangle.png"),
        "triangle": tk.PhotoImage(file="Icons/Small_Shape_Triangle.png"),
        "circle": tk.PhotoImage(file="Icons/Small_Shape_Circle.png"),
        "hexagon": tk.PhotoImage(file="Icons/Small_Shape_Hexagon.png"),
        "line": tk.PhotoImage(file="Icons/Small_Shape_Line.png"),
        "arrow": tk.PhotoImage(file="Icons/Small_Shape_Arrow.png"),
        "heart": tk.PhotoImage(file="Icons/Small_Shape_Heart.png"),
        "arc": tk.PhotoImage(file="Icons/Small_Shape_Arc.png"),
        "polygon": tk.PhotoImage(file="Icons/Small_Shape_Polygon.png"),

        "mic": tk.PhotoImage(file="Icons/microphone.png"),
        "mic_open": tk.PhotoImage(file="Icons/microphone_open.png"),
    }

    return icons