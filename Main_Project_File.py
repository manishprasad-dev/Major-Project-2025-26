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

ctk.set_appearance_mode("Dark")   # "Light" or "Dark"
ctk.set_default_color_theme("blue") # or "dark-blue", "green"

# ==================== WELCOME / SPLASH SCREEN ====================
def show_welcome_screen():
    """
    Standalone splash screen using a plain tk.Tk window.
    Runs its own event loop, then destroys itself — main app starts after.
    """
    splash = tk.Tk()
    splash.overrideredirect(True)   # borderless
    splash.resizable(False, False)
    splash.configure(bg="#134B40")

    # Center on screen
    W, H = 700, 420
    sw = splash.winfo_screenwidth()
    sh = splash.winfo_screenheight()
    splash.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")

    # ---- Top accent bar ----
    tk.Frame(splash, bg="#EF6262", height=6).pack(fill="x", side="top")

    # ---- Paint emoji icon ----
    tk.Label(splash, text="🎨", font=("Segoe UI Emoji", 72),
             bg="#134B40", fg="#FFFFFF").pack(pady=(28, 4))

    # ---- App title ----
    tk.Label(splash, text="Paint Studio",
             font=("Segoe UI", 36, "bold"),
             bg="#134B40", fg="#FFFFFF").pack(pady=(0, 4))

    # ---- Subtitle ----
    tk.Label(splash, text="Your creative canvas — draw, sketch, and express.",
             font=("Segoe UI", 13),
             bg="#134B40", fg="#A8D5CD").pack(pady=(0, 4))

    # ---- Team / version ----
    tk.Label(splash, text="v1.0  ·  By Ricky Singh, Arun Shaw & Manish Kumar Prasad",
             font=("Segoe UI", 10),
             bg="#134B40", fg="#6BA297").pack(pady=(0, 16))

    # ---- Progress bar (drawn on a Canvas manually) ----
    bar_canvas = tk.Canvas(splash, width=420, height=14,
                           bg="#1f6b5a", highlightthickness=0)
    bar_canvas.pack(pady=(0, 6))
    bar_fill = bar_canvas.create_rectangle(0, 0, 0, 14, fill="#EF6262", width=0)

    loading_var = tk.StringVar(value="Initializing…")
    tk.Label(splash, textvariable=loading_var,
             font=("Segoe UI", 11),
             bg="#134B40", fg="#A8D5CD").pack()

    # ---- Bottom accent bar ----
    tk.Frame(splash, bg="#EF6262", height=6).pack(fill="x", side="bottom")

    # ---- Animation ----
    steps = 60
    messages = {0: "Initializing…", 15: "Loading tools…",
                30: "Setting up canvas…", 45: "Almost ready…", 58: "Welcome!"}

    def animate(step=0):
        if step <= steps:
            fill_w = int((step / steps) * 420)
            bar_canvas.coords(bar_fill, 0, 0, fill_w, 14)
            if step in messages:
                loading_var.set(messages[step])
            splash.after(35, animate, step + 1)
        else:
            window.deiconify()  # Show Paint app
            splash.destroy()   # close splash → main app appears

    animate()
    splash.mainloop()   # blocks here until splash.destroy() is called
# ==================== END WELCOME SCREEN ====================

window = ctk.CTk()
window.withdraw()
appicon = tk.PhotoImage(file="Icons/App_Icon.png")
window.iconphoto(False , appicon)

window.title("Paint")
window.geometry("1280x768")
sound_on=True#-->Default Sound state

#! Importing Module Function
icons = load_icons(window)
sound = SoundManager()

activeMenuWidgetBackground = "#FFFFFF" 
hoverMenuWidgetBackground = "#F87E7E"
frameTwoBackgroudColor = "#FFFFFF"

toolbarHoverColor = "#FC9163"

frameFootBackgroundColor = "#6BA297"
# ------------------------------------------Parent-Frame-Section-Open----------------------------------------------------------+
menuFrame = ctk.CTkFrame(master= window , fg_color= activeMenuWidgetBackground , height=50)
frameOne = ctk.CTkFrame(master = window  ,fg_color = frameTwoBackgroudColor)
frameFoot = ctk.CTkFrame(master = window,fg_color = "#EF6262",height=40)

# Horizontal container that holds slides panel + canvas area
frameMain = ctk.CTkFrame(master=window, fg_color="#FFFFFF")

# Slides sidebar (left)
slidesPanel = ctk.CTkFrame(master=frameMain, fg_color="#c0e3f8", width=130)
slidesPanel.pack(side="left", fill="y" , padx=(30,0), pady=30)
slidesPanel.pack_propagate(False)

# Canvas area (right)
frameTwo = ctk.CTkFrame(master=frameMain, fg_color="#F87474")
frameTwo.pack(side="left", fill="both", expand=True)

menuFrame.pack(side = "top" , fill = "x") 
frameOne.pack(side = "top", fill = "x")
frameOne.pack_propagate(False)
frameMain.pack(side="top", fill="both", expand=True)

frameFoot.pack(side="bottom", fill="x")
frameFoot.pack_propagate(False)
#------------------------------------Global-Variables-------------------------------------------------------------------
shape=""
preview_shape=""
undo_stack=[]      # Stores item IDs for undo
redo_stack=[]      # Stores item IDs for redo
stroke_color = tk.StringVar(value="white")
global current_line# 1= solid, 2=Dashed, 3=Dotted
current_line=1
insert_image=None
image_on_canvas=None
inserted_image=[]
original_image=None
image_id=None
current_pil_image=None
canvas_virtual_size=100000
pencil_select=0

start_AI_is_running=False 
Ai_Mode=False

# ===================== SLIDES GLOBAL VARIABLES =====================
slides_data = []          # list of dicts: {"undo": [], "redo": [], "items": []}
current_slide_index = 0   # which slide is active
slide_thumbnail_labels = []  # CTkLabel widgets for thumbnails
slides_panel_visible = True
# ==================================================================
# ------------------------------------------GlobalVariable----------------------------------------------------------+


#-------------------------------------------Camera-Close-----------------------------------------------------------------------------
# !-------------------------------------------Menu-Bar----------------------------------------------------------------------+
menuToolFrame = ctk.CTkFrame(master= menuFrame , fg_color=activeMenuWidgetBackground)
menuToolFrame.pack(side = "left" , padx = 10)

HelpSettingFrame=ctk.CTkFrame(master = menuFrame ,fg_color=activeMenuWidgetBackground)
HelpSettingFrame.pack(side = "right" )
def SaveImage():
    if sound_on and not start_AI_is_running:
        sound.play("Save_Sound")
    filelocation= filedialog.asksaveasfilename(defaultextension="jpg")
    x=window.winfo_rootx()+35
    y=window.winfo_rooty()+250
    img = ImageGrab.grab(bbox=(x,y,x+1340,y+640))
    img.save(filelocation)
    if img.save:
        if sound_on:
            sound.play("ImageSaved_Sound")
    if sound_on:
        window.after(2000,lambda:sound.play("OpenImage_Sound"))
    showImage = messagebox.askyesno("Paint App", "Do you want open image?")
    
    print(showImage)
    if showImage:
        img.show()
    
def saveImageEvent():
    SaveImage()  

def clear() :
    global undo_stack, redo_stack
    if sound_on and not start_AI_is_running:
        sound.play("clear_Sound")
    if messagebox.askokcancel("Warning!", "Do you want to clear everything?"):
        canvas.delete('all')
        # Clear undo/redo stacks to prevent invalid item IDs
        undo_stack.clear()
        redo_stack.clear()
        # Also clear the saved state of the current slide
        if slides_data:
            slides_data[current_slide_index]["items"] = []
            slides_data[current_slide_index]["undo"] = []
            slides_data[current_slide_index]["redo"] = []
        if sound_on:
            sound.play("EverythingCleared_Sound")

def ClearAllEvent():
    clear()  
def undo():
    if undo_stack:
        last_item = undo_stack.pop()
        canvas.itemconfig(last_item, state='hidden')
        redo_stack.append(last_item)

