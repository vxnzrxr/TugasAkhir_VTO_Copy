import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageDraw
import os
import threading
import time
from gesture_mode.hand_gesture import HandGestureDetector
from gesture_mode.virtual_tryon import VirtualTryOnApp


# --- LIBRARY TAMBAHAN ---
try:
    import cv2
    import mediapipe as mp
    HAS_CV = True
except ImportError:
    HAS_CV = False
    print("⚠️ Library OpenCV/MediaPipe belum diinstall.")

try:
    import speech_recognition as sr
    HAS_VOICE = True
except ImportError:
    HAS_VOICE = False
    print("⚠️ Library SpeechRecognition belum diinstall.")

# --- KONFIGURASI SKALA ---
IS_DEV = True 
ORIGINAL_WIDTH = 1080
ORIGINAL_HEIGHT = 1920

if IS_DEV:
    TARGET_HEIGHT = 850 
    SCALE_FACTOR = TARGET_HEIGHT / ORIGINAL_HEIGHT
else:
    SCALE_FACTOR = 1.0

def s(value):
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
        # self.resizable(IS_DEV, IS_DEV) 
        
        container = tk.Frame(self, bg="#0a0a0a")
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.screens = {}
        
        # --- UPDATE DAFTAR SCREEN DISINI ---
        for F in (HomeScreen, 
                  CalibrationGestureScreen, VTOGestureScreen, # Pasangan Gesture
                  CalibrationTouchScreen, VTOTouchScreen,     # Pasangan Touch
                  CalibrationVoiceScreen, VTOVoiceScreen):    # Pasangan Voice
            screen_name = F.__name__
            screen = F(parent=container, controller=self)
            self.screens[screen_name] = screen
            screen.grid(row=0, column=0, sticky="nsew")
        
        self.show_screen("HomeScreen")
    
    def show_screen(self, screen_name):
        for screen in self.screens.values():
            if hasattr(screen, "on_hide"):
                screen.on_hide()
        screen = self.screens[screen_name]
        screen.tkraise()
        if hasattr(screen, "on_show"):
            screen.on_show()

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

