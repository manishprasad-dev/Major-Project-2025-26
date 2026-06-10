from logging import root
import tkinter as tk
import ttkbootstrap as ttk
from turtle import width
from click import command
import cv2
import mediapipe as mp
import time
import customtkinter as ctk 
from tkinter import Button , colorchooser , filedialog , messagebox , scrolledtext
from PIL import ImageGrab as ImageGrab # type: ignore
from PIL import Image,ImageTk
import time
import speech_recognition as sr
import pyaudio
import math
import threading
import warnings
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")

from queue import Queue

camera_queue = Queue()
#! Manual Module Imports
from Utils.utils_icons import load_icons
from Utils.utils_audio import SoundManager
from Utils.camera_utils import start_camera

# ----- Modern UI Settings -----
ctk.set_appearance_mode("dark")        # sleek dark mode
ctk.set_default_color_theme("green")   # fresh green/teal theme

# ==================== WELCOME / SPLASH SCREEN ====================
def show_welcome_screen():
    """
    Standalone splash screen using a plain tk.Tk window.
    Runs its own event loop, then destroys itself — main app starts after.
    """
    splash = tk.Tk()
    splash.overrideredirect(True)   # borderless
    splash.resizable(False, False)
    splash.configure(bg="#0F2027")   # dark gradient start

    # Center on screen
    W, H = 700, 420
    sw = splash.winfo_screenwidth()
    sh = splash.winfo_screenheight()
    splash.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")

    # ---- Gradient background (simulated with canvas) ----
    bg_canvas = tk.Canvas(splash, width=W, height=H, highlightthickness=0)
    bg_canvas.place(x=0, y=0)
    for i, color in enumerate(["#0F2027", "#203A43", "#2C5364"]):
        bg_canvas.create_rectangle(0, i*H//3, W, (i+1)*H//3, fill=color, outline="")

    # ---- Top accent bar ----
    tk.Frame(splash, bg="#EF6262", height=6).pack(fill="x", side="top")

    # ---- Paint emoji icon ----
    tk.Label(splash, text="🎨", font=("Segoe UI Emoji", 72),
             bg="#0F2027", fg="#FFFFFF").pack(pady=(28, 4))

    # ---- App title ----
    tk.Label(splash, text="Paint Studio", font=("Segoe UI", 36, "bold"),
             bg="#0F2027", fg="#2EC4B6").pack(pady=(0, 4))

    # ---- Subtitle ----
    tk.Label(splash, text="Your creative canvas — draw, sketch, and express.",
             font=("Segoe UI", 13), bg="#0F2027", fg="#A8D5CD").pack(pady=(0, 4))

    # ---- Team / version ----
    tk.Label(splash, text="v1.0  ·  By Ricky Singh, Arun Shaw & Manish Kumar Prasad",
             font=("Segoe UI", 10), bg="#0F2027", fg="#6BA297").pack(pady=(0, 16))

    # ---- Progress bar (modern) ----
    bar_canvas = tk.Canvas(splash, width=420, height=14, bg="#1f6b5a", highlightthickness=0)
    bar_canvas.pack(pady=(0, 6))
    bar_fill = bar_canvas.create_rectangle(0, 0, 0, 14, fill="#EF6262", width=0)

    loading_var = tk.StringVar(value="Initializing…")
    tk.Label(splash, textvariable=loading_var, font=("Segoe UI", 11),
             bg="#0F2027", fg="#A8D5CD").pack()

    # ---- Bottom accent bar ----
    tk.Frame(splash, bg="#EF6262", height=6).pack(fill="x", side="bottom")

    # ---- Animation ----
    steps = 60
    messages = {0: "Initializing…", 15: "Loading tools…", 30: "Setting up canvas…",
                45: "Almost ready…", 58: "Welcome!"}

    def animate(step=0):
        if step <= steps:
            fill_w = int((step / steps) * 420)
            bar_canvas.coords(bar_fill, 0, 0, fill_w, 14)
            if step in messages:
                loading_var.set(messages[step])
            splash.after(35, animate, step + 1)
        else:
            window.deiconify()
            splash.destroy()

    animate()
    splash.mainloop()
# ==================== END WELCOME SCREEN ====================

window = ctk.CTk()
window.withdraw()
appicon = tk.PhotoImage(file="Icons/App_Icon.png")
window.iconphoto(False, appicon)

window.title("Paint Studio")
window.geometry("1280x768")
sound_on = True

#! Importing Module Function
icons = load_icons(window)
sound = SoundManager()

# ----- Modern Color Palette -----
MENU_BG         = "#1A1A2E"      # deep navy
TOOLBAR_BG      = "#16213E"      # rich dark blue
TOOLBAR_BORDER  = "#0F3460"      # bright blue border
HOVER_COLOR     = "#E94560"      # vibrant pink/red
ACTIVE_BG       = "#0F3460"
CANVAS_BG       = "#1E1E2F"      # dark grey
FOOTER_BG       = "#1A1A2E"
ACCENT_TEAL     = "#2EC4B6"
ACCENT_CORAL    = "#EF6262"
ACCENT_PURPLE   = "#6A4C93"
TEXT_LIGHT      = "#E0E0E0"
TEXT_DIM        = "#7A8A99"

# Legacy compatibility
activeMenuWidgetBackground = MENU_BG
hoverMenuWidgetBackground = HOVER_COLOR
frameTwoBackgroudColor = TOOLBAR_BG
toolbarHoverColor = HOVER_COLOR
frameFootBackgroundColor = FOOTER_BG

# ------------------------------------------ Parent Frames ------------------------------------------
menuFrame = ctk.CTkFrame(master=window, fg_color=MENU_BG, height=52, corner_radius=0)
frameOne  = ctk.CTkFrame(master=window, fg_color=TOOLBAR_BG, corner_radius=0)
frameTwo  = ctk.CTkFrame(master=window, fg_color=CANVAS_BG, corner_radius=0)
frameFoot = ctk.CTkFrame(master=window, fg_color=FOOTER_BG, height=42, corner_radius=0)

menuFrame.pack(side="top", fill="x")
frameOne.pack(side="top", fill="x", pady=(0, 2))
frameOne.pack_propagate(False)
frameTwo.pack(side="top", fill="both", expand=True)
frameFoot.pack(side="bottom", fill="x")
frameFoot.pack_propagate(False)

# Accent line
ctk.CTkFrame(master=window, fg_color=ACCENT_TEAL, height=2, corner_radius=0).pack(side="top", fill="x", before=frameOne)

# ---------------------------------------- Global Variables -----------------------------------------
shape = ""
preview_shape = ""
undo_stack = []      # Stores (action_type, data) for complete undo/redo
redo_stack = []
stroke_color = tk.StringVar(value="#FFFFFF")
current_line = 1    # 1=solid, 2=dashed, 3=dotted
insert_image = None
image_on_canvas = None
inserted_image = []
original_image = None
image_id = None
current_pil_image = None
canvas_virtual_size = 100000
pencil_select = 0
start_AI_is_running = False
Ai_Mode = False

# Move tool variables
move_tool_active = False
selected_item = None
move_start_x = 0
move_start_y = 0
item_start_coords = []

# Fill tool variables
fill_tool_active = False

# ---------------------------------------- Menu Bar ------------------------------------------------
menuToolFrame = ctk.CTkFrame(master=menuFrame, fg_color=MENU_BG)
menuToolFrame.pack(side="left", padx=10)

HelpSettingFrame = ctk.CTkFrame(master=menuFrame, fg_color=MENU_BG)
HelpSettingFrame.pack(side="right")

def SaveImage():
    if sound_on and not start_AI_is_running:
        sound.play("Save_Sound")
    filelocation = filedialog.asksaveasfilename(defaultextension="jpg")
    x = window.winfo_rootx() + 35
    y = window.winfo_rooty() + 250
    img = ImageGrab.grab(bbox=(x, y, x+1340, y+640))
    img.save(filelocation)
    if img.save and sound_on:
        sound.play("ImageSaved_Sound")
    if sound_on:
        window.after(2000, lambda: sound.play("OpenImage_Sound"))
    if messagebox.askyesno("Paint Studio", "Do you want to open the saved image?"):
        img.show()

def clear():
    global undo_stack, redo_stack
    if sound_on and not start_AI_is_running:
        sound.play("clear_Sound")
    if messagebox.askokcancel("Clear Canvas", "Do you want to clear everything?"):
        canvas.delete('all')
        undo_stack.clear()
        redo_stack.clear()
        if sound_on:
            sound.play("EverythingCleared_Sound")

def undo():
    if undo_stack:
        action = undo_stack.pop()
        if action[0] == "create":
            # hide item
            canvas.itemconfig(action[1], state='hidden')
            redo_stack.append(("hide", action[1]))
        elif action[0] == "move":
            # restore old coords
            item_id, old_coords = action[1], action[2]
            canvas.coords(item_id, *old_coords)
            redo_stack.append(("move", item_id, canvas.coords(item_id)))
        elif action[0] == "fill":
            item_id, old_fill = action[1], action[2]
            canvas.itemconfig(item_id, fill=old_fill)
            redo_stack.append(("fill", item_id, stroke_color.get()))

def redo():
    if redo_stack:
        action = redo_stack.pop()
        if action[0] == "hide":
            canvas.itemconfig(action[1], state='normal')
            undo_stack.append(("create", action[1]))
        elif action[0] == "move":
            item_id, new_coords = action[1], action[2]
            canvas.coords(item_id, *new_coords)
            undo_stack.append(("move", item_id, new_coords))
        elif action[0] == "fill":
            item_id, new_fill = action[1], action[2]
            canvas.itemconfig(item_id, fill=new_fill)
            undo_stack.append(("fill", item_id, new_fill))

def toggle_sound():
    global sound_on
    sound_on = not sound_on
    if sound_on:
        sound_button.configure(image=icons["sound_on"])
        sound.play("SoundOn_Sound")
    else:
        sound_button.configure(image=icons["sound_off"])
        sound.play("SoundOff_Sound")

def help_window():
    new_window = tk.Toplevel(window)
    new_window.title("Help")
    new_window.geometry("500x650")
    new_window.configure(bg="#0F2027")
    help_text = """                               Paint Studio Help

• Getting Started  
  → Select a tool from the toolbar.
  → Choose a color.
  → Click & drag to draw (left button for freehand, right button for shapes).

• Tools  
  → Brush / Pencil – freehand drawing.
  → Eraser – erase with white.
  → Select/Move – click on a shape and drag to reposition.
  → Fill Shape – click inside a shape to fill with current color.
  → Text – add text at chosen position.
  → Insert Image – place an image, then drag to move.
  → Camera – gesture‑controlled drawing.
  → Mic – voice commands.

• Shortcuts  
  Ctrl+Z – Undo    Ctrl+Y – Redo    Ctrl+S – Save
  Ctrl+A – Clear   Ctrl+P – Pencil  Ctrl+E – Eraser
  V – Toggle voice AI    Ctrl+ / Ctrl- – Zoom
  Arrow keys – Pan canvas

• Tips  
  Scroll wheel changes brush size.
  Right‑click & drag draws perfect shapes.
  """
    text_area = scrolledtext.ScrolledText(new_window, wrap=tk.WORD, font=("Segoe UI", 11),
                                          bg="#0D1B2A", fg="#D0E8E0")
    text_area.insert(tk.END, help_text)
    text_area.config(state='disabled')
    text_area.pack(expand=True, fill='both')

def aboutus_window():
    new_window = tk.Toplevel(window)
    new_window.title("About Us")
    new_window.geometry("450x550")
    new_window.configure(bg="#0F2027")
    about_text = """                                     About Us

Paint Studio v1.0

A modern paint application with voice AI, gesture control,
undo/redo, shape repositioning, and a beautiful interface.

🛠 Features:
• Freehand & shape drawing
• Eraser & fill tool
• Move any shape after drawing
• Undo/Redo for all actions
• Voice commands & camera gestures

👨‍💻 Developed By:
• Ricky Singh
• Arun Kumar Ray
• Manish Kumar Prasad

© 2025 All Rights Reserved
Thank you for using Paint Studio!
"""
    text_area = scrolledtext.ScrolledText(new_window, wrap=tk.WORD, font=("Segoe UI", 11),
                                          bg="#0D1B2A", fg="#D0E8E0")
    text_area.insert(tk.END, about_text)
    text_area.config(state='disabled')
    text_area.pack(expand=True, fill='both')

def setting_window():
    new_window = ctk.CTkToplevel(window)
    new_window.title("Settings")
    new_window.geometry("500x400")
    new_window.configure(fg_color="#0F2027")
    ctk.CTkLabel(new_window, text="Settings will be available in the next update",
                 font=("Segoe UI", 16), text_color=ACCENT_TEAL).pack(expand=True)

# Menu buttons
def _menu_btn(parent, image, cmd):
    return ctk.CTkButton(parent, text="", image=image, fg_color=MENU_BG,
                         hover_color=HOVER_COLOR, width=38, height=38,
                         corner_radius=8, command=cmd)

saveImageButton = _menu_btn(menuToolFrame, icons["save"], SaveImage)
clearImageButton = _menu_btn(menuToolFrame, icons["clear"], clear)
undo_button = _menu_btn(menuToolFrame, icons["undo"], undo)
redo_button = _menu_btn(menuToolFrame, icons["redo"], redo)
sound_button = _menu_btn(menuToolFrame, icons["sound_on"], toggle_sound)

ctk.CTkFrame(menuToolFrame, fg_color=TOOLBAR_BORDER, width=2, height=30).grid(row=0, column=5, padx=6)

helpButton = _menu_btn(HelpSettingFrame, icons["help"], help_window)
settingButton = _menu_btn(HelpSettingFrame, icons["settings"], setting_window)
aboutButton = _menu_btn(HelpSettingFrame, icons["about"], aboutus_window)

# Placements
saveImageButton.grid(row=0, column=0, padx=4, pady=8)
clearImageButton.grid(row=0, column=1, padx=4, pady=8)
undo_button.grid(row=0, column=2, padx=4, pady=8)
redo_button.grid(row=0, column=3, padx=4, pady=8)
sound_button.grid(row=0, column=4, padx=4, pady=8)
helpButton.pack(side="left", padx=4, pady=8)
settingButton.pack(side="left", padx=4, pady=8)
aboutButton.pack(side="left", padx=4, pady=8)

# ---------------------------------------- Toolbar Sections ----------------------------------------
frameOne.grid_rowconfigure(0, weight=1)

def _section(parent, col, label, w, h):
    wrapper = ctk.CTkFrame(parent, fg_color=TOOLBAR_BG, corner_radius=0)
    wrapper.grid(row=0, column=col, padx=0, pady=0, sticky="ns")
    ctk.CTkLabel(wrapper, text=label, font=("Segoe UI", 9, "bold"),
                 text_color=ACCENT_TEAL).pack(side="top", pady=(6, 2))
    inner = ctk.CTkFrame(wrapper, fg_color="#0F2027", border_width=1,
                         border_color=TOOLBAR_BORDER, width=w, height=h, corner_radius=10)
    inner.pack(side="top", padx=8, pady=(0, 8))
    inner.pack_propagate(False)
    ctk.CTkFrame(wrapper, fg_color=TOOLBAR_BORDER, width=1).pack(side="right", fill="y", pady=6)
    return inner

toolFrame = _section(frameOne, 0, "TOOLS", 180, 96)
lineTypeFrame = _section(frameOne, 1, "LINE STYLE", 158, 96)
shapeFrame = _section(frameOne, 2, "SHAPES", 350, 96)
colorFrame = _section(frameOne, 3, "COLORS", 210, 96)
addColorFrame = _section(frameOne, 4, "PICKER", 80, 96)
advToolFrame = _section(frameOne, 5, "ADVANCED", 130, 96)

# ---------- Tools ----------
def usePencil():
    global pencil_select, current_line, move_tool_active, fill_tool_active
    move_tool_active = False
    fill_tool_active = False
    pencil_select += 1
    if sound_on and not start_AI_is_running:
        if pencil_select != 1:
            sound.play("Pencil_Sound")
        if pencil_select == 1:
            window.after(6000, lambda: sound.play("DefaultBlack_Sound"))
            stroke_color.set("#000000")
            current_color_preview.configure(fg_color="#000000")
    canvas.config(cursor="crosshair")
    SolidLineButton.configure(fg_color="white")
    DashedLineButton.configure(fg_color="#E5F0EF")
    DottedLineButton.configure(fg_color="#E5F0EF")
    current_line = 1

def useEraser():
    global move_tool_active, fill_tool_active
    move_tool_active = False
    fill_tool_active = False
    if sound_on and not start_AI_is_running:
        sound.play("Eraser_Sound")
    stroke_color.set("#FFFFFF")
    current_color_preview.configure(fg_color="#FFFFFF")
    canvas.config(cursor="dotbox")

def activate_move_tool():
    global move_tool_active, fill_tool_active
    move_tool_active = True
    fill_tool_active = False
    canvas.config(cursor="hand2")
    if sound_on:
        sound.play("Pencil_Sound")  # placeholder

def activate_fill_tool():
    global fill_tool_active, move_tool_active
    fill_tool_active = True
    move_tool_active = False
    canvas.config(cursor="spraycan")
    if sound_on:
        sound.play("selectcolor_Sound")

def addText():
    add_text_window()

def insert():
    global current_pil_image, image_id, original_image
    file_path = filedialog.askopenfilename(title="Select Image",
                                           filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")])
    if file_path:
        current_pil_image = Image.open(file_path)
        current_pil_image.thumbnail((400, 400))
        original_image = current_pil_image.copy()
        tk_image = ImageTk.PhotoImage(current_pil_image)
        inserted_image.append(tk_image)
        x = canvas.winfo_width() // 2
        y = (canvas.winfo_height() // 2) - 170
        image_id = canvas.create_image(x, y, image=tk_image, anchor="center")
        undo_stack.append(("create", image_id))
        canvas.tk_image = tk_image
        # Bind drag to move image
        canvas.tag_bind(image_id, "<Button-1>", image_move_start)
        canvas.tag_bind(image_id, "<B1-Motion>", image_do_move)

# Move image handlers
image_last_x, image_last_y = 0, 0
def image_move_start(event):
    global image_last_x, image_last_y, selected_item
    selected_item = image_id
    image_last_x = event.x
    image_last_y = event.y
    return "break"
def image_do_move(event):
    global image_last_x, image_last_y, selected_item
    if selected_item == image_id:
        dx = event.x - image_last_x
        dy = event.y - image_last_y
        canvas.move(selected_item, dx, dy)
        image_last_x = event.x
        image_last_y = event.y
        return "break"

def _tool_btn(parent, img, cmd, x, y):
    b = ctk.CTkButton(parent, text="", image=img, command=cmd,
                      fg_color="#0F2027", hover_color=HOVER_COLOR,
                      width=38, height=38, corner_radius=8)
    b.place(x=x, y=y)
    return b

pencilIcon = _tool_btn(toolFrame, icons["pencil"], usePencil, 8, 6)
eraserIcon = _tool_btn(toolFrame, icons["eraser"], useEraser, 8, 50)
fontIcon = _tool_btn(toolFrame, icons["font"], addText, 50, 6)
fillIcon = _tool_btn(toolFrame, icons["fill"], activate_fill_tool, 92, 6)
# Fallback for move icon if not available
move_icon = icons.get("move", None)
if move_icon is None:
    # Create a simple label as fallback
    move_icon = ctk.CTkImage(light_image=Image.new("RGBA", (24,24), (0,0,0,0)), size=(24,24))
moveIcon = _tool_btn(toolFrame, move_icon, activate_move_tool, 134, 6)
insertIcon = _tool_btn(toolFrame, icons["glass"], insert, 50, 50)

# ---------- Line Styles ----------
def solidline():
    global current_line, move_tool_active, fill_tool_active
    move_tool_active = fill_tool_active = False
    current_line = 1
    if sound_on: sound.play("SolidLineResponse")
    SolidLineButton.configure(fg_color="white")
    DashedLineButton.configure(fg_color="#E5F0EF")
    DottedLineButton.configure(fg_color="#E5F0EF")
    canvas.config(cursor="crosshair")

def DashedLine():
    global current_line, move_tool_active, fill_tool_active
    move_tool_active = fill_tool_active = False
    current_line = 2
    if sound_on: sound.play("DashedLineResponse")
    DashedLineButton.configure(fg_color="white")
    DottedLineButton.configure(fg_color="#E5F0EF")
    SolidLineButton.configure(fg_color="#E5F0EF")
    canvas.config(cursor="boat")

def DottedLine():
    global current_line, move_tool_active, fill_tool_active
    move_tool_active = fill_tool_active = False
    current_line = 3
    if sound_on: sound.play("DottedLineResponse")
    DottedLineButton.configure(fg_color="white")
    DashedLineButton.configure(fg_color="#E5F0EF")
    SolidLineButton.configure(fg_color="#E5F0EF")
    canvas.config(cursor="dot")

def _line_btn(text, cmd, row):
    b = ctk.CTkButton(lineTypeFrame, text=text, command=cmd, text_color=TEXT_LIGHT,
                      font=("Courier", 12, "bold"), fg_color="#0F2027",
                      hover_color=HOVER_COLOR, corner_radius=8, height=26, width=140)
    b.grid(row=row, column=0, padx=8, pady=5)
    return b

SolidLineButton = _line_btn("━━━━━━━", solidline, 0)
DashedLineButton = _line_btn("╌╌╌╌╌╌╌", DashedLine, 1)
DottedLineButton = _line_btn("·  ·  ·  ·  ·", DottedLine, 2)

# ---------- Shapes ----------
def select_circle():   global shape; shape = "circle"; sound.play("Circle_Sound") if sound_on else None
def select_rectangle(): global shape; shape = "rectangle"; sound.play("Rectangle_Sound") if sound_on else None
def select_line():     global shape; shape = "line"; sound.play("Line_Sound") if sound_on else None
def select_triangle(): global shape; shape = "triangle"; sound.play("Triangle_Sound") if sound_on else None
def select_polygon():  global shape; shape = "polygon"; sound.play("Pentagon_Sound") if sound_on else None
def select_arc():      global shape; shape = "arc"; sound.play("ArcResponse") if sound_on else None
def select_heart():    global shape; shape = "heart"; sound.play("Heart_Sound") if sound_on else None
def select_arrow():    global shape; shape = "arrow"; sound.play("Arrow_Sound") if sound_on else None

shape_buttons = [(select_circle, icons["circle"]), (select_rectangle, icons["rectangle"]),
                 (select_line, icons["line"]), (select_triangle, icons["triangle"]),
                 (select_polygon, icons["polygon"]), (select_arc, icons["arc"]),
                 (select_heart, icons["heart"]), (select_arrow, icons["arrow"])]
for idx, (cmd, img) in enumerate(shape_buttons):
    ctk.CTkButton(shapeFrame, text="", image=img, command=cmd, fg_color="#0F2027",
                  hover_color=HOVER_COLOR, width=44, height=44, corner_radius=8).grid(
                  row=idx // 8, column=idx % 8, padx=3, pady=4)

# ---------- Colors ----------
color_palette = ["#FF595E","#FFCA3A","#8AC926","#1982C4","#6A4C93",
                 "#000000","#FFFFFF","#808080","#FF9F1C","#2EC4B6"]
for i, col in enumerate(color_palette):
    ctk.CTkButton(colorFrame, text="", fg_color=col.lower(), hover_color=col.lower(),
                  width=32, height=32, corner_radius=16, border_width=2, border_color="#1A2A3A",
                  command=lambda c=col: stroke_color.set(c.lower())).grid(
                  row=i//5, column=i%5, padx=6, pady=6)

def selectcolor():
    col = colorchooser.askcolor(title="Select Color")[1]
    if col:
        stroke_color.set(col)
        current_color_preview.configure(fg_color=col)

colorBoxButton = ctk.CTkButton(addColorFrame, text="", image=icons["select_color"],
                               command=selectcolor, fg_color="#0F2027", hover_color=HOVER_COLOR,
                               width=48, height=48, corner_radius=10)
colorBoxButton.pack(pady=(10, 0))
current_color_preview = ctk.CTkFrame(addColorFrame, fg_color=stroke_color.get(),
                                     width=32, height=32, corner_radius=16,
                                     border_width=2, border_color=ACCENT_TEAL)
current_color_preview.pack(pady=6)

# ---------- Advanced (Camera & Mic) ----------
def camera():
    if sound_on and not start_AI_is_running:
        sound.play("CameraOpen_Sound")
    actions = {"save": SaveImage, "clear": clear, "mute": toggle_sound,
               "text": addText, "draw": camera_draw}
    threading.Thread(target=start_camera, args=(sound, actions)).start()

def camera_draw(x1, y1, x2, y2):
    camera_queue.put((x1, y1, x2, y2))

def process_camera_queue():
    while not camera_queue.empty():
        x1, y1, x2, y2 = camera_queue.get()
        item = canvas.create_line(x1, y1, x2, y2, fill=stroke_color.get(),
                                  width=stroke_size.get(), capstyle=tk.ROUND,
                                  smooth=True, splinesteps=36, dash=get_line_dash_pattern())
        undo_stack.append(("create", item))
    window.after(10, process_camera_queue)

def toggle_mic():
    global Ai_Mode, start_AI_is_running, sound_on
    Ai_Mode = not Ai_Mode
    sound_on = True
    sound_button.configure(image=icons["sound_on"])
    if Ai_Mode:
        useMicButton.configure(image=icons["mic_open"])
        if not start_AI_is_running:
            start_AI()
            start_AI_is_running = True
    else:
        useMicButton.configure(image=icons["mic"])
        ptt_stop()
        start_AI_is_running = False

openCameraButton = ctk.CTkButton(advToolFrame, text="", image=icons["camera"], command=camera,
                                 fg_color="#0F2027", hover_color=HOVER_COLOR, width=52, height=40, corner_radius=8)
openCameraButton.grid(row=0, column=0, padx=8, pady=(8,4))
useMicButton = ctk.CTkButton(advToolFrame, text="", image=icons["mic"], command=toggle_mic,
                             fg_color="#0F2027", hover_color=HOVER_COLOR, width=52, height=40, corner_radius=8)
useMicButton.grid(row=1, column=0, padx=8, pady=(4,8))

# ---------- Voice AI ----------
mic = sr.Recognizer()
pyaudio_instance = pyaudio.PyAudio()
stream = None
last_text = ""

def voice_command(text):
    global last_text
    text = text.strip().lower()
    if not text or text == last_text: return
    last_text = text
    # Voice command logic
    if 'pencil' in text: usePencil()
    elif 'eraser' in text: useEraser()
    elif 'color' in text: selectcolor()
    elif 'dotted' in text: DottedLine()
    elif 'dashed' in text: DashedLine()
    elif 'solid' in text: solidline()
    elif 'rectangle' in text: select_rectangle()
    elif 'circle' in text: select_circle()
    elif 'triangle' in text: select_triangle()
    elif 'pentagon' in text: select_polygon()
    elif 'arc' in text: select_arc()
    elif 'heart' in text: select_heart()
    elif 'arrow' in text: select_arrow()
    elif 'save' in text: SaveImage()
    elif 'clear' in text: clear()
    elif 'undo' in text: undo()
    elif 'redo' in text: redo()
    elif 'quit' in text or 'stop' in text: ptt_stop()
    else: pass

def ptt_stop(event=None):
    global Ai_Mode
    sound.play("AiModeOff")
    Ai_Mode = False

def listen():
    sound.play("AiModeOn")
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        while Ai_Mode:
            try:
                audio = r.listen(source)
                text = r.recognize_google(audio, language='en-IN')
                if text: voice_command(text)
            except: continue

def start_AI():
    global Ai_Mode, start_AI_is_running
    if not Ai_Mode: return
    if not start_AI_is_running:
        threading.Thread(target=listen, daemon=True).start()
        start_AI_is_running = True

# ---------------------------------------- Canvas & Drawing ----------------------------------------
stroke_size = tk.IntVar(value=5)
scale = ctk.CTkSlider(window, from_=1, to=100, orientation="vertical",
                      variable=stroke_size, height=280, progress_color=ACCENT_TEAL,
                      button_color=ACCENT_CORAL, fg_color="#1A2A3A")
scale.place(x=12, y=210)
size_label = ctk.CTkLabel(window, textvariable=stroke_size, font=("Segoe UI", 12, "bold"),
                          text_color=ACCENT_TEAL, fg_color=CANVAS_BG, width=30, height=26, corner_radius=8)
size_label.place(x=10, y=498)

def incre_scale(event):
    if event.delta > 0: stroke_size.set(stroke_size.get() + 1)
    else: stroke_size.set(stroke_size.get() - 1)

# Canvas with scrollbars
canvas_frame = ctk.CTkFrame(frameTwo, fg_color=CANVAS_BG, corner_radius=12)
canvas_frame.pack(side="top", fill="both", expand=True, padx=8, pady=8)
canvas = tk.Canvas(canvas_frame, bg="#FAFAFA", highlightthickness=2, highlightbackground=ACCENT_TEAL)
canvas.pack(side="left", fill="both", expand=True)
v_scroll = ctk.CTkScrollbar(canvas_frame, orientation="vertical", command=canvas.yview)
v_scroll.pack(side="right", fill="y")
h_scroll = ctk.CTkScrollbar(canvas_frame, orientation="horizontal", command=canvas.xview)
h_scroll.pack(side="bottom", fill="x")
canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set,
                 scrollregion=(-canvas_virtual_size, -canvas_virtual_size,
                               canvas_virtual_size, canvas_virtual_size))
canvas.config(cursor="crosshair")
process_camera_queue()

# Drawing variables
prevPoint = [0,0]
currentPoint = [0,0]
start_x = start_y = 0

def get_line_dash_pattern():
    if current_line == 1: return ()
    elif current_line == 2: return (30,15)
    elif current_line == 3: return (1,10)
    else: return ()

def paint(event):
    if move_tool_active or fill_tool_active: return
    x = canvas.canvasx(event.x)
    y = canvas.canvasy(event.y)
    global prevPoint, currentPoint
    currentPoint = [x, y]
    if prevPoint != [0,0]:
        item = canvas.create_line(prevPoint[0], prevPoint[1], currentPoint[0], currentPoint[1],
                                  fill=stroke_color.get(), width=stroke_size.get(),
                                  capstyle=tk.ROUND, smooth=True, splinesteps=36,
                                  dash=get_line_dash_pattern())
        undo_stack.append(("create", item))
    prevPoint = currentPoint
    if event.type == "5": prevPoint = [0,0]

def start_shape(event):
    if move_tool_active or fill_tool_active: return
    global start_x, start_y
    start_x = canvas.canvasx(event.x)
    start_y = canvas.canvasy(event.y)

def drawshape(event):
    if move_tool_active or fill_tool_active: return
    global preview_shape
    if preview_shape:
        canvas.delete(preview_shape)
        preview_shape = None
    end_x = canvas.canvasx(event.x)
    end_y = canvas.canvasy(event.y)
    item = None
    if shape == "circle":
        item = canvas.create_oval(start_x, start_y, end_x, end_y,
                                  outline=stroke_color.get(), width=stroke_size.get())
    elif shape == "rectangle":
        item = canvas.create_rectangle(start_x, start_y, end_x, end_y,
                                       outline=stroke_color.get(), width=stroke_size.get())
    elif shape == "line":
        item = canvas.create_line(start_x, start_y, end_x, end_y,
                                  fill=stroke_color.get(), width=stroke_size.get(),
                                  dash=get_line_dash_pattern())
    elif shape == "triangle":
        item = canvas.create_polygon(start_x, end_y, (start_x+end_x)//2, start_y,
                                     end_x, end_y, outline=stroke_color.get(),
                                     fill='', width=stroke_size.get())
    elif shape == "polygon":
        item = canvas.create_polygon(start_x, start_y, end_x, start_y, end_x, end_y,
                                     (start_x+end_x)//2, end_y+40, start_x, end_y,
                                     outline=stroke_color.get(), fill='', width=stroke_size.get())
    elif shape == "arc":
        item = canvas.create_arc(start_x, start_y, end_x, end_y, outline=stroke_color.get(),
                                 width=stroke_size.get(), start=0, extent=150, style=tk.ARC)
    elif shape == "arrow":
        item = canvas.create_line(start_x, start_y, end_x, end_y, arrow=tk.LAST,
                                  fill=stroke_color.get(), width=stroke_size.get())
    elif shape == "heart":
        cx = (start_x+end_x)/2
        cy = (start_y+end_y)/2
        w = abs(end_x-start_x)/2
        h = abs(end_y-start_y)/2
        points = []
        for t in range(0,360,10):
            rad = math.radians(t)
            x = w * 16 * math.sin(rad)**3
            y = -h * (13*math.cos(rad) - 5*math.cos(2*rad) - 2*math.cos(3*rad) - math.cos(4*rad))
            points.append((cx+x, cy+y))
        flat = [coord for pt in points for coord in pt]
        item = canvas.create_polygon(flat, outline=stroke_color.get(), fill='', width=stroke_size.get())
    if item:
        undo_stack.append(("create", item))

def on_right_drag(event):
    if move_tool_active or fill_tool_active: return
    global preview_shape
    if preview_shape: canvas.delete(preview_shape)
    size = stroke_size.get()
    color = stroke_color.get()
    cur_x = canvas.canvasx(event.x)
    cur_y = canvas.canvasy(event.y)
    if shape == "rectangle":
        preview_shape = canvas.create_rectangle(start_x, start_y, cur_x, cur_y, outline=color, width=size)
    elif shape == "circle":
        preview_shape = canvas.create_oval(start_x, start_y, cur_x, cur_y, outline=color, width=size)
    elif shape == "line":
        preview_shape = canvas.create_line(start_x, start_y, cur_x, cur_y, fill=color, width=size, dash=get_line_dash_pattern())
    elif shape == "arc":
        preview_shape = canvas.create_arc(start_x, start_y, cur_x, cur_y, outline=color, width=size, start=0, extent=150, style=tk.ARC)
    elif shape == "triangle":
        mid_x = (start_x + cur_x)/2
        preview_shape = canvas.create_polygon(start_x, cur_y, cur_x, cur_y, mid_x, start_y, outline=color, fill='', width=size)
    elif shape == "arrow":
        preview_shape = canvas.create_line(start_x, start_y, cur_x, cur_y, arrow=tk.LAST, fill=color, width=size)
    elif shape == "heart":
        cx = (start_x+cur_x)/2
        cy = (start_y+cur_y)/2
        w = abs(cur_x-start_x)/2
        h = abs(cur_y-start_y)/2
        points = []
        for t in range(0,360,10):
            rad = math.radians(t)
            x = w * 16 * math.sin(rad)**3
            y = -h * (13*math.cos(rad) - 5*math.cos(2*rad) - 2*math.cos(3*rad) - math.cos(4*rad))
            points.append((cx+x, cy+y))
        flat = [coord for pt in points for coord in pt]
        preview_shape = canvas.create_polygon(flat, outline=color, fill='', width=size)

# Move tool handlers
def on_move_click(event):
    if not move_tool_active: return
    global selected_item, move_start_x, move_start_y, item_start_coords
    x = canvas.canvasx(event.x)
    y = canvas.canvasy(event.y)
    items = canvas.find_overlapping(x-5, y-5, x+5, y+5)
    if items:
        selected_item = items[0]
        move_start_x = x
        move_start_y = y
        item_start_coords = canvas.coords(selected_item)
        canvas.config(cursor="fleur")
        return "break"

def on_move_drag(event):
    global move_start_x, move_start_y
    if not move_tool_active or selected_item is None: return
    x = canvas.canvasx(event.x)
    y = canvas.canvasy(event.y)
    dx = x - move_start_x
    dy = y - move_start_y
    canvas.move(selected_item, dx, dy)
    # Update start positions for smooth dragging
    move_start_x = x
    move_start_y = y
    return "break"

def on_move_release(event):
    if not move_tool_active or selected_item is None: return
    new_coords = canvas.coords(selected_item)
    if new_coords != item_start_coords:
        undo_stack.append(("move", selected_item, item_start_coords))
        redo_stack.clear()
    selected_item = None
    canvas.config(cursor="hand2")
    return "break"

# Fill tool handler
def on_fill_click(event):
    if not fill_tool_active: return
    x = canvas.canvasx(event.x)
    y = canvas.canvasy(event.y)
    items = canvas.find_overlapping(x-2, y-2, x+2, y+2)
    if items:
        item = items[0]
        old_fill = canvas.itemcget(item, "fill")
        if old_fill == "":
            # For outlines, change outline color
            old_outline = canvas.itemcget(item, "outline")
            canvas.itemconfig(item, outline=stroke_color.get())
            undo_stack.append(("fill", item, old_outline))
        else:
            canvas.itemconfig(item, fill=stroke_color.get())
            undo_stack.append(("fill", item, old_fill))
        redo_stack.clear()
    return "break"

canvas.bind("<B1-Motion>", paint)
canvas.bind("<ButtonRelease-1>", paint)
canvas.bind("<ButtonPress-3>", start_shape)
canvas.bind("<ButtonRelease-3>", drawshape)
canvas.bind("<B3-Motion>", on_right_drag)

# Bind move and fill tools (additional bindings, order doesn't conflict due to mode checks)
canvas.bind("<Button-1>", on_move_click, add="+")
canvas.bind("<B1-Motion>", on_move_drag, add="+")
canvas.bind("<ButtonRelease-1>", on_move_release, add="+")
canvas.bind("<Button-1>", on_fill_click, add="+")

# Text addition
def add_text_window():
    tw = ctk.CTkToplevel(window)
    tw.title("Add Text")
    tw.geometry("500x300")
    tw.configure(fg_color="#0F2027")
    ctk.CTkLabel(tw, text="Enter Text:", font=("Segoe UI", 12)).pack(pady=10)
    global text_entry
    text_entry = ctk.CTkEntry(tw, width=300, fg_color="#0F3460")
    text_entry.pack(pady=5)
    ctk.CTkLabel(tw, text="X Position:").pack()
    global x_slider
    x_slider = ctk.CTkSlider(tw, from_=0, to=1280, width=300)
    x_slider.set(200)
    x_slider.pack(pady=5)
    ctk.CTkLabel(tw, text="Y Position:").pack()
    global y_slider
    y_slider = ctk.CTkSlider(tw, from_=0, to=800, width=300)
    y_slider.set(125)
    y_slider.pack(pady=5)
    ctk.CTkButton(tw, text="Add Text", command=add_Text, fg_color=ACCENT_TEAL).pack(pady=10)

def add_Text():
    text = text_entry.get()
    x = x_slider.get()
    y = y_slider.get()
    item = canvas.create_text(x, y, text=text, font=("Segoe UI", 16),
                              fill=stroke_color.get())
    undo_stack.append(("create", item))

# Zoom & Pan
zoom_factor = 1.0
def apply_zoom(new_zoom):
    global zoom_factor
    s = new_zoom / zoom_factor
    canvas.scale("all", 0, 0, s, s)
    zoom_factor = new_zoom
    refresh_image_zoom()
    bbox = canvas.bbox("all")
    if bbox: canvas.configure(scrollregion=bbox)

def zoom_in(e=None):
    if zoom_factor < 5:
        apply_zoom(zoom_factor * 1.1)
        zoomSlider.set(zoom_factor * 100)

def zoom_out(e=None):
    if zoom_factor > 0.2:
        apply_zoom(zoom_factor / 1.1)
        zoomSlider.set(zoom_factor * 100)

def slider_zoom(val):
    apply_zoom(float(val)/100)

def refresh_image_zoom():
    global image_id, original_image, zoom_factor
    if image_id and original_image:
        x, y = canvas.coords(image_id)
        new_w = max(1, int(original_image.width * zoom_factor))
        new_h = max(1, int(original_image.height * zoom_factor))
        resized = original_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        tk_img = ImageTk.PhotoImage(resized)
        inserted_image.clear()
        inserted_image.append(tk_img)
        canvas.itemconfig(image_id, image=tk_img)
        canvas.coords(image_id, x, y)

def pan_left(e): canvas.xview_scroll(-1, "units")
def pan_right(e): canvas.xview_scroll(1, "units")
def pan_up(e): canvas.yview_scroll(-1, "units")
def pan_down(e): canvas.yview_scroll(1, "units")

window.bind("<Up>", pan_down)
window.bind("<Down>", pan_up)
window.bind("<Left>", pan_left)
window.bind("<Right>", pan_right)
window.bind_all("<MouseWheel>", incre_scale)
window.bind("<Control-plus>", zoom_in)
window.bind("<Control-equal>", zoom_in)
window.bind("<Control-minus>", zoom_out)
window.bind("<Control-z>", lambda e: undo())
window.bind("<Control-y>", lambda e: redo())
window.bind("<Control-s>", lambda e: SaveImage())
window.bind("<Control-a>", lambda e: clear())
window.bind("<Control-p>", lambda e: usePencil())
window.bind("<Control-e>", lambda e: useEraser())
window.bind("<Control-c>", lambda e: selectcolor())
window.bind("<Key-v>", lambda e: toggle_mic())

# ---------------------------------------- Footer ----------------------------------------
status_frame = ctk.CTkFrame(frameFoot, fg_color=FOOTER_BG)
status_frame.pack(side="left", padx=16, pady=6)
ctk.CTkLabel(status_frame, text="🎨 Paint Studio v1.0", font=("Segoe UI", 11, "bold"),
             text_color=ACCENT_TEAL).pack(side="left", padx=(0,20))
ctk.CTkFrame(status_frame, fg_color=TOOLBAR_BORDER, width=1, height=20).pack(side="left", padx=8)
status_info = ctk.CTkLabel(status_frame, text="", font=("Segoe UI", 10), text_color=TEXT_DIM)
status_info.pack(side="left", padx=8)
def update_status(*args):
    status_info.configure(text=f"Brush: {stroke_size.get()}px  |  Color: {stroke_color.get().upper()}")
stroke_size.trace_add("write", update_status)
stroke_color.trace_add("write", update_status)
update_status()
ctk.CTkFrame(status_frame, fg_color=TOOLBAR_BORDER, width=1, height=20).pack(side="left", padx=8)
ctk.CTkLabel(status_frame, text="Ctrl+Z Undo  |  Ctrl+S Save  |  V Voice AI",
             font=("Segoe UI", 9), text_color=TEXT_DIM).pack(side="left", padx=6)

# Zoom controls
zoom_pct = tk.StringVar(value="100%")
def update_zoom_label(val=None): zoom_pct.set(f"{int(zoom_factor*100)}%")
zoomSlider = ctk.CTkSlider(frameFoot, from_=10, to=200, number_of_steps=190,
                           command=slider_zoom, progress_color=ACCENT_TEAL,
                           button_color=ACCENT_CORAL, width=160)
zoomSlider.set(100)
zoomSlider.pack(side="right", padx=(4,20), pady=8)
ctk.CTkLabel(frameFoot, textvariable=zoom_pct, font=("Segoe UI",11,"bold"),
             text_color=ACCENT_TEAL, width=50).pack(side="right", padx=4)
zoomOutBtn = ctk.CTkButton(frameFoot, text="−", font=("Segoe UI",16,"bold"), width=32, height=30,
                           corner_radius=8, fg_color="#0F2027", hover_color=HOVER_COLOR,
                           command=zoom_out)
zoomOutBtn.pack(side="right", padx=3, pady=6)
zoomInBtn = ctk.CTkButton(frameFoot, text="+", font=("Segoe UI",16,"bold"), width=32, height=30,
                          corner_radius=8, fg_color="#0F2027", hover_color=HOVER_COLOR,
                          command=zoom_in)
zoomInBtn.pack(side="right", padx=3, pady=6)
ctk.CTkLabel(frameFoot, text="ZOOM", font=("Segoe UI",10,"bold"),
             text_color=TEXT_DIM).pack(side="right", padx=(8,2))

# ---------------------------------------- Exit handler ----------------------------------------
def on_closing():
    global Ai_Mode
    Ai_Mode = False
    window.quit()
    window.destroy()
window.protocol("WM_DELETE_WINDOW", on_closing)

if __name__ == "__main__":
    show_welcome_screen()
    try:
        window.mainloop()
    except tk.TclError:
        pass