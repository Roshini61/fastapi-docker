import asyncio
import shutil
import subprocess
import aiohttp

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain

from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone,
)


class LanguageModelProcessor:
    def _init_(self):
        self.llm = ChatGroq(temperature=0, model_name="mixtral-8x7b-32768", groq_api_key="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")
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        # Load the system prompt from a file
        with open('system_prompt.txt', 'r') as file:
            system_prompt = file.read().strip()
        
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{text}")
        ])

        self.conversation = LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            memory=self.memory
        )

    async def process_stream(self, text, callback):
        self.memory.chat_memory.add_user_message(text)  # Add user message to memory

        response = self.conversation.invoke({"text": text})  # No await here
        truncated_response = self.truncate_response(response['text'])
        self.memory.chat_memory.add_ai_message(truncated_response)  # Add AI response to memory
        await callback(truncated_response)

    def truncate_response(self, response, max_words=50):
        words = response.split()
        if len(words) > max_words:
            return ' '.join(words[:max_words]) + '...'
        return response


class TextToSpeech:
    # Set your Deepgram API Key and desired voice model
    DG_API_KEY = "031aaec2175638841f1a30eae58d816ae9e05ac1"
    MODEL_NAME = "aura-helios-en"  # Example model name, change as needed

    @staticmethod 
    def is_installed(lib_name: str) -> bool:
        lib = shutil.which(lib_name)
        return lib is not None

    async def speak_streaming(self, text_stream):
        if not self.is_installed("ffplay"):
            raise ValueError("ffplay not found, necessary to stream audio.")

        DEEPGRAM_URL = f"https://api.deepgram.com/v1/speak?model={self.MODEL_NAME}&performance=some&encoding=linear16&sample_rate=24000"
        headers = {
            "Authorization": f"Token {self.DG_API_KEY}",
            "Content-Type": "application/json"
        }

        player_command = ["ffplay", "-autoexit", "-", "-nodisp"]
        player_process = subprocess.Popen(
            player_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        async with aiohttp.ClientSession() as session:
            for text in text_stream:
                payload = {"text": text}
                async with session.post(DEEPGRAM_URL, headers=headers, json=payload) as r:
                    async for chunk in r.content.iter_chunked(1024):
                        if chunk:
                            player_process.stdin.write(chunk)
                            player_process.stdin.flush()

        if player_process.stdin:
            player_process.stdin.close()
        player_process.wait()


class TranscriptCollector:
    def _init_(self):
        self.reset()

    def reset(self):
        self.transcript_parts = []

    def add_part(self, part):
        self.transcript_parts.append(part)

    def get_full_transcript(self):
        return ' '.join(self.transcript_parts)


transcript_collector = TranscriptCollector()

async def get_transcript(callback):
    transcription_complete = asyncio.Event()  # Event to signal transcription completion

    try:
        # example of setting up a client config. logging values: WARNING, VERBOSE, DEBUG, SPAM
        config = DeepgramClientOptions(options={"keepalive": "true"})

        deepgram: DeepgramClient = DeepgramClient("031aaec2175638841f1a30eae58d816ae9e05ac1", config)


        dg_connection = deepgram.listen.asynclive.v("1")
        print ("Listening...")

        async def on_message(self, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript
            
            if not result.speech_final:
                transcript_collector.add_part(sentence)
            else:
                # This is the final part of the current sentence
                transcript_collector.add_part(sentence)
                full_sentence = transcript_collector.get_full_transcript()
                # Check if the full_sentence is not empty before printing
                if len(full_sentence.strip()) > 0:
                    full_sentence = full_sentence.strip()
                    print(f"Human: {full_sentence}")
                    callback(full_sentence)  # Call the callback with the full_sentence
                    transcript_collector.reset()
                    transcription_complete.set()  # Signal to stop transcription and exit

        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)

        options = LiveOptions(
            model="nova-2",
            punctuate=True,
            language="en-US",
            encoding="linear16",
            channels=1,
            sample_rate=16000,
            endpointing=300,
            smart_format=True,
        )

        await dg_connection.start(options)

        # Open a microphone stream on the default input device
        microphone = Microphone(dg_connection.send)
        microphone.start()

        await transcription_complete.wait()  # Wait for the transcription to complete instead of looping indefinitely

        # Wait for the microphone to close
        microphone.finish()

        # Indicate that we've finished
        await dg_connection.finish()

    except Exception as e:
        print(f"Could not open socket: {e}")
        return


class ConversationManager:
    def _init_(self):
        self.transcription_response = ""
        self.llm = LanguageModelProcessor()
        self.tts = TextToSpeech()

    async def main(self):
        def handle_full_sentence(full_sentence):
            self.transcription_response = full_sentence

        while True:
            await get_transcript(handle_full_sentence)
            
            if "goodbye" in self.transcription_response.lower():
                break
            
            async def callback_partial_response(partial_response):
                await self.tts.speak_streaming([partial_response])

            await self.llm.process_stream(self.transcription_response, callback_partial_response)
            self.transcription_response = ""


if _name_ == "_main_":
    manager = ConversationManager()
    asyncio.run(manager.main())