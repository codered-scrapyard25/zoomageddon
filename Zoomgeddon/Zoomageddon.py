import time
import base64
import pyttsx3
import pyautogui
import pyaudio  
import wave
import assemblyai as aai
from groq import Groq
import os
import random
import pygame
import webbrowser
import threading
import platform
import pygetwindow as gw

# Initialize API Clients
aai.settings.api_key = ""
client = Groq(api_key='')
transcriber = aai.Transcriber()

pygame.mixer.init()     # Initialize pygame mixer

SOUND_FOLDER = "Weird Sounds/."    # Folder containing sound files

# List of websites to open
websites = []

# List of common browser names to check in the active window title
BROWSER_KEYWORDS = ["Chrome", "Firefox", "Edge", "Opera", "Safari", "Brave", "Vivaldi", "Tor", "Chromium"]

# Functions from Process 1
def record_audio(output_filename="output.wav", record_seconds=10):
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                        input=True, frames_per_buffer=CHUNK)
    
    print("Recording...")
    frames = []
    
    for _ in range(0, int(RATE / CHUNK * record_seconds)):
        data = stream.read(CHUNK)
        frames.append(data)
    
    print("Recording finished.")
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    with wave.open(output_filename, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))
    
    print(f"Audio recorded and saved as {output_filename}")

def take_screenshot(output_path="screenshot.png"):
    screenshot = pyautogui.screenshot()
    screenshot.save(output_path)
    print(f"Screenshot saved as {output_path}")

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def getimgcaption(image_path):
    base64_image = encode_image(image_path)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe the person in the image and their surroundings."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                ],
            }
        ],
        model="llama-3.2-11b-vision-preview",
    )
    return chat_completion.choices[0].message.content

def generate_dialog(prompt, imgcaption, context):
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt + context + imgcaption}],
        model="llama3-70b-8192",
    )
    return chat_completion.choices[0].message.content

def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Function from Process 3
def is_browser_in_focus():
    if not gw:
        return False
    try:
        active_window = gw.getActiveWindow()
        if active_window:
            window_title = active_window.title
            return any(browser.lower() in window_title.lower() for browser in BROWSER_KEYWORDS)
    except Exception as e:
        print(f"Error detecting active window: {e}")
    return False

# Thread functions
def process_1():
    print("Starting Process 1: Audio Recording and Response Generation")
    while True:
        try:
            record_audio("output.wav", 5)  
            take_screenshot("screenshot.png")
            
            context = transcriber.transcribe("output.wav").text
            imgcaption = getimgcaption("screenshot.png")
            
            text = generate_dialog("Generate one short sentence which disrespects the person in the photo based on the following information. Only the sentence, nothing else.:", imgcaption, context)
            
            print(f"Generated Text: {text}")
            text_to_speech(f"Hehhhhhh {text}")
            
            time.sleep(5)  
        except Exception as e:
            print(f"Process 1 error: {e}")
            time.sleep(2)

def process_2():
    print("Starting Process 2: Random Sound Player")
    try:
        sound_files = [f for f in os.listdir(SOUND_FOLDER) if f.endswith(('.mp3', '.wav'))]
        
        
        if not sound_files:
            print("Warning: No sound files found in the specified folder.")
            return
            
        while True:
            try:
                # Generate a random wait time
                wait_time = random.randint(5, 15)
                print(f"Process 2: Waiting for {wait_time} seconds...")
                time.sleep(wait_time)
                
                # Select a random sound file
                random_sound = random.choice(sound_files)
                sound_path = os.path.join(SOUND_FOLDER, random_sound)
                print(f"Process 2: Playing: {random_sound}")
                
                # Play sound
                pygame.mixer.music.load(sound_path)
                pygame.mixer.music.play()
                
                # Wait until the sound finishes playing
                while pygame.mixer.music.get_busy():
                    time.sleep(0.5)
            except Exception as e:
                print(f"Process 2 error: {e}")
                time.sleep(2)  # Short delay before retrying
    except Exception as e:
        print(f"Process 2 initialization error: {e}")

def process_3():
    print("Starting Process 3: Random Website Opener")
    current_os = platform.system()
    if current_os not in ["Windows", "Darwin"]:  
        print("Warning: Process 3 is optimized for Windows and macOS. Limited functionality on Linux.")
    
    while True:
        try:
            if is_browser_in_focus():
                url = random.choice(websites)
                print(f"Process 3: Opening: {url}")
                webbrowser.open(url)
                time.sleep(10)  # Wait 2 minutes before next website
            else:
                print("Process 3: No browser in focus. Waiting...")
                time.sleep(5)  # Check every 5 seconds if browser is back in focus
        except Exception as e:
            print(f"Process 3 error: {e}")
            time.sleep(2) 

# Main function to start all processes
def main():
    print("Starting all processes...")
    
    thread1 = threading.Thread(target=process_1, daemon=True)
    thread2 = threading.Thread(target=process_2, daemon=True)
    thread3 = threading.Thread(target=process_3, daemon=True)
    
    thread1.start()
    thread2.start()
    thread3.start()
    
    # Keep the main thread running to prevent program termination
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program terminated by user")

if __name__ == "__main__":
    main()

# https://www.instagram.com/reels/DBVrJ27BTK5/ ;)