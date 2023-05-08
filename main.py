import openai
import asyncio
import re
import whisper
import pydub
from pydub import playback
import speech_recognition as sr
from EdgeGPT import Chatbot, ConversationStyle
from gtts import gTTS
import json

# Create a recognizer object and wake word variables
recognizer = sr.Recognizer()
BING_WAKE_WORD = "egg"
language = 'fr'

def get_wake_word(phrase):
    if BING_WAKE_WORD in phrase.lower():
        return BING_WAKE_WORD
    else:
        return None
    
def synthesize_speech(text, output_filename):
    myobj = gTTS(text=text, lang=language, slow=False)
    myobj.save(output_filename)

def play_audio(file):
    sound = pydub.AudioSegment.from_file(file, format="mp3")
    playback.play(sound)

async def main():
    mytext = 'Le programme est lancé!'
    myobj = gTTS(text=mytext, lang=language, slow=False)
    myobj.save("welcome.mp3")
    play_audio("welcome.mp3")
    while True:

        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            print(f"Waiting for wake words 'hey egg'...")
            while True:
                audio = recognizer.listen(source)
                try:
                    with open("audio.wav", "wb") as f:
                        f.write(audio.get_wav_data())
                    # Use the preloaded tiny_model
                    model = whisper.load_model("tiny")
                    result = model.transcribe("audio.wav")
                    phrase = result["text"]
                    print(f"You said: {phrase}")

                    wake_word = get_wake_word(phrase)
                    if wake_word is not None:
                        break
                    else:
                        print("Not a wake word. Try again.")
                except Exception as e:
                    print("Error transcribing audio: {0}".format(e))
                    continue

            print("Speak a prompt...")
            synthesize_speech('Comment puis-je vous aider?', 'response.mp3')
            play_audio('response.mp3')
            audio = recognizer.listen(source)

            try:
                mytext = 'Laisser moi reflechir...'
                myobj = gTTS(text=mytext, lang=language, slow=False)
                myobj.save("reflect.mp3")
                play_audio("reflect.mp3")
                with open("audio_prompt.wav", "wb") as f:
                    f.write(audio.get_wav_data())
                model = whisper.load_model("base")
                result = model.transcribe("audio_prompt.wav")
                user_input = result["text"]
                print(f"You said: {user_input}")
            except Exception as e:
                print("Error transcribing audio: {0}".format(e))
                continue

            if wake_word == BING_WAKE_WORD:
                with open('./cookies.json', 'r') as f:
                    cookies = json.load(f)
                bot = Chatbot(cookies=cookies)
                response = await bot.ask(prompt=user_input, conversation_style=ConversationStyle.precise)
                for message in response["item"]["messages"]:
                    if message["author"] == "bot":
                        bot_response = message["text"]
                bot_response = re.sub('\[\^\d+\^\]', '', bot_response)
        print("Bot's response:", bot_response)
        synthesize_speech(bot_response, 'response.mp3')
        play_audio('response.mp3')
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
