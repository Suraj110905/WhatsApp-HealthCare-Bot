# 🩺 WhatsApp AI Health Assistant (Powered by OpenAI)

A highly accessible and secure conversational AI assistant for **rural healthcare triage** and first aid advice, delivered through **WhatsApp**.  
This project uses **OpenAI’s GPT and Whisper models** for intelligent reasoning, empathy, and accurate voice transcription, alongside **Twilio** for seamless messaging.

---

## ✅ Key Features

This AI is designed to act as a **safe, non-diagnostic** health assistant.

* 🤒 **Symptom Triage:** Analyzes symptoms and provides immediate, safe first aid and home care advice.
* 🧠 **OpenAI Integration:** Utilizes **OpenAI GPT models** for powerful, context-aware reasoning and memory-based conversation handling.
* 🎙️ **Voice Message Support (ASR):** Uses **OpenAI Whisper** to **transcribe voice notes** into text, ensuring accessibility for all users.
* 🗣 **Multilingual Support:** Auto-detects and converses in **English, Hindi, Marathi, and Bengali**.
* 🚨 **Emergency Handoff:** Instantly recognizes critical keywords (e.g., "chest pain," "saans lene me dikkat") and directs the user to call **108** (Ambulance/Emergency).
* 🏥 **Referral Link:** Provides a **localized Google Maps link** to find the nearest health center or hospital during emergencies.

---

## 🛠 Tools Used

| Tool | Purpose |
| :--- | :--- |
| **Flask** | Lightweight web server to run the Python application. |
| **Twilio** | WhatsApp messaging API to receive and send messages. |
| **Ngrok** | Creates a secure public link to expose your local Flask server to Twilio. |
| **OpenAI API** | The primary engine for **health triage**, **contextual conversation**, and **voice transcription** using GPT and Whisper. |
| **Langdetect** | Python library for automatic language detection. |
| **Google Maps Link** | Provides actionable hospital or clinic search links. |

---

## ⚙️ Setup Guide (Step-by-Step for Beginners)

Follow these steps to get your AI Health Assistant running locally and connected to WhatsApp.

### 1️⃣ Project Setup

1.  **Clone the Code:** Open your terminal or command prompt and run:
    ```bash
    git clone https://github.com/ShreeNathX/WhatsApp-HealthCare-Bot
    cd whatsapp-healthcare-bot
    ```

2.  **Install Requirements:** Install all necessary Python libraries from the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Create `.env` File:** Create a file named **`.env`** inside the `whatsapp-healthcare-bot` folder. This file holds your secret keys.

    Copy and paste the following template into your **`.env`** file. **You must replace the placeholder values with your actual keys.**

    ```env
    # 🔑 OpenAI API Key for AI Reasoning and Voice Transcription
    # Get yours from https://platform.openai.com
    OPENAI_API_KEY=YOUR_OPENAI_API_KEY
    OPENAI_MODEL=gpt-3.5-turbo

    # 📞 Twilio Credentials (Required for WhatsApp Messaging)
    TWILIO_ACCOUNT_SID=YOUR_TWILIO_ACCOUNT_SID
    TWILIO_AUTH_TOKEN=YOUR_TWILIO_AUTH_TOKEN

    # Flask Configuration (Keep these default)
    FLASK_ENV=development
    FLASK_DEBUG=1
    PORT=5000
    ```

### 2️⃣ Ngrok Setup (Create a Public Link)

Twilio needs a public internet address to send messages to your local Flask app. Ngrok handles this.

