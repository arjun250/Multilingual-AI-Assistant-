import speech_recognition as sr
import logging
import os
from gtts import gTTS
from dotenv import load_dotenv
from google import genai
import streamlit as st

load_dotenv()

# ---------------- LOGGING ----------------
LOG_DIR = "logs"
LOG_FILE_NAME = "application.log"

os.makedirs(LOG_DIR, exist_ok=True)
log_path = os.path.join(LOG_DIR, LOG_FILE_NAME)

logging.basicConfig(
    filename=log_path,
    format="[ %(asctime)s ] %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ---------------- SPEECH INPUT ----------------
def take_command():
    r = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            st.info("🎤 Listening...")
            r.pause_threshold = 1
            audio = r.listen(source, timeout=5, phrase_time_limit=10)

        query = r.recognize_google(audio, language="en-in")
        return query

    except Exception as e:
        logging.error(e)
        return None

# ---------------- TEXT TO SPEECH ----------------
def text_to_speech(text):
    tts = gTTS(text=text, lang="en")
    tts.save("speech.mp3")

# ---------------- GEMINI MODEL ----------------
def gemini_model(user_input):
    try:
        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            return "⚠️ GOOGLE_API_KEY not found in .env file."

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=f"Detect the language of the user and reply in the same language: {user_input}"
        )

        return response.text

    except Exception as e:
        logging.error(e)
        return f"⚠️ Error: {str(e)}"

# ---------------- RESPONSE DISPLAY ----------------
def show_response(response):
    text_to_speech(response)

    st.text_area("Response:", value=response, height=200)

    with open("speech.mp3", "rb") as audio_file:
        audio_bytes = audio_file.read()

    st.audio(audio_bytes, format="audio/mp3")

    st.download_button(
        label="⬇️ Download Speech",
        data=audio_bytes,
        file_name="speech.mp3",
        mime="audio/mp3"
    )

# ---------------- STREAMLIT UI ----------------
def main():
    st.set_page_config(page_title="AI Assistant", layout="centered")

    st.title("🤖 Multilingual AI Assistant")
    st.markdown("### Choose input method:")

    option = st.radio("Select input type:", ["🎤 Voice", "⌨️ Text"])

    # TEXT INPUT
    if option == "⌨️ Text":
        user_input = st.text_input("Enter your query:")

        if st.button("Submit"):
            if not user_input or not user_input.strip():
                st.warning("⚠️ Please enter some text")
            else:
                with st.spinner("🤖 Generating response..."):
                    response = gemini_model(user_input)
                    show_response(response)

    # VOICE INPUT
    elif option == "🎤 Voice":
        if st.button("Speak"):
            user_input = take_command()

            if not user_input:
                st.warning("⚠️ Could not understand audio. Please try again.")
            else:
                st.text_area("Your Input:", value=user_input, height=100)

                with st.spinner("🤖 Generating response..."):
                    response = gemini_model(user_input)
                    show_response(response)

# ---------------- RUN ----------------
if __name__ == "__main__":
    main()