def redo():
    global undo_stack, redo_stack
    if redo_stack:
        item_id = redo_stack.pop()
        canvas.itemconfig(item_id, state='normal')
        undo_stack.append(item_id)

def toggle_sound():
    global sound_on
    sound_on= not sound_on
    if sound_on:
        sound_button.configure(image=icons["sound_on"])
        if sound_on:
            sound.play("SoundOn_Sound")
    else :
        sound_button.configure(image=icons["sound_off"])
        sound.play("SoundOff_Sound")

def add_text_window():
    tw = ctk.CTkToplevel(window)
    tw.title("Add Text — Paint Studio")
    tw.geometry("540x320")
    tw.resizable(False, False)
    tw.configure(fg_color="#0F2027")

    ctk.CTkFrame(tw, fg_color="#1B4332", height=54, corner_radius=0).pack(fill="x")
    ctk.CTkLabel(tw, text="✏  Add Text to Canvas", font=("Segoe UI", 14, "bold"),
                 text_color="#2EC4B6").place(x=18, y=14)
    ctk.CTkFrame(tw, fg_color="#2EC4B6", height=2).pack(fill="x")

    body = ctk.CTkFrame(tw, fg_color="#0F2027")
    body.pack(fill="both", expand=True, padx=28, pady=20)

    ctk.CTkLabel(body, text="Text:", font=("Segoe UI", 11),
                 text_color="#C8E6C9").grid(row=0, column=0, sticky="w", pady=6)

    global textofentry, entry
    textofentry = tk.StringVar(value="Your text here")
    entry = ctk.CTkEntry(body, textvariable=textofentry, width=360,
                         fg_color="#0F3460", border_color="#1982C4",
                         text_color="white", font=("Segoe UI", 12))
    entry.grid(row=0, column=1, columnspan=2, sticky="ew", padx=(10,0), pady=6)

    global x_slider, y_slider
    ctk.CTkLabel(body, text="X Position:", font=("Segoe UI", 11),
                 text_color="#C8E6C9").grid(row=1, column=0, sticky="w", pady=8)
    x_slider = ctk.CTkSlider(body, from_=0, to=1280, width=260,
                              progress_color="#2EC4B6", button_color="#EF6262")
    x_slider.set(200)
    x_slider.grid(row=1, column=1, sticky="w", padx=(10,0))

    ctk.CTkLabel(body, text="Y Position:", font=("Segoe UI", 11),
                 text_color="#C8E6C9").grid(row=2, column=0, sticky="w", pady=8)
    y_slider = ctk.CTkSlider(body, from_=0, to=800, width=260,
                              progress_color="#2EC4B6", button_color="#EF6262")
    y_slider.set(125)
    y_slider.grid(row=2, column=1, sticky="w", padx=(10,0))

    ctk.CTkButton(body, text="  Place Text  ", command=add_Text,
                  fg_color="#1982C4", hover_color="#EF6262",
                  corner_radius=10, font=("Segoe UI", 12, "bold")
                  ).grid(row=3, column=1, sticky="w", pady=16, padx=(10,0))

    ctk.CTkFrame(tw, fg_color="#2EC4B6", height=2).pack(fill="x", side="bottom")

def help_window():
    hw = ctk.CTkToplevel(window)
    hw.title("Help — Paint Studio")
    hw.geometry("560x640")
    hw.resizable(False, False)
    hw.configure(fg_color="#0F2027")

    # Header
    hdr = ctk.CTkFrame(hw, fg_color="#1B4332", height=70, corner_radius=0)
    hdr.pack(fill="x")
    ctk.CTkLabel(hdr, text="📖  Paint Studio Help", font=("Segoe UI", 18, "bold"),
                 text_color="#2EC4B6").pack(pady=18)
    ctk.CTkFrame(hw, fg_color="#2EC4B6", height=2).pack(fill="x")

    # Scrollable body
    body = scrolledtext.ScrolledText(
        hw, wrap=tk.WORD, font=("Segoe UI", 11),
        bg="#0D1B2A", fg="#D0E8E0",
        insertbackground="white",
        selectbackground="#1982C4",
        relief="flat", padx=20, pady=16,
    )
    body.pack(expand=True, fill="both", padx=0, pady=0)

    sections = [
        ("🚀  Getting Started", [
            "Select a tool from the toolbar (Brush, Eraser, etc.).",
            "Choose a color from the palette or open the color picker.",
            "Left-click and drag on the canvas to draw freehand.",
            "Right-click and drag to draw shapes.",
        ]),
        ("🛠  Tools", [
            "Pencil / Brush  — freehand drawing.",
            "Eraser          — paint over with white (or any color).",
            "Text (T)        — place text anywhere on canvas.",
            "Insert Image    — drag and reposition an image.",
            "Camera          — gesture-controlled drawing.",
            "Microphone      — voice command mode.",
        ]),
        ("⌨  Keyboard Shortcuts", [
            "Ctrl + Z   →  Undo",
            "Ctrl + Y   →  Redo",
            "Ctrl + S   →  Save image",
            "Ctrl + A   →  Clear canvas",
            "Ctrl + C   →  Open color picker",
            "Ctrl + P   →  Pencil",
            "Ctrl + E   →  Eraser",
            "V          →  Toggle voice AI",
            "Ctrl + +/−  →  Zoom in / out",
            "Arrow Keys →  Pan canvas",
        ]),
        ("💡  Tips", [
            "Scroll the mouse wheel to adjust stroke size.",
            "Use the zoom slider in the footer to zoom in/out.",
            "Hold right-click and drag to draw perfect shapes.",
        ]),
    ]

    for title, items in sections:
        body.insert(tk.END, f"\n{title}\n", "section")
        body.insert(tk.END, "─" * 56 + "\n", "rule")
        for item in items:
            body.insert(tk.END, f"  →  {item}\n", "item")
        body.insert(tk.END, "\n")

    body.tag_config("section", foreground="#2EC4B6", font=("Segoe UI", 13, "bold"))
    body.tag_config("rule",    foreground="#1B4332")
    body.tag_config("item",    foreground="#C8E6C9")
    body.config(state="disabled")

    # Footer
    ctk.CTkFrame(hw, fg_color="#2EC4B6", height=2).pack(fill="x", side="bottom")
    ctk.CTkLabel(hw, text="© 2025 Ricky Singh · Arun Shaw · Manish Kumar Prasad",
                 font=("Segoe UI", 9), text_color="#3d7a6e").pack(side="bottom", pady=6)

