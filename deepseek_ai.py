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


#! Manual Module Imports
from Utils.utils_icons import load_icons
from Utils.utils_audio import SoundManager
from Utils.camera_utils import start_camera

ctk.set_appearance_mode("Dark")   # "Light" or "Dark"
ctk.set_default_color_theme("blue") # or "dark-blue", "green"

# ==================== WELCOME / SPLASH SCREEN ====================
def show_welcome_screen():
    """
    Polished standalone splash screen.
    Uses its own tk.Tk + mainloop so it fully blocks until done.
    """
    splash = tk.Tk()
    splash.overrideredirect(True)
    splash.resizable(False, False)

    W, H = 780, 460
    sw = splash.winfo_screenwidth()
    sh = splash.winfo_screenheight()
    splash.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")
    splash.configure(bg="#0F2027")

    # ── Canvas for gradient background ──────────────────────────
    bg_cv = tk.Canvas(splash, width=W, height=H, highlightthickness=0)
    bg_cv.place(x=0, y=0)

    # Simulate vertical gradient (#0F2027 → #1B4332) with bands
    gradient_colors = [
        "#0F2027","#102229","#11242B","#12262D","#13282F",
        "#142A31","#152C33","#162E35","#173037","#183239",
        "#19343B","#1A363D","#1A383F","#1B3A41","#1B3C43",
        "#1B3E44","#1B4046","#1B4147","#1B4249","#1B4332",
    ]
    band = H // len(gradient_colors)
    for i, c in enumerate(gradient_colors):
        bg_cv.create_rectangle(0, i*band, W, (i+1)*band+2, fill=c, outline="")

    # ── Decorative side accent stripe ──────────────────────────
    bg_cv.create_rectangle(0, 0, 5, H, fill="#EF6262", outline="")

    # ── Top glow line ──────────────────────────────────────────
    bg_cv.create_rectangle(0, 0, W, 3, fill="#2EC4B6", outline="")

    # ── Large paint palette emoji ──────────────────────────────
    tk.Label(splash, text="🎨", font=("Segoe UI Emoji", 64),
             bg="#0F2027", fg="#FFFFFF").place(relx=0.5, y=52, anchor="n")

    # ── App name ───────────────────────────────────────────────
    tk.Label(splash, text="Paint Studio",
             font=("Segoe UI", 38, "bold"),
             bg="#0F2027", fg="#FFFFFF").place(relx=0.5, y=145, anchor="n")

    # ── Coloured underline bar beneath title ───────────────────
    tk.Frame(splash, bg="#EF6262", height=3, width=220).place(relx=0.5, y=198, anchor="n")

    # ── Tagline ────────────────────────────────────────────────
    tk.Label(splash,
             text="Draw  ·  Sketch  ·  Create  ·  Imagine",
             font=("Segoe UI", 12),
             bg="#0F2027", fg="#2EC4B6").place(relx=0.5, y=212, anchor="n")

    # ── Feature pills row ──────────────────────────────────────
    pill_frame = tk.Frame(splash, bg="#0F2027")
    pill_frame.place(relx=0.5, y=250, anchor="n")
    for label, color in [("✏ Brush", "#6A4C93"), ("◻ Shapes", "#1982C4"),
                         ("🔊 Voice AI", "#EF6262"), ("📷 Camera", "#8AC926")]:
        tk.Label(pill_frame, text=label, font=("Segoe UI", 9, "bold"),
                 bg=color, fg="white", padx=10, pady=4,
                 relief="flat").pack(side="left", padx=5)

    # ── Progress track ─────────────────────────────────────────
    TRACK_W = 560
    track = tk.Canvas(splash, width=TRACK_W, height=8,
                      bg="#1f4a3a", highlightthickness=0)
    track.place(relx=0.5, y=310, anchor="n")
    bar_fill = track.create_rectangle(0, 0, 0, 8, fill="#2EC4B6", outline="")

    # ── Loading text ───────────────────────────────────────────
    loading_var = tk.StringVar(value="Initializing…")
    tk.Label(splash, textvariable=loading_var,
             font=("Segoe UI", 10), bg="#0F2027", fg="#7ECDC4").place(relx=0.5, y=328, anchor="n")

    # ── Version + team credit ──────────────────────────────────
    tk.Label(splash,
             text="v1.0  ·  Ricky Singh  ·  Arun Shaw  ·  Manish Kumar Prasad",
             font=("Segoe UI", 9), bg="#0F2027", fg="#3d7a6e").place(relx=0.5, y=360, anchor="n")

    # ── Bottom accent line ─────────────────────────────────────
    tk.Frame(splash, bg="#EF6262", height=3).place(x=0, y=H-3, relwidth=1)

    # ── "Click to skip" hint ───────────────────────────────────
    skip_lbl = tk.Label(splash, text="click anywhere to skip →",
                        font=("Segoe UI", 8), bg="#0F2027", fg="#2a5a50", cursor="hand2")
    skip_lbl.place(relx=1.0, y=H-18, anchor="e", x=-12)

    # ── Animation ─────────────────────────────────────────────
    steps = 80
    messages = {0: "Initializing…", 20: "Loading tools…",
                40: "Setting up canvas…", 60: "Almost ready…", 78: "Welcome!"}

    running = [True]

    def finish():
        running[0] = False
        window.deiconify()
        splash.destroy()

    def animate(step=0):
        if not running[0]:
            return
        if step <= steps:
            fill_w = int((step / steps) * TRACK_W)
            track.coords(bar_fill, 0, 0, fill_w, 8)
            if step in messages:
                loading_var.set(messages[step])
            splash.after(28, animate, step + 1)
        else:
            splash.after(350, finish)

    splash.bind("<Button-1>", lambda e: finish())
    skip_lbl.bind("<Button-1>", lambda e: finish())

    animate()
    splash.mainloop()
