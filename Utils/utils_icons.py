# utils_icons.py

from PIL import Image
import customtkinter as ctk


def load_icons(root):
    """Load and return all icons as CTkImage dictionary"""

    def icon(path, size=(24, 24)):
        img = Image.open(path)
        return ctk.CTkImage(
            light_image=img,
            dark_image=img,
            size=size
        )

    icons = {
        "pencil": icon("Icons/Small_Pencil.png"),
        "eraser": icon("Icons/Small_Eraser.png"),
        "font": icon("Icons/Small_Font.png"),
        "glass": icon("Icons/Small_Glass.png"),
        "fill": icon("Icons/Small_Fill.png"),
        "save": icon("Icons/Small_Save.png"),
        "clear": icon("Icons/Small_Clear.png"),
        "select_color": icon("Icons/Small_MoreColorsWithPlus.png"),

        "camera": icon("Icons/camera.png"),
        "sound_on": icon("Icons/Icon_Unmute.png"),
        "sound_off": icon("Icons/Icon_Mute.png"),
        "undo": icon("Icons/Icon_Undo.png"),
        "redo": icon("Icons/Icon_Redo.png"),
        "settings": icon("Icons/Icon_Setting.png"),
        "about": icon("Icons/Icon_About.png"),
        "help": icon("Icons/Icon_Help.png"),

        "zoom_in": icon("Icons/Small_Zoom_In.png"),
        "zoom_out": icon("Icons/Small_Zoom_Out.png"),

        "rectangle": icon("Icons/Small_Shape_Rectangle.png"),
        "triangle": icon("Icons/Small_Shape_Triangle.png"),
        "circle": icon("Icons/Small_Shape_Circle.png"),
        "hexagon": icon("Icons/Small_Shape_Hexagon.png"),
        "line": icon("Icons/Small_Shape_Line.png"),
        "arrow": icon("Icons/Small_Shape_Arrow.png"),
        "heart": icon("Icons/Small_Shape_Heart.png"),
        "arc": icon("Icons/Small_Shape_Arc.png"),
        "polygon": icon("Icons/Small_Shape_Polygon.png"),

        "mic": icon("Icons/microphone.png"),
        "mic_open": icon("Icons/microphone_open.png"),
    }

    return icons
