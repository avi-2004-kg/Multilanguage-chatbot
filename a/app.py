from flask import Flask, render_template, request, jsonify, send_file
from groq import Groq
from deep_translator import GoogleTranslator
from gtts import gTTS
import os

app = Flask(__name__)

# Initialize Groq client (Replace with your actual API key)
API_KEY = "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"
client = Groq(api_key=API_KEY)

def translate_text(text, target_language):
    """Translates text to the specified target language."""
    try:
        return GoogleTranslator(source="auto", target=target_language).translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return the original text if translation fails

def text_to_speech(text, language):
    """Converts text to speech and saves it as an audio file."""
    try:
        tts = gTTS(text=text, lang=language)
        audio_file = "response.mp3"
        tts.save(audio_file)
        return audio_file
    except Exception as e:
        print(f"TTS error: {e}")
        return None

@app.route("/")
def home():
    return render_template("s2.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message")  # Get user's message
    target_language = data.get("language", "en")  # Get target language (default: English)

    try:
        # Translate user input to English before sending it to the chatbot
        user_message_en = translate_text(user_message, "en")

        # Use Groq API to get a response from the chatbot
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": user_message_en}],
            model="llama-3.3-70b-versatile"  # Replace with the correct Groq model
        )

        bot_response_en = response.choices[0].message.content  # Extract chatbot's response

        # Translate bot response back to the selected language
        bot_response_translated = translate_text(bot_response_en, target_language)

        # Convert the translated response to speech
        audio_file = text_to_speech(bot_response_translated, target_language)
        
        return jsonify({"response": bot_response_translated, "audio": "/audio" if audio_file else None})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"response": "Sorry, there was an error. Try again later!", "audio": None})

@app.route("/audio")
def get_audio():
    return send_file("response.mp3", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