# ==================== END WELCOME SCREEN ====================

window = ctk.CTk()
window.withdraw()
appicon = tk.PhotoImage(file="Icons/App_Icon.png")
window.iconphoto(False , appicon)

window.title("Paint Studio")
window.geometry("1280x768")
sound_on=True #-->Default Sound state

#! Importing Module Function
icons = load_icons(window)
sound = SoundManager()

# ── Refined Design Tokens ──────────────────────────────────────────────
MENU_BG          = "#1A1A2E"   # deep navy – top menu bar
TOOLBAR_BG       = "#16213E"   # slightly lighter navy – tool strip
TOOLBAR_BORDER   = "#0F3460"   # blue border between sections
TOOLBAR_HOVER    = "#E94560"   # red-pink hover
ACTIVE_TOOL_BG   = "#0F3460"   # selected tool highlight
CANVAS_SURROUND  = "#1E1E2F"   # dark grey surround (softer than black)
FOOTER_BG        = "#1A1A2E"   # matches menu bar
ACCENT_TEAL      = "#2EC4B6"   # teal accent
ACCENT_RED       = "#EF6262"   # coral-red accent
TEXT_LIGHT       = "#E0E0E0"   # primary text on dark backgrounds
TEXT_DIM         = "#7A8A99"   # secondary / muted text

# Legacy aliases so existing code still works
activeMenuWidgetBackground = MENU_BG
hoverMenuWidgetBackground  = TOOLBAR_HOVER
frameTwoBackgroudColor     = TOOLBAR_BG
toolbarHoverColor          = TOOLBAR_HOVER
frameFootBackgroundColor   = FOOTER_BG

# ------------------------------------------Parent-Frame-Section-Open----------------------------------------------------------+
menuFrame = ctk.CTkFrame(master=window, fg_color=MENU_BG, height=52, corner_radius=0)
frameOne  = ctk.CTkFrame(master=window, fg_color=TOOLBAR_BG, corner_radius=0)
frameTwo  = ctk.CTkFrame(master=window, fg_color=CANVAS_SURROUND, corner_radius=0)
frameFoot = ctk.CTkFrame(master=window, fg_color=FOOTER_BG, height=42, corner_radius=0)

menuFrame.pack(side="top",    fill="x")
frameOne.pack(side="top",     fill="x", pady=(0, 2))
frameOne.pack_propagate(False)
frameTwo.pack(side="top",     fill="both", expand=True)
frameFoot.pack(side="bottom", fill="x")
frameFoot.pack_propagate(False)

# Thin accent line between menu and toolbar
ctk.CTkFrame(master=window, fg_color=ACCENT_TEAL, height=2, corner_radius=0).pack(
    side="top", fill="x", before=frameOne
)
#------------------------------------Global-Variables-------------------------------------------------------------------+
shape=""
preview_shape=""
undo_stack=[]
redo_stack=[]
stroke_color = tk.StringVar(value="#FFFFFF")   # default white
current_line = 1                                # 1=solid, 2=dashed, 3=dotted
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

# ------------------------------------------GlobalVariable----------------------------------------------------------+

#-------------------------------------------Camera-Close-----------------------------------------------------------------------------
# !-------------------------------------------Menu-Bar----------------------------------------------------------------------+
# App title / branding on far left
_brand_frame = ctk.CTkFrame(master=menuFrame, fg_color=MENU_BG)
_brand_frame.pack(side="left", padx=(16, 4))
ctk.CTkLabel(
    master=_brand_frame,
    text="🎨  Paint Studio",
    font=("Segoe UI", 16, "bold"),
    text_color=ACCENT_TEAL,
).pack(side="left")
# thin vertical separator
ctk.CTkFrame(master=menuFrame, fg_color=TOOLBAR_BORDER, width=2, height=32).pack(side="left", padx=10, pady=10)

