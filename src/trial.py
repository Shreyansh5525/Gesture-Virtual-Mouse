import pyttsx3
import speech_recognition as sr
from datetime import date
import datetime
from pynput.keyboard import Key, Controller
import webbrowser
import os
import pyautogui
import Gesture_Controller
import app
from threading import Thread

# -------------Object Initialization---------------
today = date.today()
r = sr.Recognizer()
keyboard = Controller()
engine = pyttsx3.init('sapi5')
engine.setProperty('voice', engine.getProperty('voices')[1].id)

# ----------------Variables------------------------
file_exp_status = False
files = []
path = ''
is_awake = True  # Bot status

# ------------------Functions----------------------
def reply(audio):
    app.ChatBot.addAppMsg(audio)
    print(audio)
    engine.say(audio)
    engine.runAndWait()

def wish():
    hour = int(datetime.datetime.now().hour)
    if hour < 12:
        reply("Good Morning!")
    elif hour < 18:
        reply("Good Afternoon!")
    else:
        reply("Good Evening!")
    reply("Hello Sir, how may I help you?")

# Set up microphone parameters once
r.energy_threshold = 100
r.dynamic_energy_threshold = False

# Audio to String
def record_audio():
    with sr.Microphone() as source:
        r.pause_threshold = 0.5 # Reduce pause threshold for quicker response
        audio = r.listen(source, phrase_time_limit=5)
        try:
            voice_data = r.recognize_google(audio)
            return voice_data.lower()
        except sr.RequestError:
            reply('Sorry, my service is down. Please check your internet connection.')
        except sr.UnknownValueError:
            print('Cannot recognize')
    return ''

# Executes Commands (input: string)
def respond(voice_data):
    global file_exp_status, files, is_awake, path
    print(voice_data)
    voice_data = voice_data.replace('proton', '')
    app.eel.addUserMsg(voice_data)

    if not is_awake and 'wake up' in voice_data:
        is_awake = True
        wish()

    elif is_awake:
        if 'hello' in voice_data:
            wish()
        elif 'what is your name' in voice_data:
            reply('My name is Proton!')
        elif 'date' in voice_data:
            reply(today.strftime("%B %d, %Y"))
        elif 'time' in voice_data:
            reply(str(datetime.datetime.now()).split(" ")[1].split('.')[0])
        elif 'search' in voice_data:
            query = voice_data.split('search')[1]
            reply('Searching for ' + query)
            url = f'https://google.com/search?q={query}'
            try:
                webbrowser.open(url)
                reply('This is what I found, Sir.')
            except:
                reply('Please check your Internet')
        elif 'location' in voice_data:
            reply('Which place are you looking for?')
            location = record_audio()
            reply('Locating...')
            url = f'https://google.nl/maps/place/{location}/&amp;'
            try:
                webbrowser.open(url)
                reply('This is what I found, Sir.')
            except:
                reply('Please check your Internet')
        elif 'bye' in voice_data:
            reply("Goodbye, Sir! Have a nice day.")
            is_awake = False
            exit()
        elif 'exit' in voice_data:
            if Gesture_Controller.GestureController.gc_mode:
                Gesture_Controller.GestureController.gc_mode = 0
            reply("Exit successful.")
            #exit()
        elif 'launch gesture recognition' in voice_data:
            if Gesture_Controller.GestureController.gc_mode:
                reply('Gesture recognition is already active.')
            else:
                gc = Gesture_Controller.GestureController()
                Thread(target=gc.start).start()
                reply('Launched successfully.')
        elif 'stop gesture recognition' in voice_data:
            Gesture_Controller.GestureController.gc_mode = 0
            reply('Gesture recognition stopped.')
        elif 'open' in voice_data:
            if 'notepad' in voice_data:
                os.startfile("notepad.exe")
                reply("Notepad opened.")
            elif 'calculator' in voice_data:
                os.startfile("calc.exe")
                reply("Calculator opened.")
            elif 'chrome' in voice_data:
                chrome_path = "C:\\Users\\91878\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe"
                os.startfile(chrome_path)
                reply("Chrome opened.")
            elif 'brave' in voice_data:
                brave_path = "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Brave.lnk"
                os.startfile(brave_path)
                reply("Brave opened.")
            else:
                reply("Application not recognized or configured for opening.")
        elif 'close' in voice_data and 'tab' in voice_data:
            pyautogui.hotkey('alt', 'f4')
            reply("Application closed")
        elif 'copy' in voice_data:
            with keyboard.pressed(Key.ctrl):
                keyboard.press('c')
                keyboard.release('c')
            reply('Copied.')
        elif 'paste' in voice_data:
            with keyboard.pressed(Key.ctrl):
                keyboard.press('v')
                keyboard.release('v')
            reply('Pasted.')
        else:
            reply("I am not programmed to do that.")

# ------------------Driver Code--------------------
t1 = Thread(target=app.ChatBot.start)
t1.start()

# Lock main thread until Chatbot has started
while not app.ChatBot.started:
    pass

wish()
while True:
    voice_data = app.ChatBot.popUserInput() if app.ChatBot.isUserInput() else record_audio()
    if 'proton' in voice_data:
        respond(voice_data)