# ------------------------------------------------------------------
# SCREEN 1: GESTURE CALIBRATION (FIXED CAMERA ASPECT RATIO)
# ------------------------------------------------------------------
class CalibrationGestureScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0a0a0a")
        self.controller = controller
        self.cap = None
        self.is_running = False
        self.detector = None
        self.vto = None
        
        # Variabel untuk logika tombol
        self.hover_start_time = 0
        self.hover_duration = 1.5  # Waktu (detik) untuk memicu klik
        self.is_button_active = False # Status apakah tombol sedang di-hover
        
        self.success_triggered = False

        if HAS_CV:
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
            self.mp_draw = mp.solutions.drawing_utils
        
        title = tk.Label(self, text="Gesture Calibration", font=("Arial", s(56), "bold"), fg="#ffffff", bg="#0a0a0a")
        title.pack(pady=(s(100), s(20)))
        
        self.status_label = tk.Label(self, text="Initializing Camera...", font=("Arial", s(20)), fg="#b8b8b8", bg="#0a0a0a", justify="center")
        self.status_label.pack(pady=(0, s(30)))
        
        self.cw, self.ch = s(620), s(800)
        self.preview_canvas = tk.Canvas(self, width=self.cw, height=self.ch, bg="#1a1a2e", highlightthickness=2, highlightbackground="#4a4a6a")
        self.preview_canvas.pack()
        
        self.create_nav_buttons() 

    def on_show(self):
        self.success_triggered = False  # <--- RESET STATUS DISINI

        if HAS_CV:
            self.detector = HandGestureDetector()
            self.vto = VirtualTryOnApp()
            self.is_running = True
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("⚠️ Kamera tidak terbuka!")
            self.status_label.config(text="Angkat tangan ke depan kamera", fg="#b8b8b8")
            self.update_camera()
        else:
            self.status_label.config(text="Library OpenCV tidak ditemukan.", fg="#ff5555")

    def on_hide(self):
        self.is_running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.preview_canvas.delete("all") 

    def update_camera(self):
        if not self.is_running or self.cap is None:
            return

        ret, frame = self.cap.read()
        if ret:
            # 1. Mirror & Convert
            frame = cv2.flip(frame, 1)
            frame_h, frame_w, _ = frame.shape
            
            cursor_pos_ui = None
            gesture_detected = "none"

            # 2. Detect Hands
            if self.detector:
                _, gesture, finger_pos = self.detector.process_frame(frame)
                gesture_detected = gesture
                
                if gesture != "none":
                    self.status_label.config(text=f"Gesture: {gesture.upper()}", fg="#55ff55")
                else:
                    self.status_label.config(text="Webcam Aktif (Arahkan Tangan)", fg="#b8b8b8")
                
                # Update VTO logic (background)
                if self.vto:
                    self.vto.apply_gesture(gesture, frame, finger_pos)
            
            # 3. --- PROSES GAMBAR UNTUK UI (CROP & SCALE) ---
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            
            img_w, img_h = img.size
            target_w, target_h = self.cw, self.ch
            
            # Hitung scaling factor (cover)
            scale = max(target_w / img_w, target_h / img_h)
            new_w = int(img_w * scale)
            new_h = int(img_h * scale)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            # Hitung offset crop
            left = (new_w - target_w) // 2
            top = (new_h - target_h) // 2
            right = left + target_w
            bottom = top + target_h
            img = img.crop((left, top, right, bottom))
            
            # 4. --- TRANSFORMASI KOORDINAT CURSOR ---
            # Kita perlu mengubah koordinat jari (dari frame kamera asli) ke koordinat Canvas UI
            if finger_pos:
                fx, fy = finger_pos
                # Scale
                ui_x = fx * scale
                ui_y = fy * scale
                # Adjust for Crop
                ui_x -= left
                ui_y -= top
                cursor_pos_ui = (ui_x, ui_y)

            # 5. Render ke Canvas
            self.photo = ImageTk.PhotoImage(img)
            self.preview_canvas.create_image(0, 0, image=self.photo, anchor="nw")
            
            # 6. Gambar UI Overlay (Tombol & Cursor)
            self.draw_overlay_ui(gesture_detected, cursor_pos_ui)
            
            self.draw_corner_brackets(self.preview_canvas, self.cw, self.ch)
        
        self.after(33, self.update_camera)

    def draw_overlay_ui(self, gesture, cursor_pos):
        """Menggambar tombol interaktif dan kursor di atas kamera"""
        
        btn_w, btn_h = s(250), s(80)
        btn_x1 = (self.cw - btn_w) // 2
        btn_y1 = (self.ch // 2) - s(150) # Posisi agak ke atas
        btn_x2 = btn_x1 + btn_w
        btn_y2 = btn_y1 + btn_h
        
        is_hovering = False
        progress = 0
        
        # --- LOGIKA HIT TESTING ---
        if cursor_pos:
            cx, cy = cursor_pos
            if btn_x1 < cx < btn_x2 and btn_y1 < cy < btn_y2:
                # Menerima gestur 'pointing' (atau 'move' untuk jaga-jaga jika file lama belum ke-update)
                if gesture == "pointing" or gesture == "move":
                    is_hovering = True
        
        # --- LOGIKA WAKTU (DWELL TIME) ---
        if is_hovering and not self.success_triggered: # Cek jika belum sukses sebelumnya
            if not self.is_button_active:
                self.hover_start_time = time.time()
                self.is_button_active = True
            
            elapsed = time.time() - self.hover_start_time
            progress = min(elapsed / self.hover_duration, 1.0)
            
            if progress >= 1.0:
                # --- AKSI SUKSES & PINDAH HALAMAN ---
                btn_color = "#55ff55"
                btn_text = "SUCCESS!"
                self.success_triggered = True # Kunci agar tidak terpanggil berkali-kali
                
                # Beri jeda 0.5 detik agar user sempat lihat tulisan "SUCCESS" sebelum pindah
                self.after(500, lambda: self.controller.show_screen("VTOGestureScreen"))
                
            else:
                btn_color = "#ffaa55"
                btn_text = "HOLD..."
        else:
            # Jika sudah sukses, biarkan tombol hijau sampai pindah
            if self.success_triggered:
                btn_color = "#55ff55"
                btn_text = "SUCCESS!"
                progress = 1.0
            else:
                self.is_button_active = False
                progress = 0
                btn_color = "#4a4a6a"
                btn_text = "TEST BUTTON"

        # --- GAMBAR TOMBOL ---
        self.draw_rounded_rect(self.preview_canvas, btn_x1, btn_y1, btn_x2, btn_y2, s(20), fill=btn_color, outline="white", width=2)
        
        if progress > 0 and progress < 1.0:
            load_w = (btn_x2 - btn_x1) * progress
            self.preview_canvas.create_rectangle(btn_x1, btn_y2-s(10), btn_x1+load_w, btn_y2, fill="#ffffff", outline="")

        self.preview_canvas.create_text((btn_x1+btn_x2)//2, (btn_y1+btn_y2)//2, text=btn_text, font=("Arial", s(20), "bold"), fill="white")

        # --- GAMBAR CURSOR ---
        if cursor_pos:
            cx, cy = cursor_pos
            r = s(15)
            # Cursor hijau jika pointing/move, merah jika lainnya
            cur_color = "#00ff00" if (gesture == "pointing" or gesture == "move") else "#ff0000"
            self.preview_canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=cur_color, outline="white", width=2)

    # ... (Method load_icon, draw_corner_brackets, draw_rounded_rect, create_nav_buttons SAMA SEPERTI SEBELUMNYA) ...
    def load_icon(self, icon_name, max_size):
        # ... (Salin kode load_icon yang lama) ...
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
        return canvas.create_polygon(points, **kwargs, smooth=True)

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
        
        self.inst_label = tk.Label(self, text="Touch the target.", font=("Arial", s(20)), fg="#b8b8b8", bg="#0a0a0a", justify="center")
        self.inst_label.pack(pady=(0, s(80)))
        
        self.cw, self.ch = s(620), s(800)
        self.calib_canvas = tk.Canvas(self, width=self.cw, height=self.ch, bg="#0f0f1e", highlightthickness=2, highlightbackground="#4a4a6a")
        self.calib_canvas.pack()
        
        self.targets = [
            (s(150), s(150), s(80), 1),
            (s(470), s(250), s(60), 2),
            (s(310), s(380), s(45), 3),
            (s(180), s(570), s(70), 4),
            (s(450), s(630), s(90), 5)
        ]
        self.current_target_index = 0
        
        self.create_nav_buttons()

    def on_show(self):
        self.current_target_index = 0
        self.inst_label.config(text="Sentuh target yang muncul satu per satu.", fg="#b8b8b8")
        self.draw_targets()

    def on_hide(self):
        pass

    def draw_targets(self):
        self.calib_canvas.delete("all")
        self.draw_corner_brackets(self.calib_canvas, self.cw, self.ch)
        
        if self.current_target_index < len(self.targets):
            x, y, size, num = self.targets[self.current_target_index]
            for i in range(3, 0, -1):
                self.calib_canvas.create_oval(x-size*i/2, y-size*i/2, x+size*i/2, y+size*i/2, fill="#6a5aff", outline="", tags="target")
            self.calib_canvas.create_oval(x-size/2, y-size/2, x+size/2, y+size/2, fill="#8a7aff", outline="", tags="target")
            self.calib_canvas.create_text(x, y, text=str(num), font=("Arial", s(20), "bold"), fill="#ffffff", tags="target")
            self.calib_canvas.tag_bind("target", "<Button-1>", self.on_target_click)
        else:
            self.calib_canvas.create_text(self.cw/2, self.ch/2, text="Selesai!", font=("Arial", s(40), "bold"), fill="#55ff55")
            self.inst_label.config(text="Kalibrasi Touch Berhasil.", fg="#55ff55")
            self.after(1000, lambda: self.controller.show_screen("VTOTouchScreen"))

    def on_target_click(self, event):
        self.current_target_index += 1
        self.draw_targets()

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
        self.is_listening = False
        
        title = tk.Label(self, text="Voice Calibration", font=("Arial", s(56), "bold"), fg="#ffffff", bg="#0a0a0a")
        title.pack(pady=(s(150), s(20)))
        
        inst = tk.Label(self, text="Use your voice by reading the\nexample phrases below\nin Indonesian.", font=("Arial", s(20)), fg="#b8b8b8", bg="#0a0a0a", justify="center")
        inst.pack(pady=(0, s(100)))
        
        cw, ch = s(620), s(350)
        self.prompt_canvas = tk.Canvas(self, width=cw, height=ch, bg="#0a0a0a", highlightthickness=0)
        self.prompt_canvas.pack()
        
        self.draw_rounded_rect(self.prompt_canvas, s(10), s(10), cw-s(10), ch-s(10), s(30), outline="#4a4a6a", width=2)
        
        self.status_text = tk.Label(self, text="Silakan bicara...", font=("Arial", s(22)), fg="#b8b8b8", bg="#0a0a0a")
        self.prompt_canvas.create_window(cw/2, s(80), window=self.status_text)
        
        phrase_frame = tk.Frame(self.prompt_canvas, bg="#1a1a2e", width=s(520), height=s(150))
        self.prompt_canvas.create_window(cw/2, s(210), window=phrase_frame)
        phrase_label = tk.Label(phrase_frame, text="Geser ke kanan", font=("Arial", s(36), "bold"), fg="#9a8aff", bg="#1a1a2e")
        phrase_label.place(relx=0.5, rely=0.5, anchor="center")
        
        self.create_nav_buttons()

    def on_show(self):
        if HAS_VOICE:
            self.is_listening = True
            self.status_text.config(text="Mendengarkan...", fg="#ffff55")
            threading.Thread(target=self.listen_loop, daemon=True).start()
        else:
            self.status_text.config(text="Mic tidak terdeteksi.", fg="#ff5555")

    def on_hide(self):
        self.is_listening = False

    def listen_loop(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            while self.is_listening:
                try:
                    audio = r.listen(source, timeout=3, phrase_time_limit=3)
                    text = r.recognize_google(audio, language="id-ID")
                    self.after(0, lambda t=text: self.update_status(t))
                except:
                    pass 

    def update_status(self, text):
        text = text.lower()
        if "geser" in text or "kanan" in text:
            self.controller.show_screen("VTOVoiceScreen")
        else:
            self.status_text.config(text=f"Terdengar: '{text}'", fg="#ffffff")

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
    
    def on_show(self): pass
    def on_hide(self): pass

class VTOGestureScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0a0a0a")
        self.controller = controller
        self.cap = None
        self.is_running = False
        self.detector = None
        
        self.clothes = ["Classic Blazer", "Denim Jacket", "Casual Shirt"]
        self.selected_index = 0
        
        # Load Icons (Pastikan Anda punya icon ini di folder assets)
        # Jika tidak ada, kode akan fallback ke kotak berwarna
        self.icon_shirt = self.load_icon("shirt_icon.png", s(60))
        self.icon_exit = self.load_icon("exit_icon.png", s(60))
        
        # Canvas Utama
        self.cw, self.ch = s(1080), s(1920)
        self.bg_canvas = tk.Canvas(self, width=self.cw, height=self.ch, bg="#0a0a0a", highlightthickness=0)
        self.bg_canvas.pack(fill="both", expand=True)

    def on_show(self):
        if HAS_CV:
            self.detector = HandGestureDetector()
            self.is_running = True
            self.cap = cv2.VideoCapture(0)
            self.update_camera()
            
    def on_hide(self):
        self.is_running = False
        if self.cap: self.cap.release()
        self.bg_canvas.delete("all")

    def update_camera(self):
        if not self.is_running or self.cap is None: return

        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            
            # 1. Deteksi Gestur
            cursor_pos = None
            gesture = "none"
            if self.detector:
                _, gesture, finger_pos = self.detector.process_frame(frame)
                
            # 2. Gambar Kamera (Full Screen Crop)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img_w, img_h = img.size
            target_w, target_h = self.cw, self.ch
            scale = max(target_w / img_w, target_h / img_h)
            new_w, new_h = int(img_w * scale), int(img_h * scale)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            left = (new_w - target_w) // 2
            top = (new_h - target_h) // 2
            img = img.crop((left, top, left + target_w, top + target_h))
            
            # 3. Transformasi Cursor
            if finger_pos:
                fx, fy = finger_pos
                ui_x = (fx * scale) - left
                ui_y = (fy * scale) - top
                cursor_pos = (ui_x, ui_y)
            
            self.photo = ImageTk.PhotoImage(img)
            self.bg_canvas.create_image(0, 0, image=self.photo, anchor="nw")
            
            # 4. Gambar UI Baru
            self.draw_modern_ui(gesture, cursor_pos)
            
        self.after(33, self.update_camera)

    def draw_modern_ui(self, gesture, cursor_pos):
        # --- A. TOMBOL SIDEBAR (KANAN ATAS) ---
        # Tombol Baju (Ungu)
        btn_size = s(120)
        margin_right = s(40)
        margin_top = s(80)
        gap = s(40)
        
        btn_shirt_x1 = self.cw - margin_right - btn_size
        btn_shirt_y1 = margin_top
        btn_shirt_x2 = btn_shirt_x1 + btn_size
        btn_shirt_y2 = btn_shirt_y1 + btn_size
        
        self.draw_rounded_rect(self.bg_canvas, btn_shirt_x1, btn_shirt_y1, btn_shirt_x2, btn_shirt_y2, s(30), fill="#2d2d44", outline="#4a4a6a", width=0)
        if self.icon_shirt:
            self.bg_canvas.create_image((btn_shirt_x1+btn_shirt_x2)//2, (btn_shirt_y1+btn_shirt_y2)//2, image=self.icon_shirt)

        # Tombol Exit (Merah Kecoklatan)
        btn_exit_x1 = btn_shirt_x1
        btn_exit_y1 = btn_shirt_y2 + gap
        btn_exit_x2 = btn_exit_x1 + btn_size
        btn_exit_y2 = btn_exit_y1 + btn_size
        
        self.draw_rounded_rect(self.bg_canvas, btn_exit_x1, btn_exit_y1, btn_exit_x2, btn_exit_y2, s(30), fill="#442d2d", outline="#6a4a4a", width=0)
        if self.icon_exit:
            self.bg_canvas.create_image((btn_exit_x1+btn_exit_x2)//2, (btn_exit_y1+btn_exit_y2)//2, image=self.icon_exit)

        # --- B. AREA BAWAH (GRADASI GELAP) ---
        # Kita buat kotak semi-transparan di bawah untuk menampung kartu (simulasi gradasi)
        # Tkinter tidak support alpha channel native di rectangle, jadi kita pakai warna solid gelap saja
        panel_h = s(550)
        panel_y = self.ch - panel_h
        # self.bg_canvas.create_rectangle(0, panel_y, self.cw, self.ch, fill="#0a0a0a", outline="") # Opsional jika mau background penuh
        
        # Text "Swipe to change"
        self.bg_canvas.create_text(self.cw//2, panel_y + s(50), text="Swipe to change", font=("Arial", s(20)), fill="white")

        # --- C. KARTU BAJU ---
        card_w, card_h = s(280), s(320)
        card_gap = s(40)
        total_w = (card_w * 3) + (card_gap * 2)
        start_x = (self.cw - total_w) // 2
        card_start_y = panel_y + s(100)
        
        for i, name in enumerate(self.clothes):
            x = start_x + (i * (card_w + card_gap))
            y = card_start_y
            
            # Warna Border & Isi
            is_selected = (i == self.selected_index)
            border_col = "#6a5aff" if is_selected else "" # Ungu jika selected
            border_w = s(6) if is_selected else 0
            fill_col = "#d9d9d9" # Abu-abu terang sesuai desain
            
            # Cek Hover & Click
            if cursor_pos:
                cx, cy = cursor_pos
                # Hover detection
                if x < cx < x+card_w and y < cy < y+card_h:
                    if gesture == "selecting" or gesture == "pointing":
                        self.selected_index = i
                
                # Exit Button Click Detection
                if btn_exit_x1 < cx < btn_exit_x2 and btn_exit_y1 < cy < btn_exit_y2:
                    if gesture == "selecting" or gesture == "pointing":
                        self.controller.show_screen("HomeScreen")

            # Gambar Kartu
            self.draw_rounded_rect(self.bg_canvas, x, y, x+card_w, y+card_h, s(20), fill=fill_col, outline=border_col, width=border_w)
            
            # Label Nama
            self.bg_canvas.create_text(x + card_w//2, y + card_h + s(30), text=name, font=("Arial", s(16), "bold"), fill="white")

        # --- D. CURSOR ---
        if cursor_pos:
            cx, cy = cursor_pos
            cr = s(15)
            cc = "#00ff00" if gesture == "pointing" else ("#ffff00" if gesture == "selecting" else "#ff0000")
            self.bg_canvas.create_oval(cx-cr, cy-cr, cx+cr, cy+cr, fill=cc, outline="white", width=2)

    def draw_rounded_rect(self, canvas, x1, y1, x2, y2, radius, **kwargs):
        points = [x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y2-radius, x2, y2, x2-radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y1+radius, x1, y1]
        return canvas.create_polygon(points, **kwargs, smooth=True)

    def load_icon(self, icon_name, target_size):
        try:
            path = f"assets/{icon_name}"
            if os.path.exists(path):
                img = Image.open(path)
                img = img.resize((target_size, target_size), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
        except: pass
        return None

class VTOTouchScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0a0a0a")
        self.controller = controller
        self.clothes = ["Classic Blazer", "Denim Jacket", "Casual Shirt"]
        self.selected_index = 0
        
        # Load Icons
        self.icon_shirt = self.load_icon("shirt_icon.png", s(60))
        self.icon_exit = self.load_icon("exit_icon.png", s(60))
        
        self.cw, self.ch = s(1080), s(1920)
        self.canvas = tk.Canvas(self, width=self.cw, height=self.ch, bg="#0a0a0a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Bind klik mouse ke fungsi handle_click
        self.canvas.bind("<Button-1>", self.handle_click)
        self.draw_ui()

    def handle_click(self, event):
        x, y = event.x, event.y
        
        # Cek klik Tombol Exit
        btn_size = s(120)
        margin_right = s(40)
        margin_top = s(80) + s(120) + s(40) # Posisi tombol kedua (Exit)
        
        exit_x1 = self.cw - margin_right - btn_size
        exit_y1 = margin_top
        exit_x2 = exit_x1 + btn_size
        exit_y2 = exit_y1 + btn_size
        
        if exit_x1 < x < exit_x2 and exit_y1 < y < exit_y2:
            self.controller.show_screen("HomeScreen")
            return

        # Cek klik Kartu Baju
        panel_h = s(550)
        panel_y = self.ch - panel_h
        card_w, card_h = s(280), s(320)
        card_gap = s(40)
        total_w = (card_w * 3) + (card_gap * 2)
        start_x = (self.cw - total_w) // 2
        card_start_y = panel_y + s(100)
        
        for i in range(len(self.clothes)):
            cx = start_x + (i * (card_w + card_gap))
            cy = card_start_y
            if cx < x < cx+card_w and cy < y < cy+card_h:
                self.selected_index = i
                self.draw_ui() # Redraw untuk update border
                break

    def draw_ui(self):
        self.canvas.delete("all")
        
        # --- A. TOMBOL SIDEBAR ---
        btn_size = s(120)
        margin_right = s(40)
        margin_top = s(80)
        gap = s(40)
        
        # Shirt Btn
        bx1 = self.cw - margin_right - btn_size
        by1 = margin_top
        self.draw_rounded_rect(self.canvas, bx1, by1, bx1+btn_size, by1+btn_size, s(30), fill="#2d2d44", outline="#4a4a6a")
        if self.icon_shirt:
             self.canvas.create_image(bx1+btn_size//2, by1+btn_size//2, image=self.icon_shirt)

        # Exit Btn
        ex1 = bx1
        ey1 = by1 + btn_size + gap
        self.draw_rounded_rect(self.canvas, ex1, ey1, ex1+btn_size, ey1+btn_size, s(30), fill="#442d2d", outline="#6a4a4a")
        if self.icon_exit:
             self.canvas.create_image(ex1+btn_size//2, ey1+btn_size//2, image=self.icon_exit)

        # --- B. AREA BAWAH ---
        panel_h = s(550)
        panel_y = self.ch - panel_h
        self.canvas.create_text(self.cw//2, panel_y + s(50), text="Tap to select", font=("Arial", s(20)), fill="white")

        # --- C. KARTU ---
        card_w, card_h = s(280), s(320)
        card_gap = s(40)
        total_w = (card_w * 3) + (card_gap * 2)
        start_x = (self.cw - total_w) // 2
        card_start_y = panel_y + s(100)
        
        for i, name in enumerate(self.clothes):
            x = start_x + (i * (card_w + card_gap))
            y = card_start_y
            
            is_selected = (i == self.selected_index)
            border_col = "#6a5aff" if is_selected else ""
            border_w = s(6) if is_selected else 0
            
            self.draw_rounded_rect(self.canvas, x, y, x+card_w, y+card_h, s(20), fill="#d9d9d9", outline=border_col, width=border_w)
            self.canvas.create_text(x + card_w//2, y + card_h + s(30), text=name, font=("Arial", s(16), "bold"), fill="white")

    def draw_rounded_rect(self, canvas, x1, y1, x2, y2, radius, **kwargs):
        points = [x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y2-radius, x2, y2, x2-radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y1+radius, x1, y1]
        return canvas.create_polygon(points, **kwargs, smooth=True)

    def load_icon(self, icon_name, target_size):
        try:
            path = f"assets/{icon_name}"
            if os.path.exists(path):
                img = Image.open(path)
                img = img.resize((target_size, target_size), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
        except: pass
        return None
    
    def on_show(self): pass
    def on_hide(self): pass

class VTOVoiceScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0a0a0a")
        self.controller = controller
        self.is_listening = False
        self.clothes = ["Classic Blazer", "Denim Jacket", "Casual Shirt"]
        self.selected_index = 0
        
        # Load Icons
        self.icon_shirt = self.load_icon("shirt_icon.png", s(60))
        self.icon_exit = self.load_icon("exit_icon.png", s(60))

        self.cw, self.ch = s(1080), s(1920)
        self.canvas = tk.Canvas(self, width=self.cw, height=self.ch, bg="#0a0a0a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Variabel Status untuk Feedback UI
        self.last_command = "Menunggu..."
        
        self.draw_ui()

    def on_show(self):
        self.is_listening = True
        self.last_command = "Mendengarkan..."
        self.draw_ui()
        if HAS_VOICE:
            threading.Thread(target=self.listen_loop, daemon=True).start()
    
    def on_hide(self):
        self.is_listening = False

    def draw_ui(self):
        self.canvas.delete("all")
        
        # --- A. TOMBOL SIDEBAR ---
        btn_size = s(120)
        margin_right = s(40)
        margin_top = s(80)
        gap = s(40)
        
        # Ikon Baju
        bx1, by1 = self.cw - margin_right - btn_size, margin_top
        self.draw_rounded_rect(self.canvas, bx1, by1, bx1+btn_size, by1+btn_size, s(30), fill="#2d2d44", outline="#4a4a6a")
        if self.icon_shirt: self.canvas.create_image(bx1+btn_size//2, by1+btn_size//2, image=self.icon_shirt)

        # Ikon Keluar
        ex1, ey1 = bx1, by1 + btn_size + gap
        self.draw_rounded_rect(self.canvas, ex1, ey1, ex1+btn_size, ey1+btn_size, s(30), fill="#442d2d", outline="#6a4a4a")
        if self.icon_exit: self.canvas.create_image(ex1+btn_size//2, ey1+btn_size//2, image=self.icon_exit)

        # --- B. STATUS SUARA (BAHASA INDONESIA) ---
        panel_h = s(550)
        panel_y = self.ch - panel_h
        
        # Judul Instruksi
        self.canvas.create_text(self.cw//2, panel_y + s(50), text="Katakan 'Lanjut', 'Kembali', atau 'Keluar'", font=("Arial", s(20)), fill="#b0b0b0")
        
        # Feedback Status (Apa yang didengar)
        self.canvas.create_text(self.cw//2, panel_y + s(100), text=f"Status: {self.last_command}", font=("Arial", s(24), "bold"), fill="#55ff55")

        # --- C. KARTU BAJU ---
        card_w, card_h = s(280), s(320)
        card_gap = s(40)
        total_w = (card_w * 3) + (card_gap * 2)
        start_x = (self.cw - total_w) // 2
        card_start_y = panel_y + s(180) # Turun sedikit agar tidak menabrak teks status
        
        for i, name in enumerate(self.clothes):
            x = start_x + (i * (card_w + card_gap))
            y = card_start_y
            
            is_selected = (i == self.selected_index)
            border_col = "#6a5aff" if is_selected else ""
            border_w = s(6) if is_selected else 0
            
            self.draw_rounded_rect(self.canvas, x, y, x+card_w, y+card_h, s(20), fill="#d9d9d9", outline=border_col, width=border_w)
            self.canvas.create_text(x + card_w//2, y + card_h + s(30), text=name, font=("Arial", s(16), "bold"), fill="white")

    def listen_loop(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            while self.is_listening:
                try:
                    # Dengarkan audio (Batas 3 detik agar responsif)
                    audio = r.listen(source, timeout=3, phrase_time_limit=3)
                    
                    # 1. Konversi Suara ke Teks (Pakai Bahasa Indonesia)
                    text = r.recognize_google(audio, language="id-ID").lower()
                    print(f"User berkata: {text}")
                    
                    # 2. Proses Intent (NLU)
                    intent = self.process_intent_indonesia(text)
                    
                    # 3. Eksekusi Perintah
                    need_update = True
                    if intent == "NEXT":
                        self.selected_index = (self.selected_index + 1) % len(self.clothes)
                        self.last_command = f"Diterima: '{text}' (Lanjut)"
                    elif intent == "PREV":
                        self.selected_index = (self.selected_index - 1) % len(self.clothes)
                        self.last_command = f"Diterima: '{text}' (Kembali)"
                    elif intent == "EXIT":
                        self.controller.show_screen("HomeScreen")
                        break
                    else:
                        self.last_command = f"Tidak paham: '{text}'"
                        need_update = True # Tetap update UI untuk menampilkan teks error
                    
                    if need_update:
                        self.after(0, self.draw_ui)
                        
                except sr.WaitTimeoutError:
                    pass # Tidak ada suara, lanjut loop
                except Exception as e:
                    # Error koneksi atau tidak jelas
                    pass

    def process_intent_indonesia(self, text):
        """
        Logika NLU Sederhana pengganti IndoBERT untuk performa tinggi.
        Mencocokkan kata kunci sinonim bahasa Indonesia.
        """
        # Daftar Sinonim untuk Intent
        synonyms_next = ["lanjut", "lanjutkan", "selanjutnya", "berikutnya", "kanan", "ganti", "yang lain", "next"]
        synonyms_prev = ["kembali", "balik", "sebelumnya", "mundur", "kiri", "back"]
        synonyms_exit = ["keluar", "tutup", "selesai", "menu", "utama", "exit"]
        
        # Cek kecocokan kata
        for word in synonyms_next:
            if word in text: return "NEXT"
            
        for word in synonyms_prev:
            if word in text: return "PREV"
            
        for word in synonyms_exit:
            if word in text: return "EXIT"
            
        return "UNKNOWN"

    # --- Integrasi IndoBERT (Opsional) ---
    # Jika Anda WAJIB menggunakan IndoBERT (misal untuk Skripsi/Tugas Akhir), 
    # Anda perlu menginstall library: pip install transformers torch scipy
    # Lalu uncomment method di bawah ini dan panggil di listen_loop.
    """
    def predict_with_indobert(self, text):
        try:
            from transformers import pipeline
            # Menggunakan Zero-Shot Classification (Memerlukan internet untuk download model pertama kali)
            # Model XLM-RoBERTa biasanya lebih baik untuk Zero-Shot multibahasa daripada IndoBERT base raw.
            classifier = pipeline("zero-shot-classification", model="oxford-nlp/elas-roc-large") 
            
            labels = ["lanjut", "kembali", "keluar"]
            result = classifier(text, labels)
            
            # Ambil label dengan skor tertinggi
            top_label = result['labels'][0]
            score = result['scores'][0]
            
            if score > 0.5: # Threshold keyakinan
                if top_label == "lanjut": return "NEXT"
                if top_label == "kembali": return "PREV"
                if top_label == "keluar": return "EXIT"
            return "UNKNOWN"
        except ImportError:
            print("Library transformers tidak ditemukan. Gunakan keyword matching biasa.")
            return self.process_intent_indonesia(text)
    """

    def draw_rounded_rect(self, canvas, x1, y1, x2, y2, radius, **kwargs):
        points = [x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y2-radius, x2, y2, x2-radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y1+radius, x1, y1]
        return canvas.create_polygon(points, **kwargs, smooth=True)

    def load_icon(self, icon_name, target_size):
        try:
            path = f"assets/{icon_name}"
            if os.path.exists(path):
                img = Image.open(path)
                img = img.resize((target_size, target_size), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
        except: pass
        return None

if __name__ == "__main__":
    app = App()
    app.mainloop()