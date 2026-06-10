from logging import root
import tkinter as tk
import ttkbootstrap as ttk
from turtle import width
from click import command
import cv2
import mediapipe as mp
import time
import random
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
from collections import deque

warnings.filterwarnings("ignore", message="pkg_resources is deprecated")


#! Manual Module Imports
from Utils.utils_icons import load_icons
from Utils.utils_audio import SoundManager
from Utils.camera_utils import start_camera

ctk.set_appearance_mode("Dark")   # "Light" or "Dark"
ctk.set_default_color_theme("blue") # or "dark-blue", "green"

window = ctk.CTk()
appicon = tk.PhotoImage(file="Icons/App_Icon.png")
window.iconphoto(False , appicon)

window.title("Paint")
# window.resizable(True , True)
window.geometry("1280x768")
sound_on=True#-->Default Sound state
# ctk.set_appearance_mode("dark")  # "light" or "system"
# ctk.set_default_color_theme("blue")
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
frameTwo = ctk.CTkFrame(master = window , fg_color="#134B40")
frameFoot = ctk.CTkFrame(master = window,fg_color = "#EF6262",height=40)
# frameFoot = ttk.Frame(master=window, height=40, bootstyle="danger") # type: ignore

menuFrame.pack(side = "top" , fill = "x") 
frameOne.pack(side = "top", fill = "x")
frameOne.pack_propagate(False)
frameTwo.pack(side = "top", fill = "both",expand= True) #canvas will be placed in this frame

frameFoot.pack(side="bottom", fill="x")
frameFoot.pack_propagate(False)
is_spray_active = False
symmetry_mode = False
#------------------------------------Global-Variables-------------------------------------------------------------------
shape=""
preview_shape=""
# undo_stack=[]
# redo_stack=[]
# Dictionary to hold history for multiple tabs independently
undo_stacks = {}
redo_stacks = {}
undo_stack = []
redo_stack = []
stroke_color = tk.StringVar(value="white")
global current_line# 1= solid, 2=Dashed, 3=Dotted
current_line=1
insert_image=None
image_on_canvas=None
inserted_image=[]
original_image=None
canvas_virtual_size=100000
pencil_select=0

start_AI_is_running=False 
Ai_Mode=False
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
        
    filelocation= filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("JPG", "*.jpg")])
    if not filelocation: # Prevents error if user clicks "Cancel"
        return
        
    # Dynamically get the exact coordinates and size of the canvas
    window.update()
    x = canvas.winfo_rootx()
    y = canvas.winfo_rooty()
    x1 = x + canvas.winfo_width()
    y1 = y + canvas.winfo_height()
    
    img = ImageGrab.grab(bbox=(x, y, x1, y1))
    img.save(filelocation)
    
    if sound_on:
        sound.play("ImageSaved_Sound")
        window.after(2000, lambda: sound.play("OpenImage_Sound"))
        
    showImage = messagebox.askyesno("Paint App", "Do you want open the saved image?")
    if showImage:
        img.show()
    
def saveImageEvent():
    SaveImage()  

def clear() :
    if sound_on and not start_AI_is_running:
        sound.play("clear_Sound")
    if messagebox.askokcancel("Warning!", "Do you want to clear everything?"):
        canvas.delete('all')
        if sound_on:
            sound.play("EverythingCleared_Sound")

def new_canvas(event=None):
    global canvas_count
    if sound_on and not start_AI_is_running:
        sound.play("clear_Sound") # Play a sound if you like!
        
    # Generate the next canvas name and create the tab
   # Initialize the very first canvas when the app boots up
    canvas_count += 1
    create_new_tab(f"Canvas {canvas_count}")

newCanvasButton = ctk.CTkButton(
    master=menuToolFrame,
    text="New", # Swap to image=icons["new"] if you add an icon!
    font=("Arial", 12, "bold"),
    text_color="black",
    fg_color=activeMenuWidgetBackground,
    hover_color=hoverMenuWidgetBackground,
    command=new_canvas,
    width=50,
)

def ClearAllEvent():
    clear()  
def undo():
    if undo_stack:
        last_item=undo_stack.pop()
        canvas.itemconfig(last_item,state='hidden')
        redo_stack.append(last_item)

def redo():
    global undo_stack , redo_stack
    if redo_stack:
        item_id=redo_stack.pop()
        canvas.itemconfig(item_id,state='normal')
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

