import os
import uuid
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from chatbot.agent import root_agent  # tumhara existing agent

load_dotenv()

APP_NAME = "chatbot_adk"

# Yeh dono cheezein sirf ek baar banti hain, server start hote waqt.
# Har request pe naya nahi banate — yeh important hai performance ke liye.
session_service = InMemorySessionService()
runner = Runner(
    app_name=APP_NAME,
    agent=root_agent,
    session_service=session_service,
)

app = FastAPI(title="ChatbotADK")

# Widget kisi bhi client website se call karega, isliye CORS allow karna zaroori hai
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # production me specific domains list karna behtar hai
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None  # agar frontend pehle se session_id bhej raha ho


class ChatResponse(BaseModel):
    reply: str
    session_id: str


@app.post("/chat/{client_id}", response_model=ChatResponse)
async def chat(client_id: str, request: ChatRequest):
    session_id = request.session_id or f"session_{uuid.uuid4().hex[:8]}"
    user_id = f"user_{session_id}"

    # Session pehle se maujood hai ya nahi check karo
    existing = await session_service.get_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )

    if not existing:
        # Yehi wo jagah hai jahan client_id session state me daala jata hai
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
            state={"client_id": client_id},
        )

    # User ka message ADK ke Content format me convert karo
    user_message = types.Content(
        role="user",
        parts=[types.Part(text=request.message)],
    )

    reply_text = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=user_message,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            reply_text = event.content.parts[0].text or ""

    return ChatResponse(reply=reply_text, session_id=session_id)


@app.get("/health")
def health():
    return {"status": "ok"}
