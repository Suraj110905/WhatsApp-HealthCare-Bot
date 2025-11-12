import os
import time
import logging
import requests
import tempfile
from dotenv import load_dotenv
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from langdetect import detect
import backoff
from openai import OpenAI, APIError

# ===== Load configuration =====
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

openai_client = OpenAI(api_key=OPENAI_API_KEY)
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("health_assistant")

# ===== User session tracking =====
user_sessions = {}
SESSION_TIMEOUT = 300  # 5 minutes

# ===== Keywords and mappings =====
EXIT_WORDS = ["bye", "no", "thanks", "thank you", "नहीं", "धन्यवाद", "stop", "exit", "band karo"]

CRITICAL_WORDS = [
    "chest pain", "severe bleeding", "unconscious", "heart attack", "stroke",
    "fainting", "shortness of breath", "vomiting blood", "fracture", "seizure",
    "poison", "snake bite", "burn", "head injury", "coma", "drowning", "electrocution"
]

SPECIALIST_MAP = {
    "chest pain": ["Cardiologist", "Emergency Physician"],
    "heart attack": ["Cardiologist"],
    "breathing difficulty": ["Pulmonologist"],
    "fracture": ["Orthopedic Doctor"],
    "head injury": ["Neurologist", "Emergency Specialist"],
    "burn": ["Plastic Surgeon", "Emergency Physician"],
    "high fever": ["General Physician"],
    "vomiting blood": ["Gastroenterologist"],
    "abdominal pain": ["Gastroenterologist"],
    "unconscious": ["Emergency Physician"]
}

MAP_KEYWORDS = [
    "map", "hospital", "clinic", "doctor near", "nearby doctor", "health center",
    "medical center", "pharmacy near", "ambulance", "nearest clinic", "hospital location",
    "show hospital", "find hospital", "अस्पताल", "डॉक्टर", "क्लिनिक", "स्वास्थ्य केंद्र", "मैप", "नक्शा"
]

EMERGENCY_MESSAGE = {
    "hi": "⚠️ तुरंत मदद लें! कृपया 108 पर कॉल करें या नजदीकी अस्पताल जाएं।",
    "en": "⚠️ This may be an emergency. Please call 108 or visit the nearest hospital.",
    "mr": "⚠️ त्वरित मदत घ्या! 108 वर कॉल करा किंवा जवळच्या रुग्णालयात जा.",
    "bn": "⚠️ এটি একটি জরুরী পরিস্থিতি হতে পারে। দয়া করে 108 এ কল করুন বা নিকটস্থ হাসপাতালে যান।"
}

# ===== Utility functions =====
def detect_language(text):
    try:
        lang = detect(text)
        return lang if lang in EMERGENCY_MESSAGE else "en"
    except Exception:
        return "en"

def generate_maps_link(lang="en"):
    query = {
        "hi": "नजदीकी अस्पताल",
        "mr": "जवळचे रुग्णालय",
        "bn": "নিকটস্থ হাসপাতাল",
        "en": "hospital near me"
    }.get(lang, "hospital near me")
    return f"https://www.google.com/maps/search/?api=1&query={query.replace(' ', '+')}"

def get_user_state(user_id):
    state = user_sessions.get(user_id)
    if state and time.time() - state["last_seen"] <= SESSION_TIMEOUT:
        state["last_seen"] = time.time()
        return state
    return {"lang": None, "msg_count": 0, "last_seen": time.time(), "history": []}

def download_media_as_bytes(media_url: str) -> bytes:
    auth = (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    response = requests.get(media_url.replace(".json", ""), auth=auth)
    response.raise_for_status()
    return response.content

def transcribe_audio(media_url: str) -> str:
    audio_bytes = download_media_as_bytes(media_url)
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp_audio:
        tmp_audio.write(audio_bytes)
        tmp_audio.flush()
        with open(tmp_audio.name, "rb") as audio_file:
            transcript = openai_client.audio.transcriptions.create(model="whisper-1", file=audio_file)
    return transcript.text.strip()

def build_system_prompt(lang: str):
    return (
        f"You are a compassionate, safe AI Health Assistant. Respond only in {lang.upper()}.\n"
        "Provide helpful, safe health guidance. Avoid diagnosis. Suggest professional help for severe symptoms.\n"
        "Keep replies short (3 paragraphs max). Use simple, human tone."
    )

@backoff.on_exception(backoff.expo, (APIError, requests.exceptions.RequestException), max_tries=3)
def ask_openai(user_id: str, message: str, lang: str):
    state = user_sessions[user_id]
    messages = [{"role": "system", "content": build_system_prompt(lang)}]
    messages += state["history"]
    messages.append({"role": "user", "content": message})

    response = openai_client.chat.completions.create(
        model=OPENAI_MODEL, messages=messages, temperature=0.7, max_tokens=400
    )
    reply = response.choices[0].message.content.strip()
    state["history"].append({"role": "assistant", "content": reply})
    return reply

# ===== Main conversation logic =====
def build_conversation_response(user_id, user_text):
    state = get_user_state(user_id)
    state["msg_count"] += 1
    if not state["lang"]:
        state["lang"] = detect_language(user_text)
    lang = state["lang"]
    user_sessions[user_id] = state

    text_lower = user_text.lower().strip()
    final_response = ""

    if any(word in text_lower for word in EXIT_WORDS):
        user_sessions.pop(user_id, None)
        return "Conversation ended. You can message again anytime."

    # Emergency / critical cases
    if any(word in text_lower for word in CRITICAL_WORDS):
        specialists = []
        for symptom, docs in SPECIALIST_MAP.items():
            if symptom in text_lower:
                specialists = docs
                break
        emergency_text = EMERGENCY_MESSAGE.get(lang, EMERGENCY_MESSAGE["en"])
        doctor_info = f"👨‍⚕️ Recommended: {', '.join(specialists)}" if specialists else ""
        map_link = generate_maps_link(lang)
        return f"{emergency_text}\n\n{doctor_info}\n🗺️ [Nearby Hospital]({map_link})"

    # Normal conversation
    reply = ask_openai(user_id, user_text, lang)
    final_response += reply

    # Show map if user asks directly
    if any(keyword in text_lower for keyword in MAP_KEYWORDS):
        map_link = generate_maps_link(lang)
        final_response += f"\n\n🗺️ [Nearby Hospital / Health Center]({map_link})"

    return final_response

# ===== Flask routes =====
@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    from_number = request.form.get("From", "")
    message_body = request.form.get("Body", "")
    media_url = request.form.get("MediaUrl0")
    num_media = int(request.form.get("NumMedia", 0))
    reply_text = ""

    if num_media > 0 and media_url:
        try:
            message_body = transcribe_audio(media_url)
        except Exception as e:
            logger.error(f"Audio transcription failed: {e}")
            message_body = "Sorry, I couldn't process your voice message."

    if not message_body.strip():
        reply_text = "Please type or say your health question."
    else:
        reply_text = build_conversation_response(from_number, message_body)

    resp = MessagingResponse()
    resp.message(reply_text)
    return Response(str(resp), mimetype="application/xml")

@app.route("/", methods=["GET"])
def index():
    return "✅ AI Health Assistant (OpenAI) is running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=os.getenv("FLASK_DEBUG", "0") == "1")