def toggle_symmetry(event=None):
    global symmetry_mode
    symmetry_mode = not symmetry_mode
    
    if symmetry_mode:
        print("Symmetry Mode ON")
        if sound_on: sound.play("SoundOn_Sound")
    else:
        print("Symmetry Mode OFF")
        if sound_on: sound.play("SoundOff_Sound")

def help_window():
    new_window = tk.Toplevel(window)
    new_window.title("Help")
    new_window.geometry("400x600")

    help_text = (
        "                               Paint Application Help\n\n"
        "• Getting Started  \n "

        "→ Select a tool from the toolbar (e.g., Brush, Eraser).\n"
        "→ Choose a color from the color palette.\n"
        "→ Start drawing by clicking and dragging on the canvas.\n \n"


        "• Tools & Their Functions\n"
        "→ Eraser: Remove parts of your drawing.\n"
        "→ Brush: Draw freehand lines on the canvas.\n"
        "→ Color Picker: Pick any color for the brush.\n"
        "→ Fill Tool (if available):** Fill a closed area with a selected color.\n"
        "→ Line/Rectangle/Ellipse:** Draw shapes (click and drag).\n"
        "→ Clear Canvas: Erase the entire canvas.\n"
        "→ Undo/Redo: Revert or repeat your last action.\n \n"

        "• 3. File Options\n "

        "→ New: Start a new canvas.\n"
        "→ Open: Load an existing image (optional).\n"
        "→ Save: Save your drawing as an image file.\n \n"

        "• 4. Shortcuts (if any)\n"

        "→ `Ctrl + Z`: Undo\n"
        "→ `Ctrl + S`: Save\n"
        "→ `Ctrl + N`: New Canvas\n \n"

        "• 5. Tips\n "

        "→ Hold `Shift` while drawing shapes for perfect squares/circles (if implemented).\n"
        "→ Use a stylus for better precision on touch-enabled devices.\n \n"

        "• 6. About\n"

        "PaintApp v1.0\n"
        "Developed by Team Ricky Include Ricky Singh ,Arun Shaw And Manish Kumar Prasad\n "
        "© 2025 All Rights Reserved\n"
        
    )
    text_area = scrolledtext.ScrolledText(new_window, wrap=tk.WORD, font=("Arial", 12))
    text_area.insert(tk.END, help_text)
    text_area.config(state='disabled')  # Make it read-only
    text_area.pack(expand=True, fill='both')

def aboutus_window():
    new_window = tk.Toplevel(window)
    new_window.title("About Us")
    new_window.geometry("400x600")

    
    about_text = (
        "                                       About Us\n\n"

        "PaintApp v1.0\n\n"
        
        "This paint application was developed with the goal of providing a simple, "
        "user-friendly drawing tool built using Python's Tkinter library.\n\n"

        "🛠 Features include:\n"
        "• Freehand drawing (brush)\n"
        "• Eraser tool\n"
        "• Shape drawing (lines, rectangles, ellipses)\n"
        "• Color selection and fill tool\n"
        "• Undo/Redo and file operations\n\n"

        "👨‍💻 Developed By:\n"
        "• Ricky Singh\n"
        "• Arun Kumar Ray\n"
        "• Manish Kumar Prasad\n\n"

        "© 2025 All Rights Reserved\n"
        "Thank you for using our application!"
    )

    text_area = scrolledtext.ScrolledText(new_window, wrap=tk.WORD, font=("Arial", 12))
    text_area.insert(tk.END, about_text)
    text_area.config(state='disabled')  # Read-only
    text_area.pack(expand=True, fill='both')

def setting_window():
    new_window = tk.Toplevel(window)
    new_window.title("Setting")
    new_window.geometry("700x400")
    label = ctk.CTkLabel(new_window, text="This is a new window")
    label.pack(pady=20)

saveImageButton = ctk.CTkButton(
    master=menuToolFrame,
    text=None,
    image= icons["save"] ,
    fg_color=activeMenuWidgetBackground,
    hover_color=hoverMenuWidgetBackground,
    command=SaveImage,
    width=0,
)