def aboutus_window():
    aw = ctk.CTkToplevel(window)
    aw.title("About — Paint Studio")
    aw.geometry("520x580")
    aw.resizable(False, False)
    aw.configure(fg_color="#0F2027")

    hdr = ctk.CTkFrame(aw, fg_color="#1B4332", height=110, corner_radius=0)
    hdr.pack(fill="x")
    ctk.CTkLabel(hdr, text="🎨", font=("Segoe UI Emoji", 44),
                 text_color="white").pack(pady=(20, 5))
    ctk.CTkLabel(hdr, text="Paint Studio", font=("Segoe UI", 20, "bold"),
                 text_color="#2EC4B6").pack()
    ctk.CTkFrame(aw, fg_color="#2EC4B6", height=2).pack(fill="x")

    body = ctk.CTkFrame(aw, fg_color="#0F2027")
    body.pack(fill="both", expand=True, padx=30, pady=24)

    ctk.CTkLabel(body, text="v1.0  ·  Built with Python & CustomTkinter",
                 font=("Segoe UI", 11), text_color="#7ECDC4").pack(pady=(0, 12))
    ctk.CTkLabel(body,
                 text="A modern, feature-rich paint application with voice AI,\n"
                      "gesture control, and a clean dark-themed interface.",
                 font=("Segoe UI", 11), text_color="#C8E6C9",
                 justify="center", wraplength=400).pack(pady=(0, 20))

    feat_frame = ctk.CTkFrame(body, fg_color="#0F2027")
    feat_frame.pack(pady=(0, 20))
    for i, (f, c) in enumerate([("✏ Brush & Shapes","#6A4C93"),("🔊 Voice AI","#EF6262"),
                                  ("📷 Camera","#8AC926"),("↩ Undo/Redo","#1982C4")]):
        ctk.CTkLabel(feat_frame, text=f, font=("Segoe UI", 10, "bold"),
                     fg_color=c, text_color="white", corner_radius=12,
                     padx=12, pady=5).grid(row=i//2, column=i%2, padx=8, pady=5)

    ctk.CTkFrame(body, fg_color="#1B4332", height=1).pack(fill="x", pady=12)
    ctk.CTkLabel(body, text="👨‍💻  Developed By", font=("Segoe UI", 12, "bold"),
                 text_color="#2EC4B6").pack()
    for name in ["Ricky Singh", "Arun Kumar Ray", "Manish Kumar Prasad"]:
        ctk.CTkLabel(body, text=f"  •  {name}", font=("Segoe UI", 11),
                     text_color="#C8E6C9").pack()

    ctk.CTkFrame(aw, fg_color="#2EC4B6", height=2).pack(fill="x", side="bottom")
    ctk.CTkLabel(aw, text="© 2025 All Rights Reserved  ·  Thank you for using Paint Studio!",
                 font=("Segoe UI", 9), text_color="#3d7a6e").pack(side="bottom", pady=6)

def setting_window():
    sw = ctk.CTkToplevel(window)
    sw.title("Settings — Paint Studio")
    sw.geometry("560x460")
    sw.resizable(False, False)
    sw.configure(fg_color="#0F2027")

    ctk.CTkFrame(sw, fg_color="#1B4332", height=56, corner_radius=0).pack(fill="x")
    ctk.CTkLabel(sw, text="⚙  Settings", font=("Segoe UI", 16, "bold"),
                 text_color="#2EC4B6").place(x=24, y=16)
    ctk.CTkFrame(sw, fg_color="#2EC4B6", height=2).pack(fill="x")

    body = ctk.CTkFrame(sw, fg_color="#0F2027")
    body.pack(fill="both", expand=True, padx=32, pady=24)

    def _row(label, widget_fn, row):
        ctk.CTkLabel(body, text=label, font=("Segoe UI", 11),
                     text_color="#C8E6C9", anchor="w", width=26).grid(
            row=row, column=0, sticky="w", pady=10)
        widget_fn(row)

    # Theme toggle
    theme_var = tk.StringVar(value="Dark")
    def _theme(row):
        f = ctk.CTkFrame(body, fg_color="#0F2027")
        f.grid(row=row, column=1, sticky="w")
        for val, color in [("Dark","#1982C4"), ("Light","#EF6262")]:
            ctk.CTkRadioButton(f, text=val, variable=theme_var, value=val,
                               fg_color=color, hover_color=color,
                               text_color="#C8E6C9").pack(side="left", padx=12)
    _row("Theme:", _theme, 0)

    # Canvas background
    canvas_bg_var = tk.StringVar(value="#FAFAFA")
    def _cbg(row):
        ctk.CTkEntry(body, textvariable=canvas_bg_var, width=150,
                     fg_color="#0F3460", border_color="#1982C4",
                     text_color="white").grid(row=row, column=1, sticky="w")
    _row("Canvas Background:", _cbg, 1)

    # Default stroke size
    default_size_var = tk.IntVar(value=5)
    def _size(row):
        ctk.CTkSlider(body, from_=1, to=50, variable=default_size_var,
                      width=220, progress_color="#2EC4B6",
                      button_color="#EF6262").grid(row=row, column=1, sticky="w")
    _row("Default Stroke Size:", _size, 2)

    ctk.CTkFrame(body, fg_color="#1B4332", height=1).grid(row=3, columnspan=2, sticky="ew", pady=18)
    ctk.CTkButton(body, text="Apply Changes", fg_color="#1982C4", hover_color="#EF6262",
                  corner_radius=10, width=130, height=34,
                  command=lambda: canvas.config(bg=canvas_bg_var.get())
                  ).grid(row=4, column=1, sticky="w")

    ctk.CTkFrame(sw, fg_color="#2EC4B6", height=2).pack(fill="x", side="bottom")


saveImageButton = ctk.CTkButton(
    master=menuToolFrame,
    text=None,
    image= icons["save"] ,
    fg_color=activeMenuWidgetBackground,
    hover_color=hoverMenuWidgetBackground,
    command=SaveImage,
    width=0,
)

clearImageButton = ctk.CTkButton(
    master=menuToolFrame,
    text=None,
    image= icons["clear"] ,
    fg_color=activeMenuWidgetBackground,
    hover_color=hoverMenuWidgetBackground,
    command=clear,
    width=0,
)

undo_button = ctk.CTkButton(
    master=menuToolFrame,
    text=None,
    image= icons["undo"] ,
    fg_color=activeMenuWidgetBackground,
    hover_color=hoverMenuWidgetBackground,  
    command=undo,
    width=0,
)

redo_button = ctk.CTkButton(
    master=menuToolFrame,
    text=None,
    image= icons["redo"] ,
    fg_color=activeMenuWidgetBackground,
    hover_color=hoverMenuWidgetBackground,  
    command=redo,
    width=0,
)

sound_button = ctk.CTkButton(
    master=menuToolFrame,
    text=None,
    image= icons["sound_on"] ,
    fg_color=activeMenuWidgetBackground,
    hover_color=hoverMenuWidgetBackground,  
    command=toggle_sound,
    width=0,
)

helpButton = ctk.CTkButton(
    master=HelpSettingFrame,
    text=None,
    image= icons["help"],
    text_color="black",
    fg_color=activeMenuWidgetBackground,
    hover_color=hoverMenuWidgetBackground,  
    command=help_window,
    width=0
)

settingButton = ctk.CTkButton(
    master=HelpSettingFrame,
    text=None,
    image= icons["settings"],
    text_color="black",
    fg_color=activeMenuWidgetBackground,
    hover_color=hoverMenuWidgetBackground,  # optional: slightly darker on hover
    command=setting_window,
    width=0
)

aboutButton = ctk.CTkButton(
    master=HelpSettingFrame,
    text=None,
    image= icons["about"],
    text_color="black",
    fg_color=activeMenuWidgetBackground,
    hover_color=hoverMenuWidgetBackground,  # optional: slightly darker on hover
    command=aboutus_window,
    width=0
)

# Menu Button Placements
saveImageButton.grid(row=0, column=0, padx=5)
clearImageButton.grid(row=0, column=1, padx=5)
undo_button.grid(row=0, column=2, padx=5)
redo_button.grid(row=0, column=3, padx=5)
sound_button.grid(row=0, column=4, padx=5)
helpButton.pack(side="left", padx=0)
settingButton.pack(side="left", padx=0)
aboutButton.pack(side="left", padx=0)
# !-------------------------------------------Menu-Bar----------------------------------------------------------------------+

# ! Color Frame
# colorFrame=tk.LabelFrame(frameOne ,text="Colors", height=170, width=230 , borderwidth=0 ,relief="sunken" ,bg="#D6F5EF")
# colorFrame.place(x=545,y=45)

# ! Camera Functionality
def camera_draw(x1, y1, x2, y2):
    print("Putting In Queue:", x1, y1, x2, y2)
    camera_queue.put((x1, y1, x2, y2))

def draw_on_canvas(x1, y1, x2, y2):
    item = canvas.create_line(
        x1,
        y1,
        x2,
        y2,
        fill=stroke_color.get(),
        width=stroke_size.get(),
        capstyle=tk.ROUND,
        smooth=True,
        splinesteps=36,
        dash=get_line_dash_pattern()
    )

    undo_stack.append(item)

# !Frame One Tools Functionality Section
def selectcolor():
    global stroke_color
    global current_color_label
    if sound_on:
        sound.play("selectcolor_Sound")
    selectedcolor = colorchooser.askcolor("red" , title="Select Color")
    stroke_color.set(selectedcolor[1])
    # current_color_label.config(bg=selectedcolor[1])
def camera():
    if sound_on and not start_AI_is_running:
        sound.play("CameraOpen_Sound")

    actions = {
        "save": SaveImage,
        "clear": clear,
        "mute": toggle_sound,
        "text": addText,
        "draw": camera_draw

    }

    threading.Thread(target=start_camera, args=(sound, actions)).start()

def add_text_window():
    tw = ctk.CTkToplevel(window)
    tw.title("Add Text — Paint Studio")
    tw.geometry("540x320")
    tw.resizable(False, False)
    tw.configure(fg_color="#0F2027")

    ctk.CTkFrame(tw, fg_color="#1B4332", height=54, corner_radius=0).pack(fill="x")
    ctk.CTkLabel(tw, text="✏  Add Text to Canvas", font=("Segoe UI", 14, "bold"),
                 text_color="#2EC4B6").place(x=18, y=14)
    ctk.CTkFrame(tw, fg_color="#2EC4B6", height=2).pack(fill="x")

    body = ctk.CTkFrame(tw, fg_color="#0F2027")
    body.pack(fill="both", expand=True, padx=28, pady=20)

    ctk.CTkLabel(body, text="Text:", font=("Segoe UI", 11),
                 text_color="#C8E6C9").grid(row=0, column=0, sticky="w", pady=6)

    global textofentry, entry
    textofentry = tk.StringVar(value="Your text here")
    entry = ctk.CTkEntry(body, textvariable=textofentry, width=360,
                         fg_color="#0F3460", border_color="#1982C4",
                         text_color="white", font=("Segoe UI", 12))
    entry.grid(row=0, column=1, columnspan=2, sticky="ew", padx=(10,0), pady=6)

    global x_slider, y_slider
    ctk.CTkLabel(body, text="X Position:", font=("Segoe UI", 11),
                 text_color="#C8E6C9").grid(row=1, column=0, sticky="w", pady=8)
    x_slider = ctk.CTkSlider(body, from_=0, to=1280, width=260,
                              progress_color="#2EC4B6", button_color="#EF6262")
    x_slider.set(200)
    x_slider.grid(row=1, column=1, sticky="w", padx=(10,0))

    ctk.CTkLabel(body, text="Y Position:", font=("Segoe UI", 11),
                 text_color="#C8E6C9").grid(row=2, column=0, sticky="w", pady=8)
    y_slider = ctk.CTkSlider(body, from_=0, to=800, width=260,
                              progress_color="#2EC4B6", button_color="#EF6262")
    y_slider.set(125)
    y_slider.grid(row=2, column=1, sticky="w", padx=(10,0))

    ctk.CTkButton(body, text="  Place Text  ", command=add_Text,
                  fg_color="#1982C4", hover_color="#EF6262",
                  corner_radius=10, font=("Segoe UI", 12, "bold")
                  ).grid(row=3, column=1, sticky="w", pady=16, padx=(10,0))

    ctk.CTkFrame(tw, fg_color="#2EC4B6", height=2).pack(fill="x", side="bottom")

def toggle_mic():
    global Ai_Mode , start_AI_is_running , sound_on
    Ai_Mode= not Ai_Mode
    sound_on=True
    sound_button.configure(image=icons["sound_on"])
    if Ai_Mode:
        useMicButton.configure(image=icons["mic_open"])
        if not start_AI_is_running:
            start_AI()
            start_AI_is_running=True
    else :
        useMicButton.configure(image=icons["mic"])
        ptt_stop()
        start_AI_is_running=False

# ? SubFrames Of Frame One

frameOne.grid_rowconfigure(0, weight=1)

toolFrame = ctk.CTkFrame(
    master = frameOne,
    height=100,
    width=150,
    fg_color=frameTwoBackgroudColor,
    border_width=2,
    border_color="black"
)
toolFrame.grid(row=0, column=0, padx=10, pady=10)

lineTypeFrame = ctk.CTkFrame(
    master=frameOne,
    # text="Linetypes",
    height=100,
    width=150,
    fg_color=frameTwoBackgroudColor,
    border_width=2,
    border_color="black"
)
lineTypeFrame.grid(row=0, column=1, padx=10, pady=10)

shapeFrame = ctk.CTkFrame(
    master=frameOne,
    height=100,
    width=220,
    fg_color=frameTwoBackgroudColor,
    border_width=2,
    border_color="black",
    # orientation="vertical",
)
shapeFrame.grid(row=0, column=2, padx=10, pady=10)

colorFrame = ctk.CTkFrame(
    master=frameOne,
    height=100,
    # width=150,
    fg_color=frameTwoBackgroudColor,
    border_width=2,
    border_color="black"
)
colorFrame.grid(row=0, column=3, padx=10, pady=10)

addColorFrame = ctk.CTkFrame(
    master = frameOne,
    fg_color=frameTwoBackgroudColor,
    border_width=2,
    border_color="black",    
)
addColorFrame.grid(row=0, column=4 , padx = 20)

# camera + mic functionality can used from here
advToolFrame = ctk.CTkFrame(
    master = frameOne,
    fg_color=frameTwoBackgroudColor,
    border_width=2,
    border_color="black",
)
advToolFrame.grid(row=0, column=5)

# micFrame = ctk.CTkFrame(
#     frameOne,
#     fg_color=frameTwoBackgroudColor
# )
# micFrame.grid(row=0, column=6, padx=10, pady=10)

toolFrame.grid_propagate(False)
lineTypeFrame.grid_propagate(False)
shapeFrame.grid_propagate(False)
colorFrame.grid_propagate(False)

#! ---------------------------------------------------------------------------------------------------------------

def usePencil():
    global pencil_select
    global current_line

    pencil_select=pencil_select+1
    if sound_on and not start_AI_is_running :
        if pencil_select !=1:
            sound.play("Pencil_Sound")
            stroke_color.get()
        if pencil_select==1:
            window.after(6000, lambda:sound.play("DefaultBlack_Sound"))
            stroke_color.set("black")
            # current_color_label.config(bg="Black")

    canvas.config(cursor = "crosshair")
    SolidLineButton.configure(fg_color="white")
    DashedLineButton.configure(fg_color="#E5F0EF")
    DottedLineButton.configure(fg_color="#E5F0EF")
    current_line=1
    
def useEraser():
    if sound_on and not start_AI_is_running:
        sound.play("Eraser_Sound")
    stroke_color.set("white")
    # current_color_label.config(bg="white")
    canvas.config(cursor = "dotbox")

def addText():
    add_text_window()

pencilIcon = ctk.CTkButton(master = toolFrame , text="",fg_color=frameTwoBackgroudColor , hover_color=toolbarHoverColor,width=25, height=25 , image= icons["pencil"], command=usePencil)
pencilIcon.place(x = 5 , y = 5 )

# Rubber Button/Icon
eraserIcon = ctk.CTkButton(master = toolFrame , text="",fg_color=frameTwoBackgroudColor , hover_color=toolbarHoverColor,width=25, height=25 , image=icons["eraser"], command= useEraser)
eraserIcon.place(x = 5 , y = 40)

# Font Icon
fontIcon = ctk.CTkButton(master = toolFrame , text="",fg_color=frameTwoBackgroudColor , hover_color=toolbarHoverColor,width=25, height=25 , image=icons["font"],command= addText)
fontIcon.place(x = 40 , y = 5)

# Fill Icon+
fillIcon = ctk.CTkButton(master = toolFrame , text="", fg_color=frameTwoBackgroudColor ,hover_color=toolbarHoverColor,width=25, height=25, image=icons["fill"])
fillIcon.place(x=80, y = 5)
#! ----------------------------------------------------------------------------------------------------

#! ----------------------------------------------Line-Type-Start--------------------------------------------------------------
def solidline():
    global current_line
    current_line=1
    if sound_on:
        sound.play("SolidLineResponse")
    SolidLineButton.configure(fg_color="white")
    DashedLineButton.configure(fg_color="#E5F0EF")
    DottedLineButton.configure(fg_color="#E5F0EF")
    canvas.config(cursor = "crosshair")


def DashedLine():
    global current_line
    current_line=2
    if sound_on:
        sound.play("DashedLineResponse")
    DashedLineButton.configure(fg_color="white")
    DottedLineButton.configure(fg_color="#E5F0EF")
    SolidLineButton.configure(fg_color="#E5F0EF")
    canvas.config(cursor = "boat")


def DottedLine():
    global current_line
    current_line=3
    if sound_on:
        sound.play("DottedLineResponse")
    DottedLineButton.configure(fg_color="white")
    DashedLineButton.configure(fg_color="#E5F0EF")
    SolidLineButton.configure(fg_color="#E5F0EF")
    canvas.config(cursor = "dot")

SolidLineButton=ctk.CTkButton(master=lineTypeFrame,text="━━━━",command=solidline,text_color="black",hover_color="white")
SolidLineButton.grid(row=1,column=0 , padx = 4,pady=3 )

DashedLineButton=ctk.CTkButton(master=lineTypeFrame,text="- - - - - - - -",command=DashedLine,text_color="black",hover_color="white")
DashedLineButton.grid(row=2,column=0 , padx = 4,pady=2 )

DottedLineButton=ctk.CTkButton(master=lineTypeFrame,text="................",command=DottedLine,text_color="black",hover_color="white")
DottedLineButton.grid(row=3,column=0 , padx = 4,pady=2 )
#! ----------------------------------------------Line-Type-End---------------------------------------------------------------


#!-------------------------------------Shape--Frame---Open--------------------------------------------------------------------------------------
def select_circle():
    global shape
    if sound_on and not start_AI_is_running:
        sound.play("Circle_Sound")
    shape = "circle"

def select_rectangle():
    global shape
    if sound_on and not start_AI_is_running:
        sound.play("Rectangle_Sound")
    shape = "rectangle"

def select_line():
    global shape
    if sound_on and not start_AI_is_running:
        sound.play("Line_Sound")
    shape = "line"

def select_triangle():
    global shape
    if sound_on and not start_AI_is_running:
        sound.play("Triangle_Sound")
    shape = "triangle"

def select_polygon():
    global shape
    if sound_on and not start_AI_is_running:
        sound.play("Pentagon_Sound")
    shape = "polygon"

def select_arc():
    global shape
    if sound_on:
        sound.play("ArcResponse")
    shape = "arc"

def select_heart():
    global shape
    if sound_on and not start_AI_is_running:
        sound.play("Heart_Sound")
    shape = "heart"

def select_arrow():
    global shape
    if sound_on and not start_AI_is_running:
        sound.play("Arrow_Sound")
    shape = "arrow"
buttons = [
    (select_circle,   icons["circle"]),
    (select_rectangle,icons["rectangle"]),
    (select_line,     icons["line"]),
    (select_triangle, icons["triangle"]),
    (select_polygon,  icons["polygon"]),
    (select_arc,      icons["arc"]),
    (select_heart,    icons["heart"]),
    (select_arrow,    icons["arrow"]),
]

for index, (command, icon) in enumerate(buttons):
    ctk.CTkButton(
        master=shapeFrame,
        text=None,
        image=icon,
        command=command,
        fg_color="transparent",
        hover_color=hoverMenuWidgetBackground,
        width=40,
        height=40
    ).grid(
        row=index // 6,   # 2 rows
        column=index % 6, # 6 columns
        padx=2,
        pady=2
    )


#! ------------------------------------Shape--Frame---close--------------------------------------------------------------------------------------

#! ------------------------------------Color-Frame-Open--------------------------------------------------------------------------------------

colors = [
"#FF595E","#FFCA3A","#8AC926",
"#1982C4","#6A4C93",
"#000000","#FFFFFF","#808080",
"#FF9F1C","#2EC4B6"
]
for index, color in enumerate(colors):
    row = index // 5      # 0 or 1
    col = index % 5       # 0 to 4

    ctk.CTkButton(
        master=colorFrame,
        text=None,
        fg_color=color.lower(),
        hover_color=color.lower(),
        width=25,
        height=25,
        corner_radius=12,
        command=lambda c=color: stroke_color.set(c.lower())
    ).grid(row=row, column=col, padx=7, pady=5)

# more add color option
colorBoxButton= ctk.CTkButton(master = addColorFrame ,text=None, command=selectcolor , image= icons["select_color"] , fg_color=frameTwoBackgroudColor , hover_color="#FFFFFF" , width=20 , height=20)
colorBoxButton.grid(row=0 , column=0 , padx=5, pady=5)

# shows the current selected color
current_color_label = tk.Label(
    addColorFrame,
    width=5,
    height=2,
    bg=stroke_color.get(),
    relief="solid",
    bd=1
)
# current_color_label = ctk.CTkLabel(
#     master = addColorFrame,
#     width=5,
#     height=2,
#     bg_color=stroke_color.get(),
#     fg_color=stroke_color.get(),
    
#     corner_radius=5
# )
current_color_label.grid(row=1, column=0, padx=10, pady=10)   

#! ------------------------------------Color-Frame-Close--------------------------------------------------------------------------------------

#! ------------------------------------Advance-Frame-Open--------------------------------------------------------------------------------------
openCameraButton = ctk.CTkButton(master = advToolFrame , text=None,image= icons["camera"],command=camera , fg_color=frameTwoBackgroudColor , hover_color=hoverMenuWidgetBackground)
openCameraButton.grid(row = 0 , column = 0,padx=5, pady=5)

useMicButton = ctk.CTkButton(master=advToolFrame,text=None,image=icons["mic"],command=toggle_mic  , fg_color=frameTwoBackgroudColor , hover_color=hoverMenuWidgetBackground)
useMicButton.grid(row = 1 , column = 0,padx=5, pady=5)
#! ------------------------------------Advance-Frame-Close--------------------------------------------------------------------------------------
#----------------------------------------------Line-Type------------------------------------------------------------------# ! Incremeants the left side scale 
stroke_size = tk.IntVar(value = 5)

scale= ctk.CTkSlider(master = window , from_=1, to=100 , orientation ="vertical" ,variable=stroke_size , height=300,progress_color="#CB77DF",button_color="#AF9AF7",fg_color="#F7F180")
scale.place(x =10 ,y = 200)
def incre_scale(event):
    global stroke_size
    if event.delta > 0 :
        res = stroke_size.get() + 1
        stroke_size.set(res)
    else:
        res = stroke_size.get() - 1
        stroke_size.set(res)


#---This will show stroke size-----------------------------------------------------------------------
#! IDk - 
size_label = ctk.CTkLabel(window, textvariable=stroke_size, bg_color="#FFFFFF" , width=2)
size_label.place(x=10, y=500)
#! IDk - 

def process_camera_queue():
    print("QUEUE LOOP", time.time())
    while not camera_queue.empty():
        print("Got item from queue")
        x1, y1, x2, y2 = camera_queue.get()

        item = canvas.create_line(
            x1,
            y1,
            x2,
            y2,
            fill=stroke_color.get(),
            width=stroke_size.get(),
            capstyle=tk.ROUND,
            smooth=True,
            splinesteps=36,
            dash=get_line_dash_pattern()
        )

        undo_stack.append(item)

    window.after(10, process_camera_queue)


# ==================== SLIDES PANEL SETUP ====================

# Header label for the panel
ctk.CTkLabel(
    slidesPanel, text="📑 Slides", font=("Segoe UI", 11, "bold"),
    text_color="#2EC4B6", fg_color="#FFFFFF", corner_radius=0
).pack(fill="x", pady=(6, 2), padx=4)

ctk.CTkFrame(slidesPanel, fg_color="#FDFFFF", height=2).pack(fill="x", padx=4, pady=(0, 6))

# Scrollable area for slide thumbnails
slides_scroll_frame = ctk.CTkScrollableFrame(
    slidesPanel, fg_color="#4fb3f6", scrollbar_button_color="#2EC4B6",
    scrollbar_button_hover_color="#EF6262"
)
slides_scroll_frame.pack(fill="both", expand=True, padx=4, pady=4)

def _serialize_canvas_items():
    """Save current canvas drawing state as a list of item specs."""
    items = []
    try:
        for item_id in canvas.find_all():
            itype = canvas.type(item_id)
            coords = canvas.coords(item_id)
            cfg = {}
            try:
                for key in ("fill", "outline", "width", "dash", "font", "text",
                            "arrow", "smooth", "splinesteps", "capstyle",
                            "start", "extent", "style", "state"):
                    try:
                        val = canvas.itemcget(item_id, key)
                        if val != "":
                            cfg[key] = val
                    except tk.TclError:
                        pass
            except Exception:
                pass
            items.append({"type": itype, "coords": coords, "cfg": cfg})
    except Exception:
        pass
    return items

def _restore_canvas_items(items):
    """Re-draw items onto the canvas from serialised list."""
    canvas.delete("all")
    undo_stack.clear()
    redo_stack.clear()
    for spec in items:
        itype = spec["type"]
        coords = spec["coords"]
        cfg = {k: v for k, v in spec["cfg"].items()
               if k not in ("state",)}  # skip state so items are visible
        try:
            if itype == "line":
                item = canvas.create_line(*coords, **cfg)
            elif itype == "oval":
                item = canvas.create_oval(*coords, **cfg)
            elif itype == "rectangle":
                item = canvas.create_rectangle(*coords, **cfg)
            elif itype == "polygon":
                item = canvas.create_polygon(*coords, **cfg)
            elif itype == "arc":
                item = canvas.create_arc(*coords, **cfg)
            elif itype == "text":
                item = canvas.create_text(*coords, **cfg)
            else:
                continue
            undo_stack.append(item)
        except Exception:
            pass

def _make_thumbnail(slide_index):
    """Render a small 110×70 thumbnail for the slide at slide_index."""
    size = (110, 70)
    img = Image.new("RGB", size, "white")
    # Draw a simple canvas-content preview using PostScript (best effort)
    try:
        if slide_index == current_slide_index:
            # Use live canvas
            ps = canvas.postscript(colormode="color", pagewidth=size[0], pageheight=size[1])
            import io, subprocess
            try:
                proc = subprocess.run(
                    ["gs", "-dQUIET", "-dNOPAUSE", "-dBATCH", "-dSAFER",
                     "-sDEVICE=png16m", f"-g{size[0]}x{size[1]}",
                     "-r72", "-sOutputFile=-", "-"],
                    input=ps.encode(), capture_output=True, timeout=2
                )
                if proc.returncode == 0 and proc.stdout:
                    img = Image.open(io.BytesIO(proc.stdout))
            except Exception:
                pass
    except Exception:
        pass
    return ImageTk.PhotoImage(img.resize(size, Image.LANCZOS))

def _make_simple_thumbnail(slide_index):
    """Create a plain colored thumbnail with slide number (no Ghostscript needed)."""
    w, h = 110, 70
    is_active = slide_index == current_slide_index
    bg_color = "#2EC4B6" if is_active else "#FFFFFF"
    img = Image.new("RGB", (w, h), bg_color)
    return ImageTk.PhotoImage(img)

def _build_slide_thumbnail_widget(slide_index):
    """Create one thumbnail card in the scroll frame."""
    card = ctk.CTkFrame(
        slides_scroll_frame,
        fg_color="#2EC4B6" if slide_index == current_slide_index else "#0d2b24",
        corner_radius=8, border_width=2,
        border_color="#2EC4B6" if slide_index == current_slide_index else "#1a5c4e"
    )
    card.pack(fill="x", pady=4, padx=2)

    # Thumbnail image area
    thumb_label = tk.Label(card, bg="#FFFFFF", relief="flat", cursor="hand2")
    thumb_label.pack(padx=4, pady=(4, 2))
    # Update thumbnail image
    _refresh_thumb_image(thumb_label, slide_index)

    # Slide number label
    ctk.CTkLabel(
        card,
        text=f"Slide {slide_index + 1}",
        font=("Segoe UI", 9, "bold"),
        text_color="#2EC4B6" if slide_index == current_slide_index else "#A8D5CD"
    ).pack(pady=(0, 2))

    # Delete button (don't show for slide 1 if only one slide)
    def _delete_slide(idx=slide_index):
        if len(slides_data) <= 1:
            messagebox.showinfo("Slides", "Cannot delete the only slide.")
            return
        if messagebox.askyesno("Delete Slide", f"Delete Slide {idx + 1}?"):
            global current_slide_index
            slides_data.pop(idx)
            new_idx = min(idx, len(slides_data) - 1)
            current_slide_index = new_idx
            _restore_canvas_items(slides_data[current_slide_index]["items"])
            _rebuild_slides_panel()

    del_btn = ctk.CTkButton(
        card, text="✕", width=20, height=16,
        fg_color="#EF6262", hover_color="#c0392b",
        font=("Segoe UI", 8, "bold"), corner_radius=4,
        command=_delete_slide
    )
    del_btn.pack(pady=(0, 4))

    # Click card to switch to this slide
    def _switch(event=None, idx=slide_index):
        switch_to_slide(idx)

    card.bind("<Button-1>", _switch)
    thumb_label.bind("<Button-1>", _switch)

    return card, thumb_label

_thumb_images = {}   # keep references so GC doesn't eat them

def _refresh_thumb_image(label, slide_index):
    """Put a plain-colour thumbnail on label."""
    w, h = 108, 65
    is_active = slide_index == current_slide_index
    bg = "#2EC4B6" if is_active else "#f0f0f0"
    img = Image.new("RGB", (w, h), bg)
    # Draw slide number as text
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    txt = str(slide_index + 1)
    draw.text((w//2 - 6, h//2 - 10), txt, fill="#134B40" if is_active else "#888888")
    tk_img = ImageTk.PhotoImage(img)
    _thumb_images[slide_index] = tk_img   # prevent GC
    label.configure(image=tk_img, width=w, height=h)

def _rebuild_slides_panel():
    """Destroy and re-create all thumbnail cards."""
    for widget in slides_scroll_frame.winfo_children():
        widget.destroy()
    _thumb_images.clear()
    for i in range(len(slides_data)):
        _build_slide_thumbnail_widget(i)

def switch_to_slide(idx):
    """Save current canvas state, then load the target slide."""
    global current_slide_index
    if idx == current_slide_index:
        return
    # Save current
    slides_data[current_slide_index]["items"] = _serialize_canvas_items()
    slides_data[current_slide_index]["undo"] = list(undo_stack)
    slides_data[current_slide_index]["redo"] = list(redo_stack)
    # Switch
    current_slide_index = idx
    _restore_canvas_items(slides_data[current_slide_index]["items"])
    _rebuild_slides_panel()

def add_new_slide():
    """Append a blank slide and switch to it."""
    global current_slide_index
    # Save current state first
    slides_data[current_slide_index]["items"] = _serialize_canvas_items()
    slides_data[current_slide_index]["undo"] = list(undo_stack)
    slides_data[current_slide_index]["redo"] = list(redo_stack)
    # New blank slide
    slides_data.append({"items": [], "undo": [], "redo": []})
    current_slide_index = len(slides_data) - 1
    # Clear canvas for new slide
    canvas.delete("all")
    undo_stack.clear()
    redo_stack.clear()
    _rebuild_slides_panel()
    # Scroll to bottom so new slide is visible
    slides_scroll_frame._parent_canvas.yview_moveto(1.0)

def toggle_slides_panel():
    """Show / hide the slides sidebar."""
    global slides_panel_visible
    slides_panel_visible = not slides_panel_visible
    if slides_panel_visible:
        slidesPanel.pack(side="left", fill="y", before=frameTwo)
        toggle_slides_btn.configure(text="◀ Slides")
    else:
        slidesPanel.pack_forget()
        toggle_slides_btn.configure(text="▶ Slides")

# "Add Slide" button at the bottom of the panel
ctk.CTkFrame(slidesPanel, fg_color="#2EC4B6", height=2).pack(fill="x", padx=4, pady=(0, 4))
add_slide_btn = ctk.CTkButton(
    slidesPanel,
    text="+ Add Slide",
    fg_color="#000000",
    # hover_color="#2EC4B6",
    text_color="#FFFFFF",
    font=("Segoe UI", 10, "bold"),
    height=32,
    corner_radius=8,
    command=add_new_slide
)
add_slide_btn.pack(fill="x", padx=6, pady=6)

# Toggle button in the menu bar
toggle_slides_btn = ctk.CTkButton(
    menuToolFrame,
    text="◀ Slides",
    width=80,
    height=28,
    fg_color="#FEAE7C",
    hover_color="#2EC4B6",
    text_color="white",
    font=("Segoe UI", 9, "bold"),
    corner_radius=8,
    command=toggle_slides_panel
)
toggle_slides_btn.grid(row=0, column=5, padx=8)

# ==================== END SLIDES PANEL SETUP ====================

# The Canvas Frame Where The User Can Draw Things
canvas = tk.Canvas(frameTwo , bg="white") #bg colors change the background color of canvas
canvas.pack(side= "top",fill="both", expand=True)
process_camera_queue()

canvas.configure(scrollregion=(-canvas_virtual_size,-canvas_virtual_size,canvas_virtual_size,canvas_virtual_size))
canvas.config(cursor="crosshair")

# Initialise first slide entry and build the panel
slides_data.append({"items": [], "undo": [], "redo": []})
_rebuild_slides_panel()


zoom_factor = 1.0
# ----------------------------------------------------------------------------------------------------
#Creating Pencil Functionality For The Paint Program
prevPoint = [0,0]
currentPoint = [0,0]


def get_line_dash_pattern():
    global current_line
    if current_line==1:
        return()
    elif current_line==2:
        return(30,15)
    elif current_line==3:
        return(1,10)
    else:
        return()

def paint(event):
    # print(event.type)
    global is_pan_active
    global prevPoint
    global currentPoint
    global current_line
    x = canvas.canvasx(event.x)
    y = canvas.canvasy(event.y)
    currentPoint =[x,y]
#----------------------------------------------------------------------------------------------------------------------------------

    if prevPoint != [0,0] :
        item=canvas.create_line(prevPoint[0] , prevPoint[1] , currentPoint[0] , currentPoint[1] ,fill=stroke_color.get() , width=stroke_size.get() , capstyle=tk.ROUND , smooth=True , splinesteps=36,dash=get_line_dash_pattern())
        undo_stack.append(item)   
    prevPoint = currentPoint 

    if event.type == "5":
        prevPoint = [0,0]   


start_x=0
start_y=0
def start_shape(event):
    global start_x, start_y
    start_x=canvas.canvasx(event.x)
    start_y=canvas.canvasy(event.y)
def drawshape(event):
    global shape , preview_shape
    if preview_shape:
        canvas.delete(preview_shape)
        preview_shape=None
    end_x=canvas.canvasx(event.x)
    end_y=canvas.canvasy(event.y)
    item=None
    if shape=="circle":
        item=canvas.create_oval(start_x,start_y,end_x,end_y,outline=stroke_color.get(),width=stroke_size.get())
    elif shape=="rectangle":
        item=canvas.create_rectangle(start_x,start_y,end_x,end_y,outline=stroke_color.get(),width=stroke_size.get())
    elif shape=="line":
        item=canvas.create_line(start_x,start_y,end_x,end_y,fill=stroke_color.get(),width=stroke_size.get(),dash=get_line_dash_pattern())
    elif shape == "triangle":
        canvas.create_polygon(start_x, end_y,(start_x + end_x)//2, start_y, end_x, end_y,outline=stroke_color.get(),fill='', width=stroke_size.get())
    elif shape == "polygon":
        item=canvas.create_polygon( start_x, start_y, end_x, start_y, end_x, end_y, (start_x + end_x)//2, end_y + 40,start_x, end_y,outline=stroke_color.get(),fill='',width=stroke_size.get() )
    elif shape == "arc":
        item=canvas.create_arc( start_x, start_y, end_x, end_y, outline=stroke_color.get(), width=stroke_size.get(),start=0, extent=150,style=tk.ARC)
    elif shape == "triangle":
        mid_x = (start_x + event.x) / 2
        preview_shape = canvas.create_polygon(start_x, event.y, event.x, event.y, mid_x, start_y, outline=stroke_color.get(), fill='', width=stroke_size.get())

    elif shape == "arrow":
        item=canvas.create_line(start_x, start_y, event.x, event.y, arrow=tk.LAST, fill=stroke_color.get(), width=stroke_size.get())


    elif shape == "heart":
        cx = (start_x + event.x) / 2
        cy = (start_y + event.y) / 2
        width_ = abs(event.x - start_x) / 2
        height_ = abs(event.y - start_y) / 2

        points = []
        for t in range(0, 360, 10):
            rad = math.radians(t)
            x = width_ * 16 * math.sin(rad) ** 3
            y = -height_ * (13 * math.cos(rad) - 5 * math.cos(2 * rad) - 2 * math.cos(3 * rad) - math.cos(4 * rad))
            points.append((cx + x, cy + y))
        flat_points = [coord for point in points for coord in point]
        item=canvas.create_polygon(flat_points, outline=stroke_color.get(), fill='', width=stroke_size.get())

    if item:
        undo_stack.append(item)
def on_right_drag(event):
    global preview_shape
    if preview_shape:
        canvas.delete(preview_shape)
    size=stroke_size.get()
    color=stroke_color.get()
    current_x=canvas.canvasx(event.x)
    current_y=canvas.canvasy(event.y)

    if shape == "rectangle":
        preview_shape = canvas.create_rectangle(start_x, start_y, current_x, current_y, outline=color, width=size)
    elif shape == "circle":
        preview_shape = canvas.create_oval(start_x, start_y, current_x, current_y, outline=color, width=size)
    elif shape == "line":
        preview_shape = canvas.create_line(start_x, start_y, current_x, current_y, fill=color, width=size,dash=get_line_dash_pattern())
    elif shape == "arc":
        preview_shape=canvas.create_arc( start_x, start_y, current_x, current_y, outline=color, width=size,start=0, extent=150,style=tk.ARC)
    elif shape == "triangle":
        mid_x = (start_x + event.x) / 2
        preview_shape = canvas.create_polygon(start_x, current_y, current_x, current_y, mid_x, start_y, outline=color, fill='', width=size)

    elif shape == "arrow":
        preview_shape = canvas.create_line(start_x, start_y, current_x, current_y, arrow=tk.LAST, fill=stroke_color.get(), width=size)


    elif shape == "heart":
        cx = (start_x + current_x) / 2
        cy = (start_y + current_y) / 2
        width_ = abs(current_x - start_x) / 2
        height_ = abs(current_y - start_y) / 2

        points = []
        for t in range(0, 360, 10):
            rad = math.radians(t)
            x = width_ * 16 * math.sin(rad) ** 3
            y = -height_ * (13 * math.cos(rad) - 5 * math.cos(2 * rad) - 2 * math.cos(3 * rad) - math.cos(4 * rad))
            points.append((cx + x, cy + y))
        flat_points = [coord for point in points for coord in point]
        preview_shape = canvas.create_polygon(flat_points, outline=color, fill='', width=size)

canvas.bind("<B1-Motion>" , paint)
canvas.bind("<ButtonRelease-1>",paint)
canvas.bind("<ButtonPress-3>",start_shape)
canvas.bind("<ButtonRelease-3>",drawshape)
canvas.bind("<B3-Motion>",on_right_drag)


#This Function Controls The Add Text Window
def add_Text():
    entered_text = entry.get()
    x_pos_text = x_slider.get()
    y_pos_text = y_slider.get()
    textofentry.set(" ")
    
    # Create text item and add to undo stack
    text_item = canvas.create_text(x_pos_text, y_pos_text, text=entered_text, font=("Arial", 16), fill="black", tags="text")
    undo_stack.append(text_item)

#-------------------------------------------Insert_Image_START--------------------------------------------------------------------+
image_id=None
last_x=0
last_y=0
def insert():
    global current_pil_image
    global insert_image
    global image_id
    global original_image
    #Open file dialog to choose image
    file_path=filedialog.askopenfilename(title="Select an image",filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")])
    if file_path:
        #Open the image usinf pillow
        current_pil_image = Image.open(file_path)

        current_pil_image.thumbnail((400,400))

        original_image = current_pil_image.copy()
        width,height=original_image.size
        #convert image for tkinter
        tk_image=ImageTk.PhotoImage(current_pil_image)
        inserted_image.append(tk_image)
        window.update()
        #place image on the center of the canvas
        x=canvas.winfo_width()//2
        y=(canvas.winfo_height()//2)-170
        image_id=canvas.create_image(x,y,image=tk_image, anchor="center")
        undo_stack.append(image_id)
        canvas.tk_image=tk_image
        print("Image inserted on canvas")
        canvas.tag_bind(image_id,"<Button-1>",image_move)
        canvas.tag_bind(image_id,"<B1-Motion>",do_move)


def image_move(event):
    global last_x,last_y
    last_x=event.x
    last_y=event.y
    return "break"
def do_move(event):
    global last_x,last_y,image_id
    dx=event.x-last_x
    dy=event.y-last_y
    canvas.move(image_id,dx,dy)
    last_x=event.x
    last_y=event.y
    return "break"

insertIcon = ctk.CTkButton(
    master=toolFrame,
    width=25,
    height=25,
    image=icons["glass"],
    text="",
    fg_color=frameTwoBackgroudColor,
    hover_color=toolbarHoverColor,
    command=insert
)
insertIcon.place(x = 40 , y = 40)

#------------------------------------------Insert_IMAGE_END----------------------------------------------------------------+
#------------------------------------------Canvas_MOVE--------------------------------------------------------------------+
def pan_left(event):
    canvas.xview_scroll(-1,"units")

def pan_right(event):
    canvas.xview_scroll(1,"units")

def pan_up(event):
    canvas.yview_scroll(-1,"units")

def pan_down(event):
    canvas.yview_scroll(1,"units")

window.bind("<Up>",pan_down)
window.bind("<Down>",pan_up)
window.bind("<Left>",pan_left)
window.bind("<Right>",pan_right)
#=========================================Canvas_MOVE_END================================================================+
zoom_factor = 1.0

def apply_zoom(new_zoom):
    global zoom_factor

    scale = new_zoom / zoom_factor

    canvas.scale("all", 0, 0, scale, scale)

    zoom_factor = new_zoom

    refresh_image_zoom()

    bbox = canvas.bbox("all")
    if bbox:
        canvas.configure(scrollregion=bbox)


def zoom_in(event=None):
    global zoom_factor

    if zoom_factor < 5:
        apply_zoom(zoom_factor * 1.1)
        zoomSlider.set(zoom_factor * 100)


def zoom_out(event=None):
    global zoom_factor

    if zoom_factor > 0.2:
        apply_zoom(zoom_factor / 1.1)
        zoomSlider.set(zoom_factor * 100)


def slider_zoom(value):
    apply_zoom(float(value) / 100)

def refresh_image_zoom():
    global image_id
    global original_image
    global zoom_factor

    if image_id is None or original_image is None:
        return

    x, y = canvas.coords(image_id)

    new_w = max(1, int(original_image.width * zoom_factor))
    new_h = max(1, int(original_image.height * zoom_factor))

    resized = original_image.resize(
        (new_w, new_h),
        Image.Resampling.LANCZOS
    )

    tk_img = ImageTk.PhotoImage(resized)

    inserted_image.clear()
    inserted_image.append(tk_img)

    canvas.itemconfig(image_id, image=tk_img)
    canvas.coords(image_id, x, y)

#-------------------------------------------Ai-Start--------------------------------------------------------------------+
Ai_Mode=False
start_AI_is_running=False

mic=sr.Recognizer()
mic=pyaudio.PyAudio()
stream = None

last_text=""
def voice_command(text):
    global last_text
    text=text.strip().lower() 
    
    if not text:
        return

    if text==last_text:
        return

    last_text=text 

    # --- we have to Use 'in text' for flexible command matching ---
    
    if 'hi' in text or 'hello' in text or 'introduce' in text:
        sound.play("HelloSir")
        time.sleep(2)
        
    elif 'pencil' in text or 'benzene'  in text:
        usePencil()
        sound.play("PencilResponse")
        
    elif 'eraser' in text or 'era' in text or 'lazer' in text:
        useEraser()
        sound.play("EraserResponse")
        
    elif 'color' in text or 'colour' in text:
        selectcolor()
        
    elif 'dotted' in text or 'dot' in text:
        DottedLine()
    elif 'dashed' in text:
        DashedLine()
        
    elif 'solid' in text or 'simple' in text:
        solidline()
        
    elif 'nice' in text or 'good' in text or 'amazing' in text or 'excellent' in text:
        sound.play("ThankYou")
        
    elif 'arc' in text or 'semicircle' in text :
        select_arc()
        sound.play("ArcResponse")
    elif 'quit' in text or 'end' in text or 'stop' in text:
        ptt_stop()
    elif 'rectangle' in text or 'rect' in text :
        select_rectangle()
        sound.play("RectangleResponse")
    elif 'triangle' in text or 'tri' in shape:
        select_triangle()
        sound.play("TriangleResponse")
    elif 'circle' in text or 'ring' in text or 'round' in text :
        select_circle()
        sound.play("CircleResponse")
    elif 'pentagon' in text or '5 shapes' in text :
        select_polygon()
        sound.play("PentagonResponse")


def ptt_start(event=None):
    global Ai_Mode
    global start_AI_is_running
    if not Ai_Mode and not start_AI_is_running:
        Ai_Mode = True
        print("Ai is listening.............")
        start_AI()

def ptt_stop(event=None):
    global Ai_Mode
    sound.play("AiModeOff")
    print("Ai Stops listening)")
    if Ai_Mode:
        Ai_Mode = False

def listen():
    global stream
    sound.play("AiModeOn")
    print("Ai is listening")
    r=sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        while Ai_Mode:
           try:
               audio=r.listen(source)
               text=r.recognize_google(audio,language='en-IN')
               if text:
                   print(f"You said:{text}")
                   voice_command(text)
           except sr.WaitTimeoutError:
               print("Time out;")
               continue
           except sr.UnknownValueError:
               print("Google speech recognition could not understand your voice.")
               continue
           except sr.RequestError:
               print("Check your internet connection.")
               
def start_AI():
    global Ai_Mode,start_AI_is_running,stream
    if not Ai_Mode:
        return
    if not start_AI_is_running:
        # CRITICAL: Stream is opened HERE every time PTT is pressed
        stream=mic.open(format=pyaudio.paInt16,channels=1,rate=16000,input=True,frames_per_buffer=8192)
        listener_thread=threading.Thread(target=listen)
        listener_thread.daemon=True
        listener_thread.start()
        start_AI_is_running=True

#-------------------------------------------AI-Function Ends-------------------------------------------------------------+

# ---------------------------------------Shortcut-Keys-Open------------------------------------------------------------
window.bind_all("<Control-s>" , lambda event : saveImageEvent())
window.bind_all("<Control-a>" , lambda event : ClearAllEvent())
window.bind_all("<MouseWheel>" , lambda event : incre_scale(event))
window.bind("<Control-p>", lambda e: usePencil())
window.bind("<Control-e>", lambda e: useEraser())
window.bind_all("<Control-c>" , lambda event : selectcolor())
window.bind_all("<Control-z>" , lambda event : undo())
window.bind_all("<Control-y>" , lambda event : redo())
window.bind("<Control-plus>", zoom_in)
window.bind("<Control-equal>", zoom_in)
window.bind("<Control-minus>", zoom_out)
window.bind('<Key-v>',toggle_mic)

# ! Section Handling the zoom functionality


zoomSlider = ctk.CTkSlider(
    master=frameFoot,
    from_=10,
    to=200,
    number_of_steps=190,
    command=slider_zoom
)
zoomSlider.set(100)
zoomSlider.pack(side="right", padx=20, pady=10)
zoomOutBtn = ctk.CTkButton(
    frameFoot,
    text="-",
    width=30,
    command=zoom_out
)
zoomOutBtn.pack(side="right", padx=5)

zoomInBtn = ctk.CTkButton(
    frameFoot,
    text="+",
    width=30,
    command=zoom_in
)
zoomInBtn.pack(side="right", padx=5)
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