1.  **Download Ngrok:** Get the Ngrok executable from the [Ngrok Download Page](https://ngrok.com/download).
2.  **Authenticate:** Get your Auth Token from the [Ngrok Dashboard](https://dashboard.ngrok.com). In your terminal, run:
    ```bash
    ngrok config add-authtoken <YOUR_NGROK_AUTH_TOKEN>
    ```
3.  **Start Ngrok:** In a **new terminal window**, start Ngrok to tunnel port 5000.
    ```bash
    ngrok http 5000
    ```
    Keep this terminal window open! Ngrok will give you a **Forwarding URL** (e.g., `https://random-word.ngrok-free.app`). **Copy this HTTPS link.**

### 3️⃣ Run the Flask App

In your **original terminal window**, start the Python application:

```bash
python app.py
```
Keep this window open. It will show log messages when a user texts the bot.

### 4️⃣ Twilio WhatsApp Setup

1.  **Twilio Console:** Log in to your [Twilio Console](https://console.twilio.com/).
2.  **WhatsApp Sandbox:** Navigate to **Messaging** -> **Try it out** -> **Send a WhatsApp Message**.
3.  **Join Sandbox:** Follow the instructions to send the "join" code (e.g., `join <your-code>`) to the Twilio Sandbox number (`+1 415 523 8886`) from your personal WhatsApp to activate testing.
4.  **Set Webhook:** Scroll down to the **Sandbox Configuration** settings. Under "When a message comes in," paste your Ngrok URL from Step 2, adding `/whatsapp` to the end.

    *Example Webhook URL:* `https://random-word.ngrok-free.app/whatsapp`

5.  **Save** the configuration. Your bot is now live!

---

## 📱 How to Use Your Assistant

Send a message, an emergency word, or even a **voice note** to the Twilio Sandbox number: `+1 415 523 8886`.

### Example Queries:

* **Text Query (English):** `I have a fever, cough, and feel very tired.`
* **Text Query (Hindi):** `मुझे बुखार है और सिर दर्द हो रहा है।`
* **Voice Note:** Record yourself saying, "My child is vomiting and has a high temperature."
* **Emergency Test:** `chest pain` (The bot will immediately reply with the 108 emergency message).

---

## 📎 Important Notes

* **Security:** Always keep your **`.env`** file private and ensure it is listed in your **`.gitignore`** file.
* **Non-Diagnostic:** This tool is an assistant for **triage and safety**; it is **not a substitute for a doctor**.
---

## 🚀 Future Enhancements — WhatsApp AI Health Assistant

This document outlines planned improvements and advanced features for future versions of the **AI Health Assistant**.  
The goal is to make the system more intelligent, scalable, and medically reliable while maintaining accessibility through **WhatsApp**.

---

| Area | Planned Feature | Description |
|:------|:----------------|:-------------|
| 🧠 **AI Intelligence** | Context Memory | Remember previous chats for personalized responses. |
|  | Severity Scoring | Classify symptoms as mild, moderate, or severe. |
|  | Medical Ontology | Use datasets like **SNOMED CT** or **ICD-10** for accurate symptom mapping. |
| 🗺️ **Location & Hospitals** | Google Maps Integration | Suggest nearby verified hospitals or clinics. |
|  | Emergency Routing | Provide real-time routes to emergency centers. |
|  | Specialist Suggestion | Recommend doctors based on detected symptoms. |
| 🩺 **Health Insights** | Trend Dashboard | Track regional symptom and disease trends. |
|  | Anonymous Analytics | Use anonymized data for healthcare insights. |
| 💬 **Communication & UX** | Voice Interaction | Add **OpenAI TTS** for two-way voice communication. |
|  | Health Education | Send infographics or videos for first-aid and prevention. |
|  | Emotion Awareness | Adjust tone based on user sentiment. |
| 🧩 **Architecture** | Cloud Hosting | Deploy on **AWS / GCP / Azure** for reliability. |
|  | Database Integration | Store chat and health data using **MongoDB / PostgreSQL**. |
|  | Caching System | Use **Redis** for fast message handling. |
| 🔒 **Security** | Encryption | Ensure end-to-end chat data protection. |
|  | Compliance | Follow **HIPAA / GDPR** health data standards. |
|  | Consent System | Add user consent for data usage. |
| 🌍 **Community Expansion** | Multilingual Support | Extend to 15+ Indian and global languages. |
|  | Partnerships | Collaborate with hospitals & NGOs. |
|  | Offline Mode | Explore SMS or low-bandwidth operation. |

---

## 💡 Vision Statement

The **WhatsApp AI Health Assistant (Powered by OpenAI)** aims to become a trusted, scalable, and multilingual digital companion that bridges healthcare accessibility gaps worldwide.  
Through future AI advancements, real-time health insights, and verified medical integration, it will evolve into a **personalized, safe, and reliable digital triage partner** for every user.

---


## 👨‍💻 Author and Team
**Suraj Kumar (Leader)**  
📧 Contact: [suraj110905@gmail.com](mailto:suraj110905@gmail.com).<br>
💬  For any queries, suggestions, or collaborations, feel free to reach out via email.



### Team Members
* **Arjun Chaudhary** - [GitHub Profile](https://github.com/Arzunchy).
* **Aditya Singh Baghel** – [GitHub Profile](https://github.com/ArBaghel).
* **Shree Nath Mahato** – [GitHub Profile](https://github.com/ShreeNathX).






