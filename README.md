# 🌌 VoxAI — Voice-Controlled Local AI Agent

A voice-controlled AI agent that transcribes speech, detects intent, and executes actions on your local machine — all through a beautiful Streamlit UI.

> Built as part of the Mem0 AI/ML & Generative AI Developer Intern Assignment.

---

## 🎥 Demo Video
[Watch on YouTube](#) ← replace with your YouTube link

## 📄 Technical Article
(https://medium.com/@prabhkaur1811/how-i-built-a-voice-controlled-ai-agent-that-listens-thinks-and-acts-5986aeb676ee) ← replace with your article link

---

## ✨ Features

- 🎤 **Audio Input** — Record via microphone OR upload `.wav` / `.mp3` / `.mp4`
- 📝 **Speech-to-Text** — Groq Whisper API (fast, free tier)
- 🧠 **Intent Detection** — Groq LLaMA 3.3 70B
- ⚡ **Tool Execution** — Create files, write code, summarize text, general chat
- 🔀 **Compound Commands** — Handles multiple intents in one audio input
- 🔒 **Sandboxed Output** — All file operations restricted to `output/` folder
- 🌌 **Beautiful UI** — Animated galaxy background, mobile responsive

---

## 🏗️ Architecture

```
Audio Input (mic / upload)
        ↓
Speech-to-Text (Groq Whisper API)
        ↓
Intent Detection (Groq LLaMA 3.3 70B)
        ↓
Tool Execution
   ├── write_code   → generates code → saves to output/
   ├── create_file  → creates file/folder in output/
   ├── summarize    → summarizes text → saves to output/
   └── general_chat → conversational response
        ↓
Streamlit UI (shows transcription, intent, action, output)
```

### File Structure
```
voice-ai-agent/
├── app.py           # Streamlit UI
├── stt.py           # Speech-to-Text (Groq Whisper)
├── intent.py        # Intent detection (Groq LLaMA)
├── tools.py         # Tool execution
├── actions.py       # File operation helpers
├── background.png   # UI background image
├── requirements.txt
├── .env.example
└── output/          # All generated files saved here (sandboxed)
```

---

## 🛠️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/Prabhkaur18/voxai.git
cd voxai
```

### 2. Create a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up API keys
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

Get a free Groq API key at [console.groq.com](https://console.groq.com)

### 5. Run the app
```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501)

---

## 🔑 API Keys

### Groq (Free Tier)
1. Sign up at [console.groq.com](https://console.groq.com)
2. Create an API key
3. Add to `.env`: `GROQ_API_KEY=your_key_here`

---

## ⚙️ Hardware Workaround

**Why Groq instead of local Whisper?**

The assignment recommends using a HuggingFace model like `openai/whisper-large-v3` locally. However, running this model locally requires:
- ~6-10GB of VRAM (GPU memory)
- 30-120 seconds per audio clip on CPU
- Large model download (~3GB)

To ensure the app works on **any device** without GPU requirements, I used **Groq's Whisper API** instead. Groq runs the same `whisper-large-v3` model on custom LPU hardware, completing transcription in under 2 seconds with a generous free tier.

**For local Whisper fallback:** If no `GROQ_API_KEY` is set, the system automatically falls back to local Whisper:
```bash
pip install openai-whisper
```

Similarly, for intent detection, **Groq's LLaMA 3.3 70B** is used instead of a local Ollama model to ensure compatibility across all devices.

---

## 🗣️ Example Commands

| Voice Command | Intent | Action |
|---|---|---|
| *"Create a Python file with a retry function"* | `write_code + create_file` | Generates code → saves to `output/` |
| *"Write a JavaScript sorting algorithm"* | `write_code` | Generates JS → saves to `output/` |
| *"Create a file called notes.txt"* | `create_file` | Creates file in `output/` |
| *"Summarize this: [text]"* | `summarize` | Summarizes → saves to `output/` |
| *"What is machine learning?"* | `general_chat` | Conversational response |

---

## 🎁 Bonus Features Implemented

- ✅ **Compound Commands** — Detects and executes multiple intents from one audio input
- ✅ **Graceful Degradation** — Falls back to rule-based intent if LLM fails; falls back to local Whisper if no API key

---

## 📦 Requirements

```
streamlit
httpx
python-dotenv
```

---

## 🚀 Deployed App

[https://voxaii.streamlit.app](https://voxaii.streamlit.app)

---

## 📄 License

MIT
