# === Install Required Packages (uncomment below if running in Colab or Jupyter) ===
# !pip install gradio google-generativeai gtts pydub SpeechRecognition

import os
import gradio as gr
import google.generativeai as genai
from gtts import gTTS
from pydub import AudioSegment
import speech_recognition as sr

# === Gemini API Key ===
GEMINI_API_KEY = "your-gemini-api-key-here"  # 🔐 Replace with your actual Gemini API Key

try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-pro")
except Exception as e:
    raise RuntimeError(f"Failed to initialize Gemini model: {e}")

# === Text-to-Speech ===
def text_to_speech(text, filename="output.mp3"):
    try:
        if not text.strip():
            raise ValueError("Empty text for TTS.")
        tts = gTTS(text=text, lang='en')
        tts.save(filename)
        return filename
    except Exception as e:
        print(f"TTS Error: {e}")
        return None

# === Mood Support Chatbot ===
def mood_support_bot(text_input=None, audio_input=None):
    try:
        user_input = ""
        if audio_input:
            audio = AudioSegment.from_file(audio_input)
            audio.export("temp.wav", format="wav")
            recognizer = sr.Recognizer()
            with sr.AudioFile("temp.wav") as source:
                audio_data = recognizer.record(source)
                user_input = recognizer.recognize_google(audio_data)
        elif text_input:
            user_input = text_input.strip()
        if not user_input:
            return "Please describe how you feel.", None
        prompt = f"You are a kind mental health chatbot. The user says: '{user_input}'. Detect mood and give comforting, emotional support."
        response = model.generate_content(prompt)
        audio_path = text_to_speech(response.text, "mood_response.mp3")
        return response.text, audio_path
    except Exception as e:
        print(f"Mood Bot Error: {e}")
        return "Sorry, I couldn't understand your mood.", None

# === Medical Suggestion Chatbot ===
def medical_suggestion_bot(text_input=None, audio_input=None):
    try:
        user_input = ""
        if audio_input:
            audio = AudioSegment.from_file(audio_input)
            audio.export("temp.wav", format="wav")
            recognizer = sr.Recognizer()
            with sr.AudioFile("temp.wav") as source:
                audio_data = recognizer.record(source)
                user_input = recognizer.recognize_google(audio_data)
        elif text_input:
            user_input = text_input.strip()
        if not user_input:
            return "Please describe your health issue.", None
        prompt = f"You are a helpful mental health assistant. The user says: '{user_input}'. Suggest general mental health advice or treatment options, but avoid making diagnoses."
        response = model.generate_content(prompt)
        audio_path = text_to_speech(response.text, "medical_response.mp3")
        return response.text, audio_path
    except Exception as e:
        print(f"Medical Bot Error: {e}")
        return "Sorry, I couldn't provide advice at the moment.", None

# === Gradio Interfaces ===
mood_interface = gr.Interface(
    fn=mood_support_bot,
    inputs=[
        gr.Textbox(label="Type how you're feeling"),
        gr.Audio(source="microphone", type="filepath", label="Or speak your mood")
    ],
    outputs=[
        gr.Textbox(label="Chatbot Response"),
        gr.Audio(label="Voice Output")
    ],
    title="🧠 Mood Support Chatbot",
    description="Talk about your emotions and receive support."
)

medical_interface = gr.Interface(
    fn=medical_suggestion_bot,
    inputs=[
        gr.Textbox(label="Describe your issue"),
        gr.Audio(source="microphone", type="filepath", label="Or speak your issue")
    ],
    outputs=[
        gr.Textbox(label="Advice or Suggestion"),
        gr.Audio(label="Voice Output")
    ],
    title="🩺 Medical Suggestion Chatbot",
    description="Receive general mental health guidance and treatment ideas."
)

# === Launch Gradio App ===
try:
    app = gr.TabbedInterface(
        interface_list=[mood_interface, medical_interface],
        tab_names=["Mood Support", "Medical Suggestion"]
    )
    app.launch()
except Exception as e:
    print(f"Failed to launch app: {e}")
