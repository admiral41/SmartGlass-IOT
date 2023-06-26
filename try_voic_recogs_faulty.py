import cv2
import face_recognition
import os
import sounddevice as sd
import speech_recognition as sr
from espeak import espeak
import RPi.GPIO as GPIO
import pytesseract
import subprocess
import psutil

# Add the import statement for speech_recognition
import speech_recognition as sr

# Rest of the code...
current_mode = None
current_process = None

def recognize_speech():
    r = sr.Recognizer()
    recorded_audio = []

    def callback(indata, frames, time, status):
        if status:
            print("Error:", status)
        recorded_audio.append(indata.copy())

    with sd.InputStream(callback=callback, channels=1, dtype="int16"):
        print("Listening...")
        sd.sleep(int(5 * 1000))

    audio_data = b"".join(recorded_audio)
    audio = sr.AudioData(audio_data, sample_rate=48000, sample_width=2)

    try:
        text = r.recognize_google(audio, language="en-US")
        print("You said:", text)
        return text.lower()
    except sr.UnknownValueError:
        print("Sorry, could not understand audio")
        return ""

def face_recognition_mode():
    global current_mode, current_process
    current_mode = "face recognition"
    current_process = subprocess.Popen(["lxterminal", "-e", "python facewithvoice.py"])

def object_detection_mode():
    global current_mode, current_process
    current_mode = "object detection"
    current_process = subprocess.Popen(["lxterminal", "-e", "python test.py"])

def image_to_text_mode():
    global current_mode, current_process
    current_mode = "image to text"
    current_process = subprocess.Popen(["lxterminal", "-e", "python imgtotext.py"])

def close_terminal():
    global current_process
    if current_process is not None:
        current_process.terminate()  # Terminate the process
        subprocess.Popen(["pkill", "-f", current_process.args[2]])  # Terminate the associated terminal window
        current_process = None

# Rest of the code...

if __name__ == "__main__":
    espeak.synth("Welcome to Smart Assist!")
    espeak.synth("To choose a mode, please say:")
    espeak.synth("Face Recognition")
    espeak.synth("Object Detection")
    espeak.synth("Image to Text")
    
    while True:
        if current_mode is None:
            print("Select a mode:")
            print("1. Face Recognition")
            print("2. Object Detection")
            print("3. Image to Text")
            print("4. Quit")
        else:
            print(f"Currently in {current_mode} mode. Say 'Go back' to switch modes.")
            print("1. Face Recognition")
            print("2. Object Detection")
            print("3. Image to Text")
            print("4. Quit")

        choice = recognize_speech()

        if current_mode is not None and "go back" in choice:
            print("Going back to mode selection...")
            espeak.synth("Going back to mode selection")
            close_terminal()
            current_mode = None
        elif current_mode is None:
            if "face recognition" in choice or choice == "1":
                print("Switching to face recognition mode...")
                espeak.synth("Switching to face recognition mode")
                face_recognition_mode()
            elif "object detection" in choice or choice == "2":
                print("Switching to object detection mode...")
                espeak.synth("Switching to object detection mode")
                object_detection_mode()
            elif "image to text" in choice or choice == "3":
                print("Switching to image to text mode...")
                espeak.synth("Switching to image to text mode")
                image_to_text_mode()
            elif "quit" in choice or choice == "4":
                print("Exiting the program...")
                espeak.synth("Exiting the program")
                close_terminal()
                break
            else:
                print("Invalid choice. Please try again.")
        else:
            print("Invalid choice. Please say 'Go back' to switch modes.")
