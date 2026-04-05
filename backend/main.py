from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌OPENAI_API_KEY is not set in the environment variables.")

client = OpenAI(api_key=api_key)


class PromptRequest(BaseModel):
    prompt: str

class Message(BaseModel):
    message: str

@app.post("/ai")
def generate_text(request: PromptRequest):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "user", "content": f"Lag en kort og kul dating bio på norsk:\n{request.prompt}"}
        ]
    )

    return {"result": response.choices[0].message.content}

@app.post("/chat")
def chat(msg: Message):
    return {
        "reply": f"Du sa: {msg.message}"
    }