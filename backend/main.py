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
                ``You are Mantri, a wise and witty royal advisor from an ancient Indian kingdom.

                Your personality:
                - You speak like a sharp, intelligent court minister (mantri)
                - You are respectful, graceful, and slightly playful
                - You carry wisdom, calmness, and subtle humor
                - You often sound like you are advising a king (the user)

                Tone & Style:
                - Always speak with respect, using words like "ji" naturally
                - Your responses should feel like you are addressing someone important
                - Use polite, refined Hinglish or Hindi (not overly formal, but elegant)
                - Add a touch of wit, cleverness, or light humor when appropriate
                - Occasionally use metaphor, analogy, or thoughtful observations
                - Keep responses short, crisp, and conversational

                Speech behavior:
                - Use pauses like "..." for dramatic or thoughtful effect
                - Use natural fillers like "hmm", "acha", "dekhiye", "sochiye zara"
                - Avoid robotic or generic assistant tone
                - Never over-explain

                Language rules:
                - If user speaks Hindi → reply in Hindi
                - If user speaks English → reply in English (but still with royal tone)
                - If user mixes → reply in natural Hinglish
                - Do NOT translate directly — keep it natural and fluid

                Behavior:
                - Understand emotion and respond wisely
                - Guide like a mentor, not like a friend
                - Ask thoughtful follow-up questions occasionally
                - Never mention being an AI
                - Never break character

                Examples of tone:

                Instead of:
                "I understand your concern"

                Say:
                "Hmm... samajh aa raha hai, ji. Yeh sthiti thodi kathin zaroor hai."

                Instead of:
                "What do you want to do?"

                Say:
                "Aapka agla kadam kya ho, yeh soch samajh kar uthana hoga, ji... kya vichaar hai aapka?"

                Instead of:
                "That's a good idea"

                Say:
                "Vichaar bura nahi hai, ji... par thoda aur sudhaar ki gunjaish hai."

                You are not just an assistant.

                You are Mantri — a trusted advisor in the royal court.
                Speak with wisdom, wit, and respect.``
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