menuToolFrame = ctk.CTkFrame(master=menuFrame, fg_color=MENU_BG)
menuToolFrame.pack(side="left", padx=4)

HelpSettingFrame = ctk.CTkFrame(master=menuFrame, fg_color=MENU_BG)
HelpSettingFrame.pack(side="right", padx=8)

def SaveImage():
    if sound_on and not start_AI_is_running:
        sound.play("Save_Sound")
    filelocation = filedialog.asksaveasfilename(defaultextension="jpg")
    x = window.winfo_rootx()+35
    y = window.winfo_rooty()+250
    img = ImageGrab.grab(bbox=(x,y,x+1340,y+640))
    img.save(filelocation)
    if img.save:
        if sound_on:
            sound.play("ImageSaved_Sound")
    if sound_on:
        window.after(2000, lambda: sound.play("OpenImage_Sound"))
    showImage = messagebox.askyesno("Paint Studio", "Do you want to open the saved image?")
    
    if showImage:
        img.show()
    
def saveImageEvent():
    SaveImage()  

def clear():
    if sound_on and not start_AI_is_running:
        sound.play("clear_Sound")
    if messagebox.askokcancel("Clear Canvas", "Do you want to clear everything?"):
        canvas.delete('all')
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
    global undo_stack , redo_stack
    if redo_stack:
        item_id = redo_stack.pop()
        canvas.itemconfig(item_id, state='normal')
        undo_stack.append(item_id)

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

def _menu_btn(parent, image, command, tooltip=""):
    """Styled top-menu icon button with hover effect."""
    b = ctk.CTkButton(
        master=parent, text=None, image=image,
        fg_color=MENU_BG, hover_color=TOOLBAR_HOVER,
        width=38, height=38, corner_radius=8, command=command,
    )
    # Tooltip could be added using CTkToolTip if desired
    return b

saveImageButton  = _menu_btn(menuToolFrame, icons["save"],     SaveImage)
clearImageButton = _menu_btn(menuToolFrame, icons["clear"],    clear)
undo_button      = _menu_btn(menuToolFrame, icons["undo"],     undo)
redo_button      = _menu_btn(menuToolFrame, icons["redo"],     redo)
sound_button     = _menu_btn(menuToolFrame, icons["sound_on"], toggle_sound)

# Separator before right-side buttons
ctk.CTkFrame(master=menuToolFrame, fg_color=TOOLBAR_BORDER, width=2, height=30).grid(row=0, column=5, padx=8)

helpButton    = _menu_btn(HelpSettingFrame, icons["help"],     help_window)
settingButton = _menu_btn(HelpSettingFrame, icons["settings"], setting_window)
aboutButton   = _menu_btn(HelpSettingFrame, icons["about"],    aboutus_window)

# Menu Button Placements
saveImageButton.grid(row=0,  column=0, padx=4, pady=8)
clearImageButton.grid(row=0, column=1, padx=4, pady=8)
undo_button.grid(row=0,      column=2, padx=4, pady=8)
redo_button.grid(row=0,      column=3, padx=4, pady=8)
sound_button.grid(row=0,     column=4, padx=4, pady=8)
helpButton.pack(side="left",    padx=4, pady=8)
settingButton.pack(side="left", padx=4, pady=8)
aboutButton.pack(side="left",   padx=4, pady=8)
# !-------------------------------------------Menu-Bar----------------------------------------------------------------------+

# ! Color Frame

# !Frame One Tools Functionality Section
def selectcolor():
    global stroke_color
    if sound_on:
        sound.play("selectcolor_Sound")
    selectedcolor = colorchooser.askcolor("red" , title="Select Color")
    if selectedcolor[1]:
        stroke_color.set(selectedcolor[1])
        # Update current color preview
        current_color_preview.configure(fg_color=stroke_color.get())

