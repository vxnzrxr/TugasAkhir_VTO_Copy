import sys

print(f"Python Version: {sys.version}")
print("-" * 30)

# 1. Cek OpenCV & MediaPipe
try:
    import cv2
    import mediapipe
    print("✅ OpenCV & MediaPipe: TERINSTALL")
except ImportError as e:
    print(f"❌ OpenCV/MediaPipe ERROR: {e}")

# 2. Cek SpeechRecognition
try:
    import speech_recognition as sr
    print("✅ SpeechRecognition: TERINSTALL")
except ImportError as e:
    print(f"❌ SpeechRecognition ERROR: {e}")

# 3. Cek PyAudio (Mic Access)
try:
    import pyaudio
    print("✅ PyAudio: TERINSTALL")
except ImportError as e:
    print(f"❌ PyAudio ERROR: {e} (Coba install pakai pipwin)")

print("-" * 30)
input("Tekan Enter untuk keluar...")