"""
Intent Detection Module
Uses Claude (via Anthropic API) or a local Ollama model to classify intent
from transcribed text.
"""

import os
import json
import re
import httpx


INTENT_SYSTEM_PROMPT = """You are an intent classifier for a voice-controlled file and code agent.

Analyze the user's transcribed speech and return a JSON object with:
{
  "intent": "<primary intent: create_file, write_code, summarize, general_chat>",
  "intents": ["<list of ALL intents detected, e.g. write_code and create_file together>"],
  "details": {
    "filename": "<suggested filename if applicable, else null>",
    "language": "<programming language if write_code, else null>",
    "description": "<brief description of what to create/do>",
    "content_hint": "<what content/topic to use, if mentioned>"
  }
}

Intent definitions:
- create_file: User wants to create a new file or folder
- write_code: User wants code written and saved to a file
- summarize: User wants text/content summarized
- general_chat: Anything else

Rules:
- Return ONLY valid JSON. No explanation, no markdown fences.
- If user says "create a python file with hello world" → intents: ["write_code", "create_file"]
- If user says "create a file called notes.txt" → intents: ["create_file"]
- Always populate the intents list with ALL detected intents
- Always populate the details object even with nulls
"""


def detect_intent(transcription: str) -> dict:
    """
    Detect intent from transcribed text.
    Tries Groq first, then Ollama, then rule-based fallback.
    """
    api_key = os.getenv("GROQ_API_KEY", "")

    if api_key:
        return _detect_with_claude(transcription, api_key)

    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    if _check_ollama(ollama_url):
        return _detect_with_ollama(transcription, ollama_url)

    return _rule_based_fallback(transcription)


def _detect_with_claude(transcription: str, api_key: str) -> dict:
    """Use Groq API for intent detection."""
    try:
        response = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": INTENT_SYSTEM_PROMPT},
                    {"role": "user", "content": transcription}
                ],
            },
            timeout=15.0,
        )
        if response.status_code == 200:
            raw = response.json()["choices"][0]["message"]["content"].strip()
            raw = re.sub(r"```json|```", "", raw).strip()
            return json.loads(raw)
        else:
            raise Exception(f"Groq API error: {response.status_code}")
    except Exception:
        return _rule_based_fallback(transcription)


def _check_ollama(base_url: str) -> bool:
    """Check if Ollama is running."""
    try:
        r = httpx.get(f"{base_url}/api/tags", timeout=2.0)
        return r.status_code == 200
    except Exception:
        return False


def _detect_with_ollama(transcription: str, base_url: str) -> dict:
    """Use local Ollama model for intent detection."""
    try:
        model = os.getenv("OLLAMA_MODEL", "llama3.2")
        response = httpx.post(
            f"{base_url}/api/generate",
            json={
                "model": model,
                "prompt": f"{INTENT_SYSTEM_PROMPT}\n\nUser said: {transcription}",
                "stream": False,
            },
            timeout=30.0,
        )
        if response.status_code == 200:
            raw = response.json()["response"].strip()
            # Strip any markdown fences
            raw = re.sub(r"```json|```", "", raw).strip()
            return json.loads(raw)
    except Exception:
        pass
    return _rule_based_fallback(transcription)


def _rule_based_fallback(transcription: str) -> dict:
    """Simple keyword-based intent detection as last resort."""
    text = transcription.lower()

    code_keywords = ["code", "function", "script", "program", "write a", "implement", "class", "def ", "python", "javascript", "java ", "c++"]
    file_keywords = ["create a file", "make a file", "new file", "create folder", "make folder"]
    summarize_keywords = ["summarize", "summary", "tldr", "brief", "overview", "condense"]

    detected_intents = []

    language = None
    for lang in ["python", "javascript", "typescript", "java", "c++", "go", "rust", "ruby", "php", "bash"]:
        if lang in text:
            language = lang
            break

    if any(k in text for k in code_keywords):
        detected_intents.append("write_code")
    if any(k in text for k in file_keywords):
        detected_intents.append("create_file")
    if any(k in text for k in summarize_keywords):
        detected_intents.append("summarize")

    if not detected_intents:
        detected_intents = ["general_chat"]

    return {
        "intent": detected_intents[0],
        "intents": detected_intents,
        "details": {
            "filename": f"output.{language or 'py'}" if "write_code" in detected_intents else "new_file.txt",
            "language": language,
            "description": transcription,
            "content_hint": transcription,
        },
    }