def camera():
    if sound_on and not start_AI_is_running:
        sound.play("CameraOpen_Sound")

    actions = {
        "save": SaveImage,
        "clear": clear,
        "mute": toggle_sound,
        "text": addText,
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

# ? SubFrames Of Frame One (modern, labelled sections)

frameOne.grid_rowconfigure(0, weight=1)

def _section(parent, col, label_text, w, h):
    """Create a labelled toolbar section with cleaner styling."""
    wrapper = ctk.CTkFrame(master=parent, fg_color=TOOLBAR_BG, corner_radius=0)
    wrapper.grid(row=0, column=col, padx=0, pady=0, sticky="ns")
    # top label
    ctk.CTkLabel(
        wrapper, text=label_text,
        font=("Segoe UI", 9, "bold"), text_color=ACCENT_TEAL,
        fg_color=TOOLBAR_BG,
    ).pack(side="top", pady=(6, 2))
    # inner content frame
    inner = ctk.CTkFrame(
        wrapper, fg_color="#0F2027",
        border_width=1, border_color=TOOLBAR_BORDER,
        width=w, height=h, corner_radius=10,
    )
    inner.pack(side="top", padx=8, pady=(0, 8))
    inner.pack_propagate(False)
    # right-side separator line
    ctk.CTkFrame(master=wrapper, fg_color=TOOLBAR_BORDER, width=1).pack(
        side="right", fill="y", pady=6
    )
    return inner

toolFrame     = _section(frameOne, 0, "TOOLS",       160, 96)
lineTypeFrame = _section(frameOne, 1, "LINE STYLE",  158, 96)
shapeFrame    = _section(frameOne, 2, "SHAPES",      320, 96)
colorFrame    = _section(frameOne, 3, "COLORS",      200, 96)
addColorFrame = _section(frameOne, 4, "PICKER",       78, 96)
advToolFrame  = _section(frameOne, 5, "ADVANCED",    120, 96)

toolFrame.grid_propagate(False)
lineTypeFrame.grid_propagate(False)
shapeFrame.grid_propagate(False)
colorFrame.grid_propagate(False)

#! ---------------------------------------------------------------------------------------------------------------

def usePencil():
    global pencil_select
    global current_line

    pencil_select = pencil_select + 1
    if sound_on and not start_AI_is_running :
        if pencil_select != 1:
            sound.play("Pencil_Sound")
        if pencil_select == 1:
            window.after(6000, lambda: sound.play("DefaultBlack_Sound"))
            stroke_color.set("#000000")
            current_color_preview.configure(fg_color="#000000")

    canvas.config(cursor = "crosshair")
    SolidLineButton.configure(fg_color="white")
    DashedLineButton.configure(fg_color="#E5F0EF")
    DottedLineButton.configure(fg_color="#E5F0EF")
    current_line = 1
    
def useEraser():
    if sound_on and not start_AI_is_running:
        sound.play("Eraser_Sound")
    stroke_color.set("#FFFFFF")
    current_color_preview.configure(fg_color="#FFFFFF")
    canvas.config(cursor = "dotbox")

def addText():
    add_text_window()

def _tool_btn(parent, image, command, x, y):
    b = ctk.CTkButton(
        master=parent, text="", image=image, command=command,
        fg_color="#0F2027", hover_color=TOOLBAR_HOVER,
        width=38, height=38, corner_radius=8,
    )
    b.place(x=x, y=y)
    return b

pencilIcon = _tool_btn(toolFrame, icons["pencil"], usePencil,  8,  6)
eraserIcon = _tool_btn(toolFrame, icons["eraser"], useEraser,  8, 50)
fontIcon   = _tool_btn(toolFrame, icons["font"],   addText,   50,  6)
fillIcon   = _tool_btn(toolFrame, icons["fill"],   lambda: None, 92, 6)

# Insert Image button moved to toolFrame
def insert(path=None):
    # placeholder; real implementation is defined later in the file
    return None

insertIcon = ctk.CTkButton(
    master=toolFrame,
    width=38, height=38,
    image=icons["glass"],
    text="",
    fg_color="#0F2027",
    hover_color=TOOLBAR_HOVER,
    corner_radius=8,
    command=lambda: globals()['insert'](),
)
insertIcon.place(x=50, y=50)

#! ----------------------------------------------------------------------------------------------------

#! ----------------------------------------------Line-Type-Start--------------------------------------------------------------
def solidline():
    global current_line
    current_line = 1
    if sound_on:
        sound.play("SolidLineResponse")
    SolidLineButton.configure(fg_color="white")
    DashedLineButton.configure(fg_color="#E5F0EF")
    DottedLineButton.configure(fg_color="#E5F0EF")
    canvas.config(cursor = "crosshair")

def DashedLine():
    global current_line
    current_line = 2
    if sound_on:
        sound.play("DashedLineResponse")
    DashedLineButton.configure(fg_color="white")
    DottedLineButton.configure(fg_color="#E5F0EF")
    SolidLineButton.configure(fg_color="#E5F0EF")
    canvas.config(cursor = "boat")

def DottedLine():
    global current_line
    current_line = 3
    if sound_on:
        sound.play("DottedLineResponse")
    DottedLineButton.configure(fg_color="white")
    DashedLineButton.configure(fg_color="#E5F0EF")
    SolidLineButton.configure(fg_color="#E5F0EF")
    canvas.config(cursor = "dot")

def _line_btn(text, cmd, row):
    b = ctk.CTkButton(
        master=lineTypeFrame, text=text, command=cmd,
        text_color=TEXT_LIGHT, font=("Courier", 12, "bold"),
        fg_color="#0F2027", hover_color=TOOLBAR_HOVER,
        corner_radius=8, height=26, width=140,
    )
    b.grid(row=row, column=0, padx=8, pady=5)
    return b

SolidLineButton  = _line_btn("━━━━━━━",  solidline,  0)
DashedLineButton = _line_btn("╌╌╌╌╌╌╌",  DashedLine, 1)
DottedLineButton = _line_btn("·  ·  ·  ·  ·", DottedLine, 2)
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

for index, (cmd, icon) in enumerate(buttons):
    ctk.CTkButton(
        master=shapeFrame,
        text=None,
        image=icon,
        command=cmd,
        fg_color="#0F2027",
        hover_color=TOOLBAR_HOVER,
        width=44, height=44,
        corner_radius=8,
    ).grid(
        row=index // 8,
        column=index % 8,
        padx=3, pady=4,
    )

#! ------------------------------------Shape--Frame---close--------------------------------------------------------------------------------------

#! ------------------------------------Color-Frame-Open--------------------------------------------------------------------------------------
colors = [
    "#FF595E","#FFCA3A","#8AC926",
    "#1982C4","#6A4C93",
    "#000000","#FFFFFF","#808080",
    "#FF9F1C","#2EC4B6",
]
for index, color in enumerate(colors):
    row = index // 5
    col = index % 5
    ctk.CTkButton(
        master=colorFrame,
        text=None,
        fg_color=color.lower(),
        hover_color=color.lower(),
        width=32, height=32,
        corner_radius=16,        # circle
        border_width=2,
        border_color="#1A2A3A",
        command=lambda c=color: stroke_color.set(c.lower()),
    ).grid(row=row, column=col, padx=6, pady=6)

# Custom color picker button
colorBoxButton = ctk.CTkButton(
    master=addColorFrame, text=None,
    command=selectcolor, image=icons["select_color"],
    fg_color="#0F2027", hover_color=TOOLBAR_HOVER,
    width=48, height=48, corner_radius=10,
)
colorBoxButton.pack(pady=(10, 0))

# Current color preview
current_color_preview = ctk.CTkFrame(
    addColorFrame, fg_color=stroke_color.get(),
    width=32, height=32, corner_radius=16,
    border_width=2, border_color="#2EC4B6"
)
current_color_preview.pack(pady=6)

#! ------------------------------------Color-Frame-Close--------------------------------------------------------------------------------------

#! ------------------------------------Advance-Frame-Open--------------------------------------------------------------------------------------
openCameraButton = ctk.CTkButton(
    master=advToolFrame, text=None, image=icons["camera"], command=camera,
    fg_color="#0F2027", hover_color=TOOLBAR_HOVER,
    width=52, height=40, corner_radius=8,
)
openCameraButton.grid(row=0, column=0, padx=8, pady=(8, 4))

useMicButton = ctk.CTkButton(
    master=advToolFrame, text=None, image=icons["mic"], command=toggle_mic,
    fg_color="#0F2027", hover_color=TOOLBAR_HOVER,
    width=52, height=40, corner_radius=8,
)
useMicButton.grid(row=1, column=0, padx=8, pady=(4, 8))
#! ------------------------------------Advance-Frame-Close--------------------------------------------------------------------------------------

#----------------------------------------------Stroke Size Slider (Vertical)------------------------------------------------------------------
stroke_size = tk.IntVar(value=5)

scale = ctk.CTkSlider(
    master=window, from_=1, to=100,
    orientation="vertical", variable=stroke_size, height=280,
    progress_color=ACCENT_TEAL,
    button_color=ACCENT_RED,
    button_hover_color="#FF8A80",
    fg_color="#1A2A3A",
)
scale.place(x=12, y=210)

def incre_scale(event):
    global stroke_size
    if event.delta > 0:
        res = stroke_size.get() + 1
        stroke_size.set(res)
    else:
        res = stroke_size.get() - 1
        stroke_size.set(res)

# Stroke size display label
size_label = ctk.CTkLabel(
    window, textvariable=stroke_size,
    font=("Segoe UI", 12, "bold"),
    text_color=ACCENT_TEAL,
    fg_color=CANVAS_SURROUND,
    width=30, height=26, corner_radius=8,
)
size_label.place(x=10, y=498)

# The Canvas — drawing surface with scrollbars
canvas_frame = ctk.CTkFrame(frameTwo, fg_color=CANVAS_SURROUND, corner_radius=12)
canvas_frame.pack(side="top", fill="both", expand=True, padx=8, pady=8)

canvas = tk.Canvas(
    canvas_frame, bg="#FAFAFA",
    highlightthickness=2, highlightbackground="#2EC4B6",
)
canvas.pack(side="left", fill="both", expand=True)

# Scrollbars for canvas
v_scrollbar = ctk.CTkScrollbar(canvas_frame, orientation="vertical", command=canvas.yview)
v_scrollbar.pack(side="right", fill="y")
h_scrollbar = ctk.CTkScrollbar(canvas_frame, orientation="horizontal", command=canvas.xview)
h_scrollbar.pack(side="bottom", fill="x")
canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

canvas.configure(scrollregion=(
    -canvas_virtual_size, -canvas_virtual_size,
     canvas_virtual_size,  canvas_virtual_size,
))
canvas.config(cursor="crosshair")

zoom_factor = 1.0
# ----------------------------------------------------------------------------------------------------
# Creating Pencil Functionality For The Paint Program
prevPoint = [0,0]
currentPoint = [0,0]

def get_line_dash_pattern():
    global current_line
    if current_line == 1:
        return ()
    elif current_line == 2:
        return (30,15)
    elif current_line == 3:
        return (1,10)
    else:
        return ()

def paint(event):
    global is_pan_active
    global prevPoint
    global currentPoint
    global current_line
    x = canvas.canvasx(event.x)
    y = canvas.canvasy(event.y)
    currentPoint = [x,y]

    if prevPoint != [0,0]:
        item = canvas.create_line(prevPoint[0], prevPoint[1], currentPoint[0], currentPoint[1],
                                  fill=stroke_color.get(), width=stroke_size.get(),
                                  capstyle=tk.ROUND, smooth=True, splinesteps=36,
                                  dash=get_line_dash_pattern())
        undo_stack.append(item)   
    prevPoint = currentPoint 

    if event.type == "5":
        prevPoint = [0,0]   

start_x = 0
start_y = 0
def start_shape(event):
    global start_x, start_y
    start_x = canvas.canvasx(event.x)
    start_y = canvas.canvasy(event.y)

def drawshape(event):
    global shape, preview_shape
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
        item = canvas.create_polygon(start_x, end_y, (start_x + end_x)//2, start_y,
                                     end_x, end_y, outline=stroke_color.get(),
                                     fill='', width=stroke_size.get())
    elif shape == "polygon":
        item = canvas.create_polygon(start_x, start_y, end_x, start_y, end_x, end_y,
                                     (start_x + end_x)//2, end_y + 40, start_x, end_y,
                                     outline=stroke_color.get(), fill='', width=stroke_size.get())
    elif shape == "arc":
        item = canvas.create_arc(start_x, start_y, end_x, end_y,
                                 outline=stroke_color.get(), width=stroke_size.get(),
                                 start=0, extent=150, style=tk.ARC)
    elif shape == "arrow":
        item = canvas.create_line(start_x, start_y, end_x, end_y,
                                  arrow=tk.LAST, fill=stroke_color.get(), width=stroke_size.get())
    elif shape == "heart":
        cx = (start_x + end_x) / 2
        cy = (start_y + end_y) / 2
        width_ = abs(end_x - start_x) / 2
        height_ = abs(end_y - start_y) / 2
        points = []
        for t in range(0, 360, 10):
            rad = math.radians(t)
            x = width_ * 16 * math.sin(rad) ** 3
            y = -height_ * (13 * math.cos(rad) - 5 * math.cos(2 * rad) - 2 * math.cos(3 * rad) - math.cos(4 * rad))
            points.append((cx + x, cy + y))
        flat_points = [coord for point in points for coord in point]
        item = canvas.create_polygon(flat_points, outline=stroke_color.get(),
                                     fill='', width=stroke_size.get())
    if item:
        undo_stack.append(item)

def on_right_drag(event):
    global preview_shape
    if preview_shape:
        canvas.delete(preview_shape)
    size = stroke_size.get()
    color = stroke_color.get()
    current_x = canvas.canvasx(event.x)
    current_y = canvas.canvasy(event.y)

    if shape == "rectangle":
        preview_shape = canvas.create_rectangle(start_x, start_y, current_x, current_y,
                                                outline=color, width=size)
    elif shape == "circle":
        preview_shape = canvas.create_oval(start_x, start_y, current_x, current_y,
                                           outline=color, width=size)
    elif shape == "line":
        preview_shape = canvas.create_line(start_x, start_y, current_x, current_y,
                                           fill=color, width=size, dash=get_line_dash_pattern())
    elif shape == "arc":
        preview_shape = canvas.create_arc(start_x, start_y, current_x, current_y,
                                          outline=color, width=size, start=0, extent=150, style=tk.ARC)
    elif shape == "triangle":
        mid_x = (start_x + current_x) / 2
        preview_shape = canvas.create_polygon(start_x, current_y, current_x, current_y,
                                              mid_x, start_y, outline=color, fill='', width=size)
    elif shape == "arrow":
        preview_shape = canvas.create_line(start_x, start_y, current_x, current_y,
                                           arrow=tk.LAST, fill=color, width=size)
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

canvas.bind("<B1-Motion>", paint)
canvas.bind("<ButtonRelease-1>", paint)
canvas.bind("<ButtonPress-3>", start_shape)
canvas.bind("<ButtonRelease-3>", drawshape)
canvas.bind("<B3-Motion>", on_right_drag)

# This Function Controls The Add Text Window
def add_Text():
    entered_text = entry.get()
    x_pos_text = x_slider.get()
    y_pos_text = y_slider.get()
    textofentry.set(" ")
    canvas.create_text(x_pos_text, y_pos_text, text=entered_text,
                       font=("Segoe UI", 16), fill=stroke_color.get(), tags="text")

#-------------------------------------------Insert_Image_START--------------------------------------------------------------------+
image_id = None
last_x = 0
last_y = 0

def insert():
    global current_pil_image
    global insert_image
    global image_id
    global original_image
    file_path = filedialog.askopenfilename(title="Select an image",
                                           filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")])
    if file_path:
        current_pil_image = Image.open(file_path)
        current_pil_image.thumbnail((400,400))
        original_image = current_pil_image.copy()
        width, height = original_image.size
        tk_image = ImageTk.PhotoImage(current_pil_image)
        inserted_image.append(tk_image)
        window.update()
        x = canvas.winfo_width() // 2
        y = (canvas.winfo_height() // 2) - 170
        image_id = canvas.create_image(x, y, image=tk_image, anchor="center")
        undo_stack.append(image_id)
        canvas.tk_image = tk_image
        print("Image inserted on canvas")
        canvas.tag_bind(image_id, "<Button-1>", image_move)
        canvas.tag_bind(image_id, "<B1-Motion>", do_move)

def image_move(event):
    global last_x, last_y
    last_x = event.x
    last_y = event.y
    return "break"

def do_move(event):
    global last_x, last_y, image_id
    dx = event.x - last_x
    dy = event.y - last_y
    canvas.move(image_id, dx, dy)
    last_x = event.x
    last_y = event.y
    return "break"

#------------------------------------------Insert_IMAGE_END----------------------------------------------------------------+
#------------------------------------------Canvas_MOVE--------------------------------------------------------------------+
def pan_left(event):
    canvas.xview_scroll(-1, "units")

def pan_right(event):
    canvas.xview_scroll(1, "units")

def pan_up(event):
    canvas.yview_scroll(-1, "units")

def pan_down(event):
    canvas.yview_scroll(1, "units")

window.bind("<Up>", pan_down)
window.bind("<Down>", pan_up)
window.bind("<Left>", pan_left)
window.bind("<Right>", pan_right)
#=========================================Canvas_MOVE_END================================================================+
zoom_factor = 1.0

def apply_zoom(new_zoom):
    global zoom_factor
    scale_factor = new_zoom / zoom_factor
    canvas.scale("all", 0, 0, scale_factor, scale_factor)
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
    global image_id, original_image, zoom_factor
    if image_id is None or original_image is None:
        return
    x, y = canvas.coords(image_id)
    new_w = max(1, int(original_image.width * zoom_factor))
    new_h = max(1, int(original_image.height * zoom_factor))
    resized = original_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
    tk_img = ImageTk.PhotoImage(resized)
    inserted_image.clear()
    inserted_image.append(tk_img)
    canvas.itemconfig(image_id, image=tk_img)
    canvas.coords(image_id, x, y)

#-------------------------------------------Ai-Start--------------------------------------------------------------------+
Ai_Mode = False
start_AI_is_running = False

mic = sr.Recognizer()
mic = pyaudio.PyAudio()
stream = None
last_text = ""

def voice_command(text):
    global last_text
    text = text.strip().lower() 
    if not text:
        return
    if text == last_text:
        return
    last_text = text 

    if 'hi' in text or 'hello' in text or 'introduce' in text:
        sound.play("HelloSir")
        time.sleep(2)
    elif 'pencil' in text or 'benzene' in text:
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
    elif 'arc' in text or 'semicircle' in text:
        select_arc()
        sound.play("ArcResponse")
    elif 'quit' in text or 'end' in text or 'stop' in text:
        ptt_stop()
    elif 'rectangle' in text or 'rect' in text:
        select_rectangle()
        sound.play("RectangleResponse")
    elif 'triangle' in text or 'tri' in shape:
        select_triangle()
        sound.play("TriangleResponse")
    elif 'circle' in text or 'ring' in text or 'round' in text:
        select_circle()
        sound.play("CircleResponse")
    elif 'pentagon' in text or '5 shapes' in text:
        select_polygon()
        sound.play("PentagonResponse")

def ptt_start(event=None):
    global Ai_Mode, start_AI_is_running
    if not Ai_Mode and not start_AI_is_running:
        Ai_Mode = True
        print("Ai is listening.............")
        start_AI()

def ptt_stop(event=None):
    global Ai_Mode
    sound.play("AiModeOff")
    print("Ai Stops listening")
    if Ai_Mode:
        Ai_Mode = False

def listen():
    global stream
    sound.play("AiModeOn")
    print("Ai is listening")
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        while Ai_Mode:
            try:
                audio = r.listen(source)
                text = r.recognize_google(audio, language='en-IN')
                if text:
                    print(f"You said: {text}")
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
    global Ai_Mode, start_AI_is_running, stream
    if not Ai_Mode:
        return
    if not start_AI_is_running:
        stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000,
                          input=True, frames_per_buffer=8192)
        listener_thread = threading.Thread(target=listen)
        listener_thread.daemon = True
        listener_thread.start()
        start_AI_is_running = True

#-------------------------------------------AI-Function Ends-------------------------------------------------------------+

# ---------------------------------------Shortcut-Keys-Open------------------------------------------------------------
window.bind_all("<Control-s>", lambda event: saveImageEvent())
window.bind_all("<Control-a>", lambda event: ClearAllEvent())
window.bind_all("<MouseWheel>", lambda event: incre_scale(event))
window.bind("<Control-p>", lambda e: usePencil())
window.bind("<Control-e>", lambda e: useEraser())
window.bind_all("<Control-c>", lambda event: selectcolor())
window.bind_all("<Control-z>", lambda event: undo())
window.bind_all("<Control-y>", lambda event: redo())
window.bind("<Control-plus>", zoom_in)
window.bind("<Control-equal>", zoom_in)
window.bind("<Control-minus>", zoom_out)
window.bind('<Key-v>', toggle_mic)

# ! Section Handling the zoom functionality

# ── Status bar label (left side of footer) ──────────────────
_status_frame = ctk.CTkFrame(master=frameFoot, fg_color=FOOTER_BG)
_status_frame.pack(side="left", padx=16, pady=6)

ctk.CTkLabel(
    _status_frame, text="🎨  Paint Studio  v1.0",
    font=("Segoe UI", 11, "bold"), text_color=ACCENT_TEAL,
    fg_color=FOOTER_BG,
).pack(side="left", padx=(0, 20))

ctk.CTkFrame(master=_status_frame, fg_color=TOOLBAR_BORDER, width=1, height=20).pack(side="left", padx=8)

# Dynamic status info
status_info = ctk.CTkLabel(
    _status_frame, text="Brush: 5px  |  Color: White",
    font=("Segoe UI", 10), text_color=TEXT_DIM,
    fg_color=FOOTER_BG,
)
status_info.pack(side="left", padx=8)

def update_status_info(*args):
    status_info.configure(text=f"Brush: {stroke_size.get()}px  |  Color: {stroke_color.get().upper()}")
stroke_size.trace_add("write", update_status_info)
stroke_color.trace_add("write", update_status_info)
update_status_info()

ctk.CTkFrame(master=_status_frame, fg_color=TOOLBAR_BORDER, width=1, height=20).pack(side="left", padx=8)

ctk.CTkLabel(
    _status_frame, text="Ctrl+Z Undo  |  Ctrl+S Save  |  Ctrl+E Eraser  |  V Voice AI",
    font=("Segoe UI", 9), text_color=TEXT_DIM,
    fg_color=FOOTER_BG,
).pack(side="left", padx=6)

# ── Zoom controls (right side) ───────────────────────────────
zoom_pct_var = tk.StringVar(value="100%")

def _update_zoom_label(val=None):
    zoom_pct_var.set(f"{int(zoom_factor * 100)}%")

zoomSlider = ctk.CTkSlider(
    master=frameFoot,
    from_=10, to=200,
    number_of_steps=190,
    command=slider_zoom,
    progress_color=ACCENT_TEAL,
    button_color=ACCENT_RED,
    button_hover_color="#FF8A80",
    fg_color="#2A3A4A",
    width=160,
)
zoomSlider.set(100)
zoomSlider.pack(side="right", padx=(4, 20), pady=8)

ctk.CTkLabel(
    frameFoot, textvariable=zoom_pct_var,
    font=("Segoe UI", 11, "bold"),
    text_color=ACCENT_TEAL, fg_color=FOOTER_BG, width=50,
).pack(side="right", padx=4)

zoomOutBtn = ctk.CTkButton(
    frameFoot, text="−", font=("Segoe UI", 16, "bold"),
    width=32, height=30, corner_radius=8,
    fg_color="#0F2027", hover_color=TOOLBAR_HOVER,
    text_color=TEXT_LIGHT,
    command=zoom_out,
)
zoomOutBtn.pack(side="right", padx=3, pady=6)

zoomInBtn = ctk.CTkButton(
    frameFoot, text="+", font=("Segoe UI", 16, "bold"),
    width=32, height=30, corner_radius=8,
    fg_color="#0F2027", hover_color=TOOLBAR_HOVER,
    text_color=TEXT_LIGHT,
    command=zoom_in,
)
zoomInBtn.pack(side="right", padx=3, pady=6)

ctk.CTkLabel(
    frameFoot, text="ZOOM",
    font=("Segoe UI", 10, "bold"), text_color=TEXT_DIM, fg_color=FOOTER_BG,
).pack(side="right", padx=(8, 2))

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