newCanvasButton = ctk.CTkButton(
    master=menuToolFrame,
    text="New", 
    font=("Arial", 12, "bold"),
    text_color="black",
    fg_color=activeMenuWidgetBackground,
    hover_color=hoverMenuWidgetBackground,
    command=new_canvas,
    width=50,
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
# Menu Button Placements
newCanvasButton.grid(row=0, column=0, padx=5)
saveImageButton.grid(row=0, column=1, padx=5)
clearImageButton.grid(row=0, column=2, padx=5)
undo_button.grid(row=0, column=3, padx=5)
redo_button.grid(row=0, column=4, padx=5)
sound_button.grid(row=0, column=5, padx=5)
# !-------------------------------------------Menu-Bar----------------------------------------------------------------------+


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
    }

    threading.Thread(target=start_camera, args=(sound, actions)).start()

def add_text_window():
    new_window = tk.Toplevel(window)
    new_window.title("Add Text To Canvas")
    new_window.geometry("600x300")
    label = tk.Label(new_window, text="Enter The Text You Want To Display :")
    label.pack(pady=20)

    global textofentry
    global entry 
    textofentry = tk.StringVar(value = "Enter Here")

    entry = tk.Entry(new_window , justify="center" , font=("Arial", 10) , textvariable=textofentry , width=50)
    entry.place(x = 100, y = 80)
    btn = tk.Button(new_window , text="Add" , command= add_Text  , width = 10, height = 2, highlightthickness=0 , relief="flat",bd=1)
    btn.place(x = 250 , y = 120)


    # Sliders for X and Y position
    global x_slider , y_slider
    x_slider = tk.Scale(new_window, from_=0, to=1280, orient="horizontal", label="X Position" , length=200)
    x_slider.set(200)  # default center
    x_slider.place(x = 50 , y = 200)

    y_slider = tk.Scale(new_window, from_=0, to=800, orient="horizontal", label="Y Position" , length=200)
    y_slider.set(125)
    y_slider.place(x = 350 , y = 200)
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
    # height=100,
    # width=100,
    fg_color=frameTwoBackgroudColor,
    border_width=2,
    border_color="black",    
)
addColorFrame.grid(row=0, column=4)

# camera + mic functionality can used from here
advToolFrame = ctk.CTkFrame(
    master = frameOne,
    width=200 ,
    height=120,
    fg_color=frameTwoBackgroudColor,
    border_width=2,
    border_color="black",
)
advToolFrame.grid(row=0, column=5)



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

def useSpray():
    global is_spray_active
    is_spray_active = True
    
    if sound_on and not start_AI_is_running:
        sound.play("Pencil_Sound") # Or a custom spray sound if you have one
        
    canvas.config(cursor="target")
    SolidLineButton.configure(fg_color="#E5F0EF")
    DashedLineButton.configure(fg_color="#E5F0EF")
    DottedLineButton.configure(fg_color="#E5F0EF")


def useEraser():
    if sound_on and not start_AI_is_running:
        sound.play("Eraser_Sound")
        
    # Make the eraser match the actual canvas background color dynamically
    current_bg_color = canvas["bg"]
    stroke_color.set(current_bg_color)
    
    canvas.config(cursor = "dotbox")

def fill_canvas():
    if sound_on and not start_AI_is_running:
        # Plays a sound if you have one, otherwise just fallback to another sound
        sound.play("selectcolor_Sound") 
    
    # Change the canvas background to the current selected color
    canvas.config(bg=stroke_color.get())

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
#fillIcon = ctk.CTkButton(master = toolFrame , text="", fg_color=frameTwoBackgroudColor ,hover_color=toolbarHoverColor,width=25, height=25, image=icons["fill"])
fillIcon = ctk.CTkButton(master = toolFrame , text="", fg_color=frameTwoBackgroudColor ,hover_color=toolbarHoverColor,width=25, height=25, image=icons["fill"], command=fill_canvas)
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

#------------------------------------------Canvas_Move--------------------------------------------------------------------+

# >>> NEW CODE TO ADD HERE <<<
def start_mouse_pan(event):
    # Marks the starting point of the drag
    canvas.scan_mark(event.x, event.y)

def do_mouse_pan(event):
    # Drags the canvas based on the mouse movement
    canvas.scan_dragto(event.x, event.y, gain=1)

#------------------------------------------Canvas_Move--------------------------------------------------------------------+
def pan_left(event=None):
    canvas.xview_scroll(-1, "units")

def pan_right(event=None):
    canvas.xview_scroll(1, "units")

def pan_up(event=None):
    canvas.yview_scroll(-1, "units")

def pan_down(event=None):
    canvas.yview_scroll(1, "units")

