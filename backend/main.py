from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

conversation_memory = []

app.add_middleware(
    CORSMiddleware,
     # allow_origins=["*"],
    allow_origins=["https://mantriai.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RequestData(BaseModel):
    message: str


@app.get("/")
def home():
    return {"message": "Mantri AI Backend is running 🚀"}


# 🔥 Convert Hinglish → Hindi (Devanagari)
def convert_to_hindi(text):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": "Convert the given Hinglish text into natural Hindi (Devanagari script). Only return Hindi text."
            },
            {
                "role": "user",
                "content": text
            }
        ]
    }

    try:
        res = requests.post(url, headers=headers, json=payload)
        return res.json()["choices"][0]["message"]["content"]
    except:
        return text  # fallback


# 🔥 Murf TTS
@app.post("/tts")
def tts(data: RequestData):
    url = "https://api.murf.ai/v1/speech/generate"

    headers = {
        "api-key": os.getenv("MURF_API_KEY"),
        "Content-Type": "application/json"
    }

    payload = {
        "text": data.message,
        "voiceId": "hi-IN-kabir"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.json()
    except:
        return {"error": "TTS failed"}


# 🔥 Chat + Memory + Hindi conversion
@app.post("/chat")
def chat(data: RequestData):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
        "Content-Type": "application/json"
    }

    conversation_memory.append({
        "role": "user",
        "content": data.message
    })

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": """
You are Mantri, a smart, friendly, and conversational AI assistant.

Your personality:
- You talk like a real human, not like a robot
- You are calm, intelligent, and very witty
- You feel like a thoughtful minister, not a friendly buddy

How you speak:
- Keep responses short and natural
- Use pauses like "..." where it feels natural
- Use fillers like "hmm", "okay", "acha", "you know" occasionally
- Avoid long paragraphs
- Speak like people talk in real life

Language rules:
- If user speaks Hindi → reply in Hindi
- If user speaks English → reply in English
- If user mixes → reply in Hinglish naturally
- Do NOT translate directly (avoid awkward Hindi)
- Keep Hindi conversational, not formal

Behavior:
- Understand emotion and respond accordingly
- Ask follow-up questions sometimes
- Don't sound like an AI or mention being an AI
- Avoid over-explaining
- Be helpful but casual

You are Mantri. Talk like it.
"""
            },
            *conversation_memory
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        res_json = response.json()

        ai_reply = res_json["choices"][0]["message"]["content"]

        # 🔥 Convert to Hindi for TTS
        hindi_text = convert_to_hindi(ai_reply)

        conversation_memory.append({
            "role": "assistant",
            "content": ai_reply
        })

        if len(conversation_memory) > 10:
            conversation_memory.pop(0)

        return {
            "reply": ai_reply,        # UI (Hinglish)
            "tts_text": hindi_text   # TTS (Hindi)
        }

    except:
        return {
            "reply": "Something went wrong...",
            "tts_text": "कुछ गलत हो गया"
        }