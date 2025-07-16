import speech_recognition as sr
import pyttsx3
import datetime
import requests
import json
import webbrowser
import time
import threading

NEWS_API_KEY = 'API_KEY'
WEATHER_API_KEY = 'WEATHER_API_KEY'
WEATHER_CITY = 'Mangalpalle'

engine = pyttsx3.init()
voices = engine.getProperty('voices')
try:
    engine.setProperty('voice', voices[1].id)
except IndexError:
    pass

def speak(audio):
    print(f"Assistant: {audio}")
    engine.say(audio)
    engine.runAndWait()

def listen_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        r.energy_threshold = 300
        audio = r.listen(source)

    try:
        print("Recognizing...")
        command = r.recognize_google(audio, language='en-in').lower()
        print(f"You: {command}")
        return command
    except sr.UnknownValueError:
        print("Sorry, I could not understand your audio.")
        return ""
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return ""

def greet_user():
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak("Good Morning!")
    elif 12 <= hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")
    speak("I am your personal assistant. How can I help you today?")

def get_weather(city):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={city}&appid={WEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(complete_url)
        data = response.json()

        if data["cod"] != "404":
            main = data["main"]
            weather_description = data["weather"][0]["description"]
            temperature = main["temp"]
            humidity = main["humidity"]
            speak(f"The weather in {city} is {weather_description}.")
            speak(f"The temperature is {temperature:.1f} degrees Celsius with {humidity} percent humidity.")
        else:
            speak(f"Sorry, I couldn't find weather information for {city}.")
    except requests.exceptions.ConnectionError:
        speak("I'm having trouble connecting to the weather service. Please check your internet connection.")
    except Exception as e:
        speak(f"An error occurred while fetching weather data: {e}")

def get_news():
    url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(url)
        news_data = response.json()
        if news_data['status'] == 'ok' and news_data['articles']:
            speak("Here are the top headlines:")
            for i, article in enumerate(news_data['articles'][:5]):
                title = article['title']
                speak(f"News number {i+1}: {title}.")
                time.sleep(1)
            speak("You can find more news on your browser.")
        else:
            speak("Sorry, I couldn't fetch the news at the moment.")
    except requests.exceptions.ConnectionError:
        speak("I'm having trouble connecting to the news service. Please check your internet connection.")
    except Exception as e:
        speak(f"An error occurred while fetching news: {e}")

def set_reminder(remind_time_str, task):
    try:
        remind_hour, remind_minute = map(int, remind_time_str.split(':'))
        
        now = datetime.datetime.now()
        remind_time = now.replace(hour=remind_hour, minute=remind_minute, second=0, microsecond=0)

        if remind_time < now:
            remind_time += datetime.timedelta(days=1)

        time_difference = (remind_time - now).total_seconds()

        if time_difference > 0:
            speak(f"Okay, I will remind you to {task} at {remind_time.strftime('%I:%M %p')}.")
            threading.Timer(time_difference, lambda: speak(f"Reminder: It's time to {task}!")).start()
        else:
            speak("I cannot set a reminder for a time that has already passed today. Please specify a future time.")
    except ValueError:
        speak("I didn't understand the time format. Please try saying it like 'set a reminder for 3:30 PM to call John'.")
    except Exception as e:
        speak(f"An error occurred while setting the reminder: {e}")


def run_assistant():
    greet_user()
    while True:
        command = listen_command()

        if "hello" in command or "hi" in command:
            speak("Hello there! How can I assist you?")
        elif "time" in command:
            str_time = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"The current time is {str_time}")
        elif "date" in command:
            str_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
            speak(f"Today is {str_date}")
        elif "weather" in command:
            speak(f"Checking weather for {WEATHER_CITY}.")
            get_weather(WEATHER_CITY)
        elif "news" in command:
            get_news()
        elif "set a reminder" in command:
            speak("What should I remind you about?")
            task = listen_command()
            if task:
                speak("And for what time? Please say it like '3:30 PM'.")
                time_str = listen_command()
                if "am" in time_str:
                    time_str = time_str.replace("am", "").strip()
                elif "pm" in time_str:
                    parts = time_str.replace("pm", "").strip().split(':')
                    hour = int(parts[0])
                    if hour != 12:
                        hour += 12
                    time_str = f"{hour}:{parts[1]}"
                
                set_reminder(time_str, task)
            else:
                speak("I didn't get the task for the reminder.")

        elif "open google" in command:
            speak("Opening Google.")
            webbrowser.open("https://www.google.com")
        elif "open youtube" in command:
            speak("Opening YouTube.")
            webbrowser.open("https://www.youtube.com")
        elif "exit" in command or "quit" in command or "bye" in command:
            speak("Goodbye! Have a great day.")
            break
        elif not command:
            speak("Could you please repeat that? I didn't catch it.")
        else:
            speak("I'm sorry, I don't know how to do that yet. Can I help with something else?")

if __name__ == "__main__":
    run_assistant()