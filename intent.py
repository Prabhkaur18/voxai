def detect_intent(text):
    text = text.lower()

    if "code" in text or "write" in text:
        return "write_code"

    elif "create" in text and "file" in text:
        return "create_file"

    elif "summarize" in text:
        return "summarize"

    else:
        return "chat"


def generate_code_from_text(text):
    text = text.lower()

    if "hello world" in text:
        return "print('Hello, World!')"

    elif "addition" in text:
        return "a = 5\nb = 3\nprint(a + b)"

    elif "loop" in text:
        return "for i in range(5):\n    print(i)"

    else:
        return "# Code not recognized"