window.bind("<Up>", pan_down)
window.bind("<Down>", pan_up)
window.bind("<Left>", pan_left)
window.bind("<Right>", pan_right)
#=========================================Canvas_Move_End================================================================+


# >>> END OF NEW CODE <<<

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
colors = ["Red", "Green", "Blue", "Yellow", "Grey",

          "Black", "White", "Orange", "Purple", "Pink"]
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
colorBoxButton= ctk.CTkButton(master = addColorFrame ,text=None, command=selectcolor , image= icons["select_color"] , fg_color=frameTwoBackgroudColor , hover_color="#FFFFFF")
colorBoxButton.pack()


#! ------------------------------------Color-Frame-Close--------------------------------------------------------------------------------------

#! ------------------------------------Advance-Frame-Open--------------------------------------------------------------------------------------
openCameraButton = ctk.CTkButton(master = advToolFrame , text=None,image= icons["camera"],command=camera , fg_color=frameTwoBackgroudColor , hover_color=hoverMenuWidgetBackground)
openCameraButton.grid(row = 0 , column = 0)

useMicButton = ctk.CTkButton(master=advToolFrame,text=None,image=icons["mic"],command=toggle_mic  , fg_color=frameTwoBackgroudColor , hover_color=hoverMenuWidgetBackground)
useMicButton.grid(row = 1 , column = 0)
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

# The Canvas Frame Where The User Can Draw Things
# canvas = tk.Canvas(frameTwo , bg="white")
# # canvas.grid(row=0,column=0)
# canvas.pack(side= "top",fill="both", expand=True)

# ------------------ MULTIPLE CANVAS TAB SYSTEM ------------------
canvas_tabs = ctk.CTkTabview(master=frameTwo, command=lambda: update_active_canvas(), fg_color="#134B40")
canvas_tabs.pack(side="top", fill="both", expand=True)

canvases = {} # Stores {tab_name: canvas_object}
canvas_count = 0

def update_active_canvas():
    """Switches the global canvas reference to whatever tab you click on"""
    global canvas, undo_stack, redo_stack
    active_tab = canvas_tabs.get()
    canvas = canvases[active_tab]
    
    # Swap to the active tab's specific undo/redo history
    undo_stack = undo_stacks[active_tab]
    redo_stack = redo_stacks[active_tab]

def create_new_tab(tab_name):
    global canvas, undo_stacks, redo_stacks
    
    # 1. Create a new tab and put a fresh canvas inside it
    new_tab = canvas_tabs.add(tab_name)
    new_canvas = tk.Canvas(new_tab, bg="white")
    new_canvas.pack(side="top", fill="both", expand=True)
    new_canvas.configure(scrollregion=(-canvas_virtual_size, -canvas_virtual_size, canvas_virtual_size, canvas_virtual_size))
    new_canvas.config(cursor="crosshair")

    # 2. Bind all of your drawing/mouse actions to this SPECIFIC canvas
    new_canvas.bind("<B1-Motion>", paint)
    new_canvas.bind("<ButtonRelease-1>", reset_point)
    new_canvas.bind("<ButtonPress-3>", start_shape)
    new_canvas.bind("<ButtonRelease-3>", drawshape)
    new_canvas.bind("<B3-Motion>", on_right_drag)
    new_canvas.bind("<ButtonPress-2>", start_mouse_pan)
    new_canvas.bind("<B2-Motion>", do_mouse_pan)

    # 3. Create fresh undo/redo memory for this new tab
    undo_stacks[tab_name] = []
    redo_stacks[tab_name] = []

    # 4. Save it, bring it to the front, and activate it
    canvases[tab_name] = new_canvas
    canvas_tabs.set(tab_name)
    update_active_canvas()

# Initialize the very first canvas when the app boots up

# ----------------------------------------------------------------


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

  
def reset_point(event):
    global prevPoint
    prevPoint = [0, 0]


