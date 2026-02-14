import sounddevice as sd
import queue
import json
import pyttsx3
import datetime
import webbrowser
import time
from vosk import Model, KaldiRecognizer

# ---------------- AUDIO QUEUE ----------------
q = queue.Queue(maxsize=10)

# ---------------- LOAD VOSK ----------------
model = Model("vosk-model-small-en-us-0.15")
recognizer = KaldiRecognizer(model, 16000)
recognizer.SetWords(True)

# ---------------- MIC CALLBACK ----------------
def callback(indata, frames, time_info, status):
    if not q.full():
        q.put(bytes(indata))

# ---------------- SPEAK FUNCTION ----------------
def speak(text):
    print(f"Assistant: {text}")   # Display assistant message

    engine = pyttsx3.init('sapi5')   # Windows voice engine
    engine.setProperty("rate", 160)

    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)  # Change to voices[1].id for female voice

    engine.say(text)
    engine.runAndWait()
    engine.stop()

# ---------------- CLEAR QUEUE ----------------
def clear_queue():
    while not q.empty():
        q.get()

# ---------------- LISTEN FUNCTION ----------------
def listen(timeout=20):
    clear_queue()
    recognizer.Reset()
    start_time = time.time()

    while True:
        if time.time() - start_time > timeout:
            return ""

        data = q.get()

        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").strip()
            if text:
                return text.lower()
        else:
            partial = json.loads(recognizer.PartialResult()).get("partial", "")
            if len(partial.split()) >= 2:
                return partial.lower()

# ---------------- GREET USER ----------------
def wish_user():
    hour = datetime.datetime.now().hour

    if 5 <= hour < 12:
        speak("Good morning")
    elif 12 <= hour < 17:
        speak("Good afternoon")
    elif 17 <= hour < 21:
        speak("Good evening")
    else:
        speak("Good night")

# ---------------- START MIC STREAM ----------------
with sd.RawInputStream(
    samplerate=16000,
    blocksize=8000,
    dtype="int16",
    channels=1,
    callback=callback
):
    wish_user()
    speak("I am your voice assistant. How can I help you?")

    while True:
        print("Listening...")
        command = listen()

        if not command:
            continue

        print("You said:", command)

        if "hello" in command:
            speak("Hello! Nice to meet you")

        elif "time" in command:
            now = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"The time is {now}")

        elif "date" in command:
            today = datetime.datetime.now().strftime("%d %B %Y")
            speak(f"Today's date is {today}")

        elif "day" in command:
            day = datetime.datetime.now().strftime("%A")
            speak(f"Today is {day}")

        elif "google" in command:
            speak("Opening Google")
            webbrowser.open("https://www.google.com")

        elif "you tube" in command:
            speak("Opening YouTube")
            webbrowser.open("https://www.youtube.com")

        elif "search" in command:
            speak("What should I search?")
            query = listen()

            if query:
                speak(f"Searching for {query}")
                webbrowser.open(f"https://www.google.com/search?q={query}")
            else:
                speak("I did not hear the search query")

        elif "exit" in command or "quit" in command:
            speak("Goodbye!")
            break

        else:
            speak("Sorry, I did not understand that please repeat it again")

        time.sleep(0.3)
