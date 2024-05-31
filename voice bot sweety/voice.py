import streamlit as st # type: ignore
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from groq import Groq
from gtts import gTTS
import os

def main():
    st.title("I am sweety your assistant")
    st.write("Please click the button below to start recording")

    stt_button = Button(label="Speak", width=100)
    st.bokeh_chart(stt_button)

    stt_button.js_on_event("button_click", CustomJS(code="""
        var recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.onresult = function (e) {
            var value = "";
            for (var i = e.resultIndex; i < e.results.length; ++i) {
                if (e.results[i].isFinal) {
                    value += e.results[i][0].transcript;
                }
            }
            if (value != "") {
                document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
            }
        }
        recognition.start();
    """))

    result = streamlit_bokeh_events(
        stt_button,
        events="GET_TEXT",
        key="listen",
        refresh_on_update=False,
        override_height=75,
        debounce_time=0
    )

    if result:
        if "GET_TEXT" in result:
            user_query = result.get("GET_TEXT")
            st.write("User Query: " + user_query)

            # Initialize Groq client with API key
            client = Groq(api_key='')
            completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {
                        "role": "user",
                        "content": user_query
                    }
                ],
                temperature=1,
                max_tokens=1024,
                top_p=1,
                stream=True,
                stop=None,
            )

            response = ""
            for chunk in completion:
                response += chunk.choices[0].delta.content or ""

            st.write("Response: " + response)

            # Convert the response to speech and save as audio file
            tts = gTTS(text=response, lang='en')
            audio_path = "response_audio.mp3"
            tts.save(audio_path)

            # Play the audio
            st.audio(audio_path, format="audio/mp3")

if __name__ == "__main__":
    main()