def paint(event):
    global prevPoint, currentPoint, current_line, is_spray_active
    x = canvas.canvasx(event.x)
    y = canvas.canvasy(event.y)
    currentPoint = [x, y]

    if is_spray_active:
        # Spray paint logic: scatter random dots around the cursor
        radius = stroke_size.get() * 2  # The spread of the spray
        density = stroke_size.get() * 3 # How many particles spawn per frame
        
        for _ in range(density):
            # Generate random offset
            dx = random.randint(-radius, radius)
            dy = random.randint(-radius, radius)
            
            # Keep the spray circular using the Pythagorean theorem
            if dx*dx + dy*dy <= radius*radius:
                item = canvas.create_oval(x + dx, y + dy, x + dx + 1, y + dy + 1, 
                                          fill=stroke_color.get(), outline=stroke_color.get())
                undo_stack.append(item)
        prevPoint = currentPoint
        return # Skip the solid line drawing below


    if prevPoint != [0,0]:
        # Draw the main line
        item = canvas.create_line(prevPoint[0], prevPoint[1], currentPoint[0], currentPoint[1], fill=stroke_color.get(), width=stroke_size.get(), capstyle=tk.ROUND, smooth=True, splinesteps=36, dash=get_line_dash_pattern())
        undo_stack.append(item)
        
        # >>> NEW: Draw the mirrored line if symmetry is on <<<
        if symmetry_mode:
            # Find the exact center of the visible canvas
            canvas_center_x = canvas.winfo_width() / 2 
            
            # Calculate the mirrored X coordinates
            mirror_prev_x = canvas_center_x + (canvas_center_x - prevPoint[0])
            mirror_curr_x = canvas_center_x + (canvas_center_x - currentPoint[0])
            
            mirror_item = canvas.create_line(mirror_prev_x, prevPoint[1], mirror_curr_x, currentPoint[1], fill=stroke_color.get(), width=stroke_size.get(), capstyle=tk.ROUND, smooth=True, splinesteps=36, dash=get_line_dash_pattern())
            undo_stack.append(mirror_item)

    prevPoint = currentPoint


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



#This Function Controls The Add Text Window
def add_Text():
    entered_text = entry.get()
    x_pos_text = x_slider.get()
    y_pos_text = y_slider.get()
    textofentry.set(" ")
    
    canvas.create_text(x_pos_text, y_pos_text, text=entered_text, font=("Arial", 16), fill="black", tags="text")

#-------------------------------------------Insert_Image_Start--------------------------------------------------------------------+
image_id=None
last_x=0
last_y=0
def insert():
    global insert_image
    global image_id
    global original_image
    #Open file dialog to choose image
    file_path=filedialog.askopenfilename(title="Select an image",filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")])
    if file_path:
        #Open the image usinf pillow
        img=Image.open(file_path)
        #Resize for better fit
        img.thumbnail((400,400))
        original_image=img.copy()
        width,height=original_image.size
        #convert image for tkinter
        tk_image=ImageTk.PhotoImage(img)
        inserted_image.append(tk_image)
        window.update()
        #place image on the center of the canvas
        x=canvas.winfo_width()//2
        y=(canvas.winfo_height()//2)-170
        image_id=canvas.create_image(x,y,image=tk_image, anchor="center")
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

#------------------------------------------Insert_Image_End----------------------------------------------------------------+
#------------------------------------------Canvas_Move--------------------------------------------------------------------+
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
#=========================================Canvas_Move_End================================================================+
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
#Button Creating


# Mic_Label = tk.Label(frameOne , text="Voice Command" , width=15 ,bg="#D6F5EF" ,font=("Calibri",8) )
# Mic_Label.place(x = 918 , y = 130)
# openCameraButton= Button(frameOne  , width=90, height=90 ,image= iconOfCamera ,command=camera ,bg="#D6F5EF" , activebackground="#D6F5EF" , highlightthickness=0 , relief="flat",bd=0)
# openCameraButton.place(x=820, y=50)
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
# window.bind_all("<Control-plus>" , lambda event : increment_zoom_scale())
# window.bind_all("<Control-minus>" , lambda event : decrement_zoom_scale())
window.bind('<Key-v>',toggle_mic)
window.bind("<Control-m>", toggle_symmetry) # M for Mirror/Symmetry

# Bind the middle mouse button (Button-2) for smooth panning

window.bind_all("<Control-n>", new_canvas)

# ! Section Handling the zoom functionality

# zoomFrame = ctk.CTkFrame(master=frameFoot , bg_color="#0DB949" , height=50)
# zoomFrame.pack(side = "right")

zoomSlider = ctk.CTkSlider(
    master=frameFoot,
    from_=10,
    to=200,
    number_of_steps=190
)
zoomSlider.set(100)
zoomSlider.pack(side="right", padx=20, pady=10)

canvas_count += 1
create_new_tab(f"Canvas {canvas_count}")

if __name__ == "__main__":
    window.mainloop()
    