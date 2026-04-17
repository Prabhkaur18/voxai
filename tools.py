"""
Tool Execution Module
Executes actions based on detected intent.
All file operations are sandboxed to the output/ directory.
"""

import os
import json
import re
import httpx
from pathlib import Path
from datetime import datetime


OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


def execute_action(intent_result: dict, transcription: str) -> dict:
    """
    Route to the correct tool based on intent.
    Supports multitask — executes ALL detected intents.
    """
    intents = intent_result.get("intents", [intent_result.get("intent", "general_chat")])
    details = intent_result.get("details", {})

    # Single intent
    if len(intents) == 1:
        return _route(intents[0], details, transcription)

    # Multitask — run all intents and combine results
    results = []
    for intent in intents:
        result = _route(intent, details, transcription)
        results.append(result)

    # Combine all results into one
    combined_output = "\n\n---\n\n".join(
        [r["output"] for r in results if r.get("output")]
    )
    combined_message = "\n".join([r["message"] for r in results])
    combined_files = [r["file_path"] for r in results if r.get("file_path")]

    return {
        "success": all(r["success"] for r in results),
        "action": " + ".join([r["action"] for r in results]),
        "message": combined_message,
        "output": combined_output,
        "file_path": ", ".join(combined_files) if combined_files else None,
        "language": results[0].get("language", "text"),
    }


def _route(intent: str, details: dict, transcription: str) -> dict:
    """Route a single intent to its handler."""
    if intent == "write_code":
        return _handle_write_code(details, transcription)
    elif intent == "create_file":
        return _handle_create_file(details, transcription)
    elif intent == "summarize":
        return _handle_summarize(details, transcription)
    else:
        return _handle_chat(transcription)


# ─── Handlers ────────────────────────────────────────────────────────────────

def _handle_write_code(details: dict, transcription: str) -> dict:
    """Generate code and save to output/ folder."""
    language = details.get("language") or "python"
    filename = details.get("filename") or _generate_filename(language)
    description = details.get("description") or transcription

    # Sanitize filename
    filename = _safe_filename(filename)
    ext_map = {
        "python": "py", "javascript": "js", "typescript": "ts",
        "java": "java", "go": "go", "rust": "rs", "ruby": "rb",
        "php": "php", "bash": "sh", "c++": "cpp", "c": "c",
    }
    if "." not in filename:
        filename += f".{ext_map.get(language, 'py')}"

    # Generate code
    code = _generate_code(description, language)

    file_path = OUTPUT_DIR / filename
    file_path.write_text(code)

    return {
        "success": True,
        "action": "write_code → save_file",
        "message": f"✅ Code generated and saved to `output/{filename}`",
        "output": code,
        "file_path": str(file_path),
        "language": language,
    }


def _handle_create_file(details: dict, transcription: str) -> dict:
    """Create a new file or folder in output/."""
    filename = details.get("filename") or "new_file.txt"
    filename = _safe_filename(filename)
    content_hint = details.get("content_hint") or ""

    # Check if it's a folder request
    text = transcription.lower()
    if "folder" in text or "directory" in text:
        folder_name = _extract_name(text, "folder") or filename.replace(".txt", "")
        folder_path = OUTPUT_DIR / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)
        return {
            "success": True,
            "action": "create_folder",
            "message": f"✅ Folder `output/{folder_name}/` created successfully",
            "output": None,
            "file_path": str(folder_path),
            "language": None,
        }

    # Create file with optional content
    content = f"# {filename}\nCreated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    if content_hint:
        content += f"# Purpose: {content_hint}\n\n"
    content += "# Add your content here\n"

    file_path = OUTPUT_DIR / filename
    file_path.write_text(content)

    return {
        "success": True,
        "action": "create_file",
        "message": f"✅ File `output/{filename}` created successfully",
        "output": content,
        "file_path": str(file_path),
        "language": "text",
    }


