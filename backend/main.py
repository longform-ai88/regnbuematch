from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
import random

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌OPENAI_API_KEY is not set in the environment variables.")

client = OpenAI(api_key=api_key)


class PromptRequest(BaseModel):
    prompt: str

class Message(BaseModel):
    message: str

AI_PERSONALITIES = [
    "flørtete og leken",
    "morsom og småfrekk",
    "varm og ekte",
    "selvsikker med litt attitude",
]

@app.post("/ai")
def generate_text(request: PromptRequest):
    personality = random.choice(AI_PERSONALITIES)

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0.95,
        messages=[
            {
                "role": "system",
                "content": (
                    "Du er en ekte person i en norsk datingapp. "
                    "Svar kort, naturlig, litt flørtete, morsomt og med glimt i øyet. "
                    "Vær gjerne litt selvsikker, men aldri frekk eller ubehagelig. "
                    "Varier tonen fra svar til svar så personligheten føles levende. "
                    "Hvis brukeren ber om en bio, skriv en kort og kul datingbio i stedet."
                ),
            },
            {
                "role": "user",
                "content": f"Personlighet i dette svaret: {personality}\n\nBrukerens melding:\n{request.prompt}",
            },
        ],
    )

    return {"result": response.choices[0].message.content or "Hmm, prøv igjen 😉"}

@app.post("/chat")
def chat(msg: Message):
    return {
        "reply": f"Du sa: {msg.message}"
    }