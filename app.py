import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw
import os

# --- KONFIGURASI SKALA (SCALING) ---
IS_DEV = True 

# Ukuran Asli Desain
ORIGINAL_WIDTH = 1080
ORIGINAL_HEIGHT = 1920

# Hitung Faktor Skala
if IS_DEV:
    TARGET_HEIGHT = 850 
    SCALE_FACTOR = TARGET_HEIGHT / ORIGINAL_HEIGHT
else:
    SCALE_FACTOR = 1.0

def s(value):
    """Fungsi helper untuk menskalakan angka"""
    return int(value * SCALE_FACTOR)

# -----------------------------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Virtual Try-On Kiosk")
        
        app_width = s(ORIGINAL_WIDTH)
        app_height = s(ORIGINAL_HEIGHT)
        self.geometry(f"{app_width}x{app_height}")
        
        self.configure(bg="#0a0a0a")
        self.resizable(IS_DEV, IS_DEV) 
        
        container = tk.Frame(self, bg="#0a0a0a")
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.screens = {}
        for F in (HomeScreen, CalibrationGestureScreen, CalibrationTouchScreen, 
                  CalibrationVoiceScreen, VTOScreen):
            screen_name = F.__name__
            screen = F(parent=container, controller=self)
            self.screens[screen_name] = screen
            screen.grid(row=0, column=0, sticky="nsew")
        
        self.show_screen("HomeScreen")
    
    def show_screen(self, screen_name):
        screen = self.screens[screen_name]
        screen.tkraise()

class HomeScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0a0a0a")
        self.controller = controller
        
        title_label = tk.Label(self, text="Virtual\nTry-On Kiosk", font=("Arial", s(72), "bold"), fg="#ffffff", bg="#0a0a0a", justify="center")
        title_label.pack(pady=(s(120), s(20)))
        
        subtitle1 = tk.Label(self, text="Choose Interaction Mode", font=("Arial", s(32), "bold"), fg="#ffffff", bg="#0a0a0a")
        subtitle1.pack(pady=(0, s(10)))
        
        subtitle2 = tk.Label(self, text="Select how you'd like to interact with the\nvirtual try-on", font=("Arial", s(20)), fg="#b8b8b8", bg="#0a0a0a", justify="center")
        subtitle2.pack(pady=(0, s(60)))
        
        buttons_frame = tk.Frame(self, bg="#0a0a0a")
        buttons_frame.pack(pady=s(20))
        
        self.create_mode_button(buttons_frame, "Gesture Mode", "Control with hand gestures\ndetected by camera", "gesture_icon.png", "CalibrationGestureScreen", 0)
        self.create_mode_button(buttons_frame, "Touch Mode", "Direct touch interaction\nwith the display", "touch_icon.png", "CalibrationTouchScreen", 1)
        self.create_mode_button(buttons_frame, "Voice Mode", "Navigate using voice\ncommands", "voice_icon.png", "CalibrationVoiceScreen", 2)
    
    def create_mode_button(self, parent, title, desc, icon_name, target_screen, row):
        w, h = s(620), s(220)
        canvas = tk.Canvas(parent, width=w, height=h, bg="#0a0a0a", highlightthickness=0)
        canvas.grid(row=row, column=0, pady=s(20), padx=s(40))
        
        self.draw_rounded_rect(canvas, s(10), s(10), w-s(10), h-s(10), s(30), outline="#3a3a5a", width=2)
        
        icon_size_limit = s(100) 
        icon_frame_size = s(110) 
        icon_frame = tk.Frame(canvas, bg="#0a0a0a", width=icon_frame_size, height=icon_frame_size)
        canvas.create_window(s(100), s(110), window=icon_frame)
        
        try:
            icon_path = f"assets/{icon_name}"
            if os.path.exists(icon_path):
                img = Image.open(icon_path)
                ratio = min(icon_size_limit / img.width, icon_size_limit / img.height)
                new_w = int(img.width * ratio)
                new_h = int(img.height * ratio)
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                icon_photo = ImageTk.PhotoImage(img)
                icon_label = tk.Label(icon_frame, image=icon_photo, bg="#0a0a0a")
                icon_label.image = icon_photo
                icon_label.place(relx=0.5, rely=0.5, anchor="center")
                icon_label.bind("<Button-1>", lambda e: self.controller.show_screen(target_screen))
        except: pass
        
        text_frame = tk.Frame(canvas, bg="#0a0a0a")
        canvas.create_window(s(400), s(110), window=text_frame)
        
        title_label = tk.Label(text_frame, text=title, font=("Arial", s(28), "bold"), fg="#ffffff", bg="#0a0a0a", anchor="w")
        title_label.pack(anchor="w")
        desc_label = tk.Label(text_frame, text=desc, font=("Arial", s(16)), fg="#b8b8b8", bg="#0a0a0a", anchor="w", justify="left")
        desc_label.pack(anchor="w", pady=(s(5), 0))
        
        canvas.bind("<Button-1>", lambda e: self.controller.show_screen(target_screen))
        title_label.bind("<Button-1>", lambda e: self.controller.show_screen(target_screen))
        desc_label.bind("<Button-1>", lambda e: self.controller.show_screen(target_screen))
    
    def draw_rounded_rect(self, canvas, x1, y1, x2, y2, radius, **kwargs):
        points = [x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y2-radius, x2, y2, x2-radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y1+radius, x1, y1]
        return canvas.create_polygon(points, **kwargs, smooth=True, fill="")

class CalibrationGestureScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0a0a0a")
        self.controller = controller
        
        title = tk.Label(self, text="Gesture Calibration", font=("Arial", s(56), "bold"), fg="#ffffff", bg="#0a0a0a")
        title.pack(pady=(s(150), s(20)))
        
        inst = tk.Label(self, text="Position your hand in front of the camera\nand follow the on-screen instructions.", font=("Arial", s(20)), fg="#b8b8b8", bg="#0a0a0a", justify="center")
        inst.pack(pady=(0, s(80)))
        
        cw, ch = s(620), s(800)
        preview_canvas = tk.Canvas(self, width=cw, height=ch, bg="#1a1a2e", highlightthickness=2, highlightbackground="#4a4a6a")
        preview_canvas.pack()
        
        self.draw_corner_brackets(preview_canvas, cw, ch)
        self.create_nav_buttons() 
    
    def load_icon(self, icon_name, max_size):
        try:
            icon_path = f"assets/{icon_name}"
            if os.path.exists(icon_path):
                img = Image.open(icon_path)
                ratio = min(max_size / img.width, max_size / img.height)
                new_width = int(img.width * ratio)
                new_height = int(img.height * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
        except: pass
        return None

    def draw_corner_brackets(self, canvas, w, h):
        bl, bw, off = s(60), s(4), s(20)
        bc = "#7a7aff"
        canvas.create_line(off, off+bl, off, off, off+bl, off, fill=bc, width=bw)
        canvas.create_line(w-off-bl, off, w-off, off, w-off, off+bl, fill=bc, width=bw)
        canvas.create_line(off, h-off-bl, off, h-off, off+bl, h-off, fill=bc, width=bw)
        canvas.create_line(w-off-bl, h-off, w-off, h-off, w-off, h-off-bl, fill=bc, width=bw)
    
    def create_nav_buttons(self):
        icon_size = s(250)
        nav_h = icon_size + s(20)
        nav_w = (icon_size * 2) + s(200)
        
        self.nav_canvas = tk.Canvas(self, width=nav_w, height=nav_h, bg="#0a0a0a", highlightthickness=0)
        self.nav_canvas.pack(side="bottom", pady=s(40))
        
        self.btn_back_img = self.load_icon("back_arrow.png", icon_size)
        self.btn_next_img = self.load_icon("next_arrow.png", icon_size)
        
        center_y = nav_h / 2
        offset_x = icon_size // 2
        
        if self.btn_back_img:
            btn_back = self.nav_canvas.create_image(offset_x, center_y, image=self.btn_back_img, anchor="center")
            self.nav_canvas.tag_bind(btn_back, "<Button-1>", lambda e: self.controller.show_screen("HomeScreen"))
        
        if self.btn_next_img:
            btn_next = self.nav_canvas.create_image(nav_w - offset_x, center_y, image=self.btn_next_img, anchor="center")
            self.nav_canvas.tag_bind(btn_next, "<Button-1>", lambda e: self.controller.show_screen("VTOScreen"))

class CalibrationTouchScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0a0a0a")
        self.controller = controller
        
        title = tk.Label(self, text="Touch Calibration", font=("Arial", s(56), "bold"), fg="#ffffff", bg="#0a0a0a")
        title.pack(pady=(s(150), s(20)))
        
        inst = tk.Label(self, text="Touch the target with your finger for\naccurate testing.", font=("Arial", s(20)), fg="#b8b8b8", bg="#0a0a0a", justify="center")
        inst.pack(pady=(0, s(80)))
        
        cw, ch = s(620), s(800)
        calib_canvas = tk.Canvas(self, width=cw, height=ch, bg="#0f0f1e", highlightthickness=2, highlightbackground="#4a4a6a")
        calib_canvas.pack()
        
        self.draw_corner_brackets(calib_canvas, cw, ch)
        
        targets = [(s(150), s(150), s(80), 1), (s(470), s(250), s(60), 2), (s(310), s(380), s(45), 3), (s(180), s(570), s(70), 4), (s(450), s(630), s(90), 5)]
        for x, y, size, num in targets:
            for i in range(3, 0, -1):
                calib_canvas.create_oval(x-size*i/2, y-size*i/2, x+size*i/2, y+size*i/2, fill="#6a5aff", outline="")
            calib_canvas.create_oval(x-size/2, y-size/2, x+size/2, y+size/2, fill="#8a7aff", outline="")
            calib_canvas.create_text(x, y, text=str(num), font=("Arial", s(20), "bold"), fill="#ffffff")
        
        self.create_nav_buttons()

    def load_icon(self, icon_name, max_size):
        try:
            icon_path = f"assets/{icon_name}"
            if os.path.exists(icon_path):
                img = Image.open(icon_path)
                ratio = min(max_size / img.width, max_size / img.height)
                new_width = int(img.width * ratio)
                new_height = int(img.height * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
        except: pass
        return None

    def draw_corner_brackets(self, canvas, w, h):
        bl, bw, off = s(60), s(4), s(20)
        bc = "#7a7aff"
        canvas.create_line(off, off+bl, off, off, off+bl, off, fill=bc, width=bw)
        canvas.create_line(w-off-bl, off, w-off, off, w-off, off+bl, fill=bc, width=bw)
        canvas.create_line(off, h-off-bl, off, h-off, off+bl, h-off, fill=bc, width=bw)
        canvas.create_line(w-off-bl, h-off, w-off, h-off, w-off, h-off-bl, fill=bc, width=bw)

    def create_nav_buttons(self):
        icon_size = s(250)
        nav_h = icon_size + s(20)
        nav_w = (icon_size * 2) + s(200)
        
        self.nav_canvas = tk.Canvas(self, width=nav_w, height=nav_h, bg="#0a0a0a", highlightthickness=0)
        self.nav_canvas.pack(side="bottom", pady=s(40))
        
        self.btn_back_img = self.load_icon("back_arrow.png", icon_size)
        self.btn_next_img = self.load_icon("next_arrow.png", icon_size)
        
        center_y = nav_h / 2
        offset_x = icon_size // 2
        
        if self.btn_back_img:
            btn_back = self.nav_canvas.create_image(offset_x, center_y, image=self.btn_back_img, anchor="center")
            self.nav_canvas.tag_bind(btn_back, "<Button-1>", lambda e: self.controller.show_screen("HomeScreen"))
        
        if self.btn_next_img:
            btn_next = self.nav_canvas.create_image(nav_w - offset_x, center_y, image=self.btn_next_img, anchor="center")
            self.nav_canvas.tag_bind(btn_next, "<Button-1>", lambda e: self.controller.show_screen("VTOScreen"))

class CalibrationVoiceScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0a0a0a")
        self.controller = controller
        
        title = tk.Label(self, text="Voice Calibration", font=("Arial", s(56), "bold"), fg="#ffffff", bg="#0a0a0a")
        title.pack(pady=(s(150), s(20)))
        
        inst = tk.Label(self, text="Use your voice by reading the\nexample phrases below\nin Indonesian.", font=("Arial", s(20)), fg="#b8b8b8", bg="#0a0a0a", justify="center")
        inst.pack(pady=(0, s(100)))
        
        cw, ch = s(620), s(350)
        prompt_canvas = tk.Canvas(self, width=cw, height=ch, bg="#0a0a0a", highlightthickness=0)
        prompt_canvas.pack()
        
        self.draw_rounded_rect(prompt_canvas, s(10), s(10), cw-s(10), ch-s(10), s(30), outline="#4a4a6a", width=2)
        inst_text = tk.Label(self, text="Please speak clearly...", font=("Arial", s(22)), fg="#b8b8b8", bg="#0a0a0a")
        prompt_canvas.create_window(cw/2, s(80), window=inst_text)
        
        phrase_frame = tk.Frame(prompt_canvas, bg="#1a1a2e", width=s(520), height=s(150))
        prompt_canvas.create_window(cw/2, s(210), window=phrase_frame)
        phrase_label = tk.Label(phrase_frame, text="Geser ke kanan", font=("Arial", s(36), "bold"), fg="#9a8aff", bg="#1a1a2e")
        phrase_label.place(relx=0.5, rely=0.5, anchor="center")
        
        self.create_nav_buttons()

    def load_icon(self, icon_name, max_size):
        try:
            icon_path = f"assets/{icon_name}"
            if os.path.exists(icon_path):
                img = Image.open(icon_path)
                ratio = min(max_size / img.width, max_size / img.height)
                new_width = int(img.width * ratio)
                new_height = int(img.height * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
        except: pass
        return None

    def draw_rounded_rect(self, canvas, x1, y1, x2, y2, radius, **kwargs):
        points = [x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y2-radius, x2, y2, x2-radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y1+radius, x1, y1]
        return canvas.create_polygon(points, **kwargs, smooth=True, fill="")
    
    def create_nav_buttons(self):
        icon_size = s(250)
        nav_h = icon_size + s(20)
        nav_w = (icon_size * 2) + s(200)
        
        self.nav_canvas = tk.Canvas(self, width=nav_w, height=nav_h, bg="#0a0a0a", highlightthickness=0)
        self.nav_canvas.pack(side="bottom", pady=s(40))
        
        self.btn_back_img = self.load_icon("back_arrow.png", icon_size)
        self.btn_next_img = self.load_icon("next_arrow.png", icon_size)
        
        center_y = nav_h / 2
        offset_x = icon_size // 2
        
        if self.btn_back_img:
            btn_back = self.nav_canvas.create_image(offset_x, center_y, image=self.btn_back_img, anchor="center")
            self.nav_canvas.tag_bind(btn_back, "<Button-1>", lambda e: self.controller.show_screen("HomeScreen"))
        
        if self.btn_next_img:
            btn_next = self.nav_canvas.create_image(nav_w - offset_x, center_y, image=self.btn_next_img, anchor="center")
            self.nav_canvas.tag_bind(btn_next, "<Button-1>", lambda e: self.controller.show_screen("VTOScreen"))

class VTOScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0a0a0a")
        self.controller = controller
        
        dw, dh = s(1080), s(1450)
        self.display_canvas = tk.Canvas(self, width=dw, height=dh, bg="#0a0a0a", highlightthickness=0)
        self.display_canvas.pack()
        
        vto_icon_max_size = s(150) 
        
        self.shirt_img = self.load_icon("shirt_icon_vto.png", vto_icon_max_size)
        self.logout_img = self.load_icon("exit_icon_vto.png", vto_icon_max_size)
        
        icon_x_pos = s(920)
        start_y = s(100)
        padding = s(30)
        next_y = start_y + vto_icon_max_size + padding
        
        if self.shirt_img:
            shirt_id = self.display_canvas.create_image(icon_x_pos, start_y, image=self.shirt_img, anchor="center")
            self.display_canvas.tag_bind(shirt_id, "<Button-1>", lambda e: print("Shirt Clicked"))
        
        if self.logout_img:
            logout_id = self.display_canvas.create_image(icon_x_pos, next_y, image=self.logout_img, anchor="center")
            self.display_canvas.tag_bind(logout_id, "<Button-1>", lambda e: self.controller.show_screen("HomeScreen"))

        target_frame_height = s(500)
        bottom_frame = tk.Frame(self, bg="#1a1a2e", height=target_frame_height)
        bottom_frame.pack_propagate(False) 
        bottom_frame.pack(side="bottom", fill="x",)
        
        swipe_label = tk.Label(bottom_frame, text="Swipe to change", font=("Arial", s(24)), fg="#ffffff", bg="#1a1a2e")
        swipe_label.pack(pady=(s(30), s(20)))
        
        clothes_frame = tk.Frame(bottom_frame, bg="#1a1a2e")
        clothes_frame.pack()
        
        clothes = ["Classic Blazer", "Denim Jacket", "Casual Shirt"]
        for i, name in enumerate(clothes):
            # --- UBAH UKURAN CARD JADI 1:1 ---
            card_size = s(250)
            card = tk.Frame(clothes_frame, bg="#d0d0d0", width=card_size, height=card_size)
            card.grid(row=0, column=i, padx=s(50))
            if i == 0:
                card.config(highlightthickness=3, highlightbackground="#7a7aff")
            label = tk.Label(clothes_frame, text=name, font=("Arial", s(18), "bold"), fg="#ffffff", bg="#1a1a2e")
            label.grid(row=1, column=i, pady=(s(10), 0))
    
    def load_icon(self, icon_name, max_size):
        try:
            icon_path = f"assets/{icon_name}"
            if os.path.exists(icon_path):
                img = Image.open(icon_path)
                ratio = min(max_size / img.width, max_size / img.height)
                new_width = int(img.width * ratio)
                new_height = int(img.height * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
        except: pass
        return None

if __name__ == "__main__":
    app = App()
    app.mainloop()