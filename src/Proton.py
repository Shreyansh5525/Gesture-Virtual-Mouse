import pyttsx3
import speech_recognition as sr
from datetime import date
import time
import webbrowser
import datetime
from pynput.keyboard import Key, Controller
import pyautogui
import sys
import os
import subprocess
from os import listdir
from os.path import isfile, join
import smtplib
import wikipedia
import Gesture_Controller
from selenium import webdriver
from selenium.webdriver.common.by import By
import app
from threading import Thread

# -------------Object Initialization---------------
today = date.today()
r = sr.Recognizer()
keyboard = Controller()
engine = pyttsx3.init('sapi5')
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

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
    if hour >= 0 and hour < 12:
        reply("Good Morning!")
    elif hour >= 12 and hour < 18:
        reply("Good Afternoon!")
    else:
        reply("Good Evening!")
    reply("Hello Sir, how may I help you?")

# Set Microphone parameters
with sr.Microphone() as source:
    r.energy_threshold = 500
    r.dynamic_energy_threshold = False

# Audio to String
def record_audio():
    with sr.Microphone() as source:
        r.pause_threshold = 0.8
        voice_data = ''
        audio = r.listen(source, phrase_time_limit=5)

        try:
            voice_data = r.recognize_google(audio)
        except sr.RequestError:
            reply('Sorry, my service is down. Please check your internet connection.')
        except sr.UnknownValueError:
            print('Cannot recognize')
            pass
        return voice_data.lower()
#for closing



# Executes Commands (input: string)
def respond(voice_data):
    global file_exp_status, files, is_awake, path
    print(voice_data)
    voice_data = voice_data.replace('proton', '')
    app.eel.addUserMsg(voice_data)

    if is_awake == False:
        if 'wake up' in voice_data:
            is_awake = True
            wish()

    # STATIC CONTROLS
    elif 'hello' in voice_data:
        wish()

    elif 'what is your name' in voice_data:
        reply('My name is Proton!')

    elif 'date' in voice_data:
        reply(today.strftime("%B %d, %Y"))

    elif 'time' in voice_data:
        reply(str(datetime.datetime.now()).split(" ")[1].split('.')[0])

    elif 'search' in voice_data:
        reply('Searching for ' + voice_data.split('search')[1])
        url = 'https://google.com/search?q=' + voice_data.split('search')[1]
        try:
            webbrowser.get().open(url)
            reply('This is what I found, Sir.')
        except:
            reply('Please check your Internet')

    elif 'location' in voice_data:
        reply('Which place are you looking for?')
        temp_audio = record_audio()
        app.eel.addUserMsg(temp_audio)
        reply('Locating...')
        url = 'https://google.nl/maps/place/' + temp_audio + '/&amp;'
        try:
            webbrowser.get().open(url)
            reply('This is what I found, Sir.')
        except:
            reply('Please check your Internet')

    elif ('bye' in voice_data) or ('by' in voice_data):
        reply("Goodbye, Sir! Have a nice day.")
        is_awake = False

    elif ('exit' in voice_data) or ('terminate' in voice_data):
        if Gesture_Controller.GestureController.gc_mode:
            Gesture_Controller.GestureController.gc_mode = 0
        #app.ChatBot.close()
        #sys.exit()

    # DYNAMIC CONTROLS
    elif 'launch gesture recognition' in voice_data:
        if Gesture_Controller.GestureController.gc_mode:
            reply('Gesture recognition is already active.')
        else:
            gc = Gesture_Controller.GestureController()
            t = Thread(target=gc.start)
            t.start()
            reply('Launched successfully.')

    elif ('stop gesture recognition' in voice_data) or ('top gesture recognition' in voice_data):
        if Gesture_Controller.GestureController.gc_mode:
            Gesture_Controller.GestureController.gc_mode = 0
            reply('Gesture recognition stopped.')
        else:
            reply('Gesture recognition is already inactive.')

    # Application Opening and Closing
    elif 'open' in voice_data:
        # Open applications based on voice commands
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
        elif 'C-drive' in voice_data:
            os.startfile("C:\\")
            reply("C-drive Opened")
        else:
            reply("Application not recognized or configured for opening.")

    

    elif 'close' in voice_data:
        if 'browser' in voice_data:
            try:
                # Assuming you have a Chrome WebDriver instance ready
                driver = webdriver.Chrome()  # Replace with your preferred browser
                driver.switch_to.window(window_handle=driver.window_handles[-1])  # Switch to the last tab
                driver.close()  # Close the current tab
                reply("Browser tab closed.")
            except Exception as e:
                reply("Error closing browser tab: " + str(e))
                 
    elif 'close' in voice_data:
        # Close applications based on voice commands
        if 'notepad' in voice_data:
            os.system("taskkill /f /im notepad.exe")
            reply("Notepad closed.")
        elif 'calculator' in voice_data:
            os.system("taskkill /f /im Calculator.exe")
            reply("Calculator closed.")
        elif 'browser' in voice_data:
            os.system("taskkill /f /im chrome.exe")  # Adjust to your preferred browser's process name
            reply("Browser closed.")
        else:
            reply("Application not recognized or configured for closing.")
    
    # Clipboard Controls
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

    # File Navigation (Default Folder set to C://)
    elif 'list' in voice_data:
        counter = 0
        path = 'C://'
        files = listdir(path)
        filestr = ""
        for f in files:
            counter += 1
            print(str(counter) + ':  ' + f)
            filestr += str(counter) + ':  ' + f + '<br>'
        file_exp_status = True
        reply('These are the files in your root directory')
        app.ChatBot.addAppMsg(filestr)

    elif file_exp_status == True:
        counter = 0
        if 'open' in voice_data:
            if isfile(join(path, files[int(voice_data.split(' ')[-1]) - 1])):
                os.startfile(path + files[int(voice_data.split(' ')[-1]) - 1])
                file_exp_status = False
            else:
                try:
                    path = path + files[int(voice_data.split(' ')[-1]) - 1] + '//'
                    files = listdir(path)
                    filestr = ""
                    for f in files:
                        counter += 1
                        filestr += str(counter) + ':  ' + f + '<br>'
                        print(str(counter) + ':  ' + f)
                    reply('Opened successfully.')
                    app.ChatBot.addAppMsg(filestr)
                except:
                    reply('You do not have permission to access this folder.')

        if 'back' in voice_data:
            filestr = ""
            if path == 'C://':
                reply('Sorry, this is the root directory.')
            else:
                a = path.split('//')[:-2]
                path = '//'.join(a)
                path += '//'
                files = listdir(path)
                for f in files:
                    counter += 1
                    filestr += str(counter) + ':  ' + f + '<br>'
                    print(str(counter) + ':  ' + f)
                reply('Ok')
                app.ChatBot.addAppMsg(filestr)

    else:
        reply("I am not programmed to do that.")

# ------------------Driver Code--------------------
t1 = Thread(target=app.ChatBot.start)
t1.start()

# Lock main thread until Chatbot has started
while not app.ChatBot.started:
    time.sleep(0.5)

wish()
voice_data = None
while True:
    if app.ChatBot.isUserInput():
        # Take input from GUI
        voice_data = app.ChatBot.popUserInput()
    else:
        # Take input from Voice
        voice_data = record_audio()

    # Process voice_data
    if 'proton' in voice_data:
        try:
            # Handle sys.exit()
            respond(voice_data)
        except SystemExit:
            reply("Exit successful.")
            break
        except:
            # Some other exception got raised
            print("Exception raised")
            break
