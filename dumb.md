# ---------------------------------------Shortcut-Keys-Close------------------------------------------------------------


# ---------------------------------------Responsive-Setting-Open------------------------------------------------------------
def on_resize(event):

    if window.state() == "zoomed":
        frameFoot.place(x= 0 , y = 612)
        HelpSettingFrame.place(x=1050,y=0)
        zoomFrame.place(x = 980 , y = 0)
        
    else:
        frameFoot.place(x= 0 , y = 565)
        HelpSettingFrame.place(x=850,y=0)
        zoomFrame.place(x = 800 , y = 0)

sound.play("welcome")
usePencil()
window.bind("<Configure>", on_resize)
# ---------------------------------------Responsive-Setting-Close------------------------------------------------------------
#--------------------------------------------Zoom---------------------------------------------------------------------

# showCordinates = tk.Frame(frameFoot , width=200 , height=35)
# showCordinates.place(x = 50 , y = 0)

# cordinates = "X = {x} : Y = {y}"
def image_resize_onCanvas():
    global original_image,image_id,zoom_level
    if original_image and image_id:
        new_width=int(original_image.width*zoom_level)
        new_height=int(original_image.height*zoom_level)
        resized_image=original_image.resize((new_width,new_height))
        tk_image=ImageTk.PhotoImage(resized_image)
        canvas.itemconfig(image_id,image=tk_image)
        canvas.tk_image=tk_image

def apply_zoom_from_scrollbar(value):
    global zoom_level
    scale = int(value) / (zoom_level * 100)
    zoom_level = int(value) / 100
    canvas.scale("all", 0, 0, scale, scale)
    image_resize_onCanvas()
    # canvas.configure(scrollregion=canvas.bbox("all"))

# zoomSlider.config(command=apply_zoom_from_scrollbar)

def increment_zoom_scale():
    global zoomSlider,value
    value = value + 1
    zoomSlider.set(value) 

def decrement_zoom_scale():
    global zoomSlider
    zoomSlider = zoomSlider - 1 

zoom_level = 1.0

zoomFrame2 = ctk.CTkFrame(master=frameFoot , bg_color="#7A97ED")
zoomFrame2.grid(row = 0 , column = 0)
zoomFrame = ctk.CTkFrame(master=frameFoot , bg_color="#FFFFFF")
zoomFrame.grid(row = 0 , column = 1 , padx = 200)

value = 100
# zoomSlider = ctk.CTkScale(master = frameFoot, from_=10, to=200, orient="horizontal",width = 7 ,length = 200 , label="         Zoom In/Zoom Out")
zoomSlider = ctk.CTkSlider(master = zoomFrame, from_=10, to=200, number_of_steps=100)
zoomSlider.set(value)
zoomSlider.pack()


# Pan with middle mouse button
drag_start = [0, 0]

def start_pan(event):
    drag_start[0] = event.x
    drag_start[1] = event.y

def do_pan(event):
    dx = drag_start[0] - event.x
    dy = drag_start[1] - event.y
    canvas.xview_scroll(int(dx), "units")
    canvas.yview_scroll(int(dy), "units")
    drag_start[0] = event.x
    drag_start[1] = event.y

# Mouse wheel zoom
def zoom(event):
    global zoom_level
    if event.delta > 0 or event.num == 4:
        scale = 1.1
    elif event.delta < 0 or event.num == 5:
        scale = 0.9
    else:
        return

    if not (0.5 <= zoom_level * scale <= 5):
        return

    zoom_level *= scale
    canvas.scale("all", 0, 0, scale, scale)
    # canvas.configure(scrollregion=canvas.bbox("all"))
    zoomSlider.set(int(zoom_level * 100))
    image_resize_onCanvas()

def zoom_fake(scale):
    global zoom_level
    if not (0.5 <= zoom_level * scale <= 5):
        return

    zoom_level *= scale
    canvas.scale("all", 0, 0, scale, scale)
    image_resize_onCanvas()
    # canvas.configure(scrollregion=canvas.bbox("all"))
    zoomSlider.set(int(zoom_level * 100))

#--------------------------------------------Zoom Close---------------------------------------------------------------------------

if __name__ == "__main__":
    window.mainloop()