def _handle_summarize(details: dict, transcription: str) -> dict:
    """Summarize the provided text using LLM."""
    content = details.get("content_hint") or transcription
    summary = _generate_summary(content)

    # Save summary to output
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"summary_{ts}.txt"
    file_path = OUTPUT_DIR / filename
    file_path.write_text(f"SUMMARY\n{'='*40}\n{summary}\n\nORIGINAL\n{'='*40}\n{content}")

    return {
        "success": True,
        "action": "summarize_text",
        "message": f"✅ Summary saved to `output/{filename}`",
        "output": summary,
        "file_path": str(file_path),
        "language": "text",
    }


def _handle_chat(transcription: str) -> dict:
    """Handle general chat responses."""
    response = _chat_response(transcription)
    return {
        "success": True,
        "action": "general_chat",
        "message": "✅ Response generated",
        "output": response,
        "file_path": None,
        "language": "text",
    }


# ─── LLM Helpers ─────────────────────────────────────────────────────────────

def _call_llm(prompt: str, system: str) -> str:
    """Call LLM — tries Groq, then Ollama, then template fallback."""
    api_key = os.getenv("GROQ_API_KEY", "")

    if api_key:
        try:
            response = httpx.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt}
                    ],
                },
                timeout=20.0,
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
        except Exception:
            pass

    # Try Ollama
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    try:
        model = os.getenv("OLLAMA_MODEL", "llama3.2")
        r = httpx.post(
            f"{ollama_url}/api/generate",
            json={"model": model, "prompt": f"{system}\n\n{prompt}", "stream": False},
            timeout=30.0,
        )
        if r.status_code == 200:
            return r.json()["response"]
    except Exception:
        pass

    return None


def _generate_code(description: str, language: str) -> str:
    """Generate code using LLM or template."""
    system = f"You are an expert {language} programmer. Write clean, well-commented code. Return ONLY the code, no explanation or markdown fences."
    result = _call_llm(f"Write {language} code for: {description}", system)

    if result:
        # Strip markdown fences if present
        result = re.sub(r"```\w*\n?", "", result).strip()
        return result

    # Template fallback
    templates = {
        "python": f'"""\\n{description}\\n"""\n\ndef main():\n    # TODO: implement\n    print("Hello from voice agent!")\n\nif __name__ == "__main__":\n    main()\n',
        "javascript": f'// {description}\n\nfunction main() {{\n  // TODO: implement\n  console.log("Hello from voice agent!");\n}}\n\nmain();\n',
    }
    return templates.get(language, f"# {description}\n# TODO: implement\n")


def _generate_summary(text: str) -> str:
    """Generate a summary using LLM or simple truncation."""
    system = "You are a helpful assistant. Summarize the provided text concisely in 3-5 sentences."
    result = _call_llm(text, system)
    if result:
        return result
    # Fallback: first 200 chars
    return text[:200] + ("..." if len(text) > 200 else "")


def _chat_response(text: str) -> str:
    """Generate a conversational response."""
    system = "You are a helpful voice assistant. Give a concise, friendly response."
    result = _call_llm(text, system)
    if result:
        return result
    return f"I heard: \"{text}\". I'm ready to help — try asking me to create a file or write some code!"


# ─── Utilities ───────────────────────────────────────────────────────────────

def _safe_filename(name: str) -> str:
    """Remove dangerous characters from filename."""
    name = re.sub(r"[^\w\.\-]", "_", name)
    name = name.lstrip("./")
    return name or "output_file"


def _generate_filename(language: str) -> str:
    ts = datetime.now().strftime("%H%M%S")
    ext_map = {"python": "py", "javascript": "js", "typescript": "ts"}
    ext = ext_map.get(language, language[:2] if language else "py")
    return f"code_{ts}.{ext}"


def _extract_name(text: str, kind: str) -> str:
    """Try to extract a name after keywords like 'called', 'named'."""
    patterns = [
        rf"{kind}\s+(?:called|named)\s+['\"]?(\w+)['\"]?",
        rf"(?:called|named)\s+['\"]?(\w+)['\"]?\s+{kind}",
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(1)
    return None
