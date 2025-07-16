import speech_recognition as sr
import requests
import json
import os
import time
import uuid
from dotenv import load_dotenv

load_dotenv()

MONSTER_API_KEY = os.getenv("MONSTER_API_KEY")
if not MONSTER_API_KEY:
    raise Exception("Missing MONSTER_API_KEY. Make sure it's in the .env file.")

def transcribe_audio(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as src:
        audio_data = recognizer.record(src)
    try:
        text = recognizer.recognize_google(audio_data, language=None)
        return text
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError as err:
        return f"Request Error: {err}"

def generate_image(prompt):
    url = "https://api.monsterapi.ai/v1/generate/txt2img"
    headers = {
        "Authorization": f"Bearer {MONSTER_API_KEY}",
        "accept": "application/json",
        "content-type": "application/json"
    }

    payload = {
        "prompt": prompt,
        "samples": 1,
        "steps": 40,
        "guidance_scale": 7,
        "safe_filter": True,
        "style": "photographic"
    }

    try:
        res = requests.post(url, headers=headers, json=payload)
        res.raise_for_status()
        resp_data = res.json()

        process_id = resp_data.get("process_id")
        if not process_id:
            return None, "No process ID returned"

        status_url = f"https://api.monsterapi.ai/v1/status/{process_id}"
        for _ in range(30):
            time.sleep(5)
            status_res = requests.get(status_url, headers=headers)
            status_res.raise_for_status()
            status_data = status_res.json()
            if status_data.get("status") == "COMPLETED":
                images = status_data.get("result", {}).get("output", [])
                if images:
                    return images[0], None
                return None, "No image URL found"
            elif status_data.get("status") == "FAILED":
                return None, f"Generation failed: {status_data.get('message', 'No details')}"
        return None, "Timeout while waiting for image"
    except Exception as e:
        return None, str(e)

def download_image(img_url, filename="image_out.png"):
    try:
        resp = requests.get(img_url, stream=True)
        if resp.status_code == 200:
            with open(filename, "wb") as f:
                for chunk in resp.iter_content(1024):
                    f.write(chunk)
            return True, None
        return False, f"HTTP {resp.status_code}"
    except Exception as e:
        return False, str(e)

def speak(msg):
    print(f"Assistant: {msg}")

def main():
    print(">>> Speech-to-Image Tool Started <<<")
    print("Speak something... Press Ctrl+C to quit.")

    recognizer = sr.Recognizer()

    while True:
        try:
            with sr.Microphone() as mic:
                print("\nListening...")
                recognizer.adjust_for_ambient_noise(mic, duration=1)
                audio = recognizer.listen(mic)

            temp_audio = f"temp_{uuid.uuid4().hex[:8]}.wav"
            with open(temp_audio, "wb") as af:
                af.write(audio.get_wav_data())

            print("Transcribing speech...")
            spoken_text = transcribe_audio(temp_audio)
            print(f"You said: {spoken_text}")
            os.remove(temp_audio)

            if "Could not understand" in spoken_text or "Request Error" in spoken_text:
                speak("Sorry, couldn't get that. Try again.")
                continue

            if not spoken_text.strip():
                speak("Didn't catch any meaningful words. Try again.")
                continue

            speak(f"Creating image for: '{spoken_text}'")
            img_url, err = generate_image(spoken_text)

            if img_url:
                filename = f"img_{uuid.uuid4().hex[:6]}.png"
                success, download_err = download_image(img_url, filename)
                if success:
                    speak(f"Image saved as {filename}")
                    print(f"URL: {img_url}")
                else:
                    speak(f"Download failed: {download_err}")
            else:
                speak(f"Generation failed: {err}")

        except KeyboardInterrupt:
            speak("Goodbye!")
            break
        except Exception as ex:
            speak(f"Oops! Something went wrong: {ex}")

if __name__ == "__main__":
    main()