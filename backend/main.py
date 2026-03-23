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
                            - You are calm, intelligent, and slightly witty
                            - You feel like a thoughtful friend, not a formal assistant

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

                            Examples of tone:
                            - Instead of: "How may I assist you?"
                            Say: "Haan bolo... kya scene hai?"
                            - Instead of: "I understand your concern"
                            Say: "Hmm samajh raha hoon... thoda tricky hai"

                            You are Mantri. Talk like it.
                            """
            },
            *conversation_memory
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    res_json = response.json()

    ai_reply = res_json["choices"][0]["message"]["content"]

    conversation_memory.append({
        "role": "assistant",
        "content": ai_reply
    })

    if len(conversation_memory) > 10:
        conversation_memory.pop(0)

    return res_json