import streamlit as st
from stt import transcribe_audio
from intent import detect_intent, generate_code_from_text
from actions import create_file, write_code
import os
import base64

# ---------- LOAD BACKGROUND ----------
def get_base64(file):
    with open(file, "rb") as f:
        return base64.b64encode(f.read()).decode()

img = get_base64("background.png")

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="VoxAI", page_icon="🎤", layout="wide")

# ---------- LOAD FONTS ----------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Exo+2:wght@400&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# ---------- CSS ----------
st.markdown(f"""
<style>

/* REMOVE TOP SPACE */
.block-container {{
    padding-top: 0rem !important;
    padding-bottom: 0rem !important;
}}
header, footer {{
    visibility: hidden;
}}

/* 🌌 BACKGROUND (MOVING FIXED) */
.stApp {{
    background: url("data:image/png;base64,{img}");
    background-size: 120%;
    background-position: 0% 0%;
    background-repeat: no-repeat;
    background-attachment: scroll;
    animation: galaxyMove 60s linear infinite;
}}

/* 🌌 ANIMATION */
@keyframes galaxyMove {{
    0% {{ background-position: 0% 0%; }}
    50% {{ background-position: 50% 50%; }}
    100% {{ background-position: 100% 100%; }}
}}

/* DARK OVERLAY */
.stApp::before {{
    content: "";
    position: fixed;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.55);
    z-index: -1;
}}

/* TITLE */
.title {{
    font-family: 'Orbitron', sans-serif;
    font-size: 55px;
    text-align: center;
    color: #00ffe7;
    text-shadow: 0 0 30px #00ffe7;
    letter-spacing: 2px;
}}

/* SUBTITLE */
.subtitle {{
    font-family: 'Exo 2', sans-serif;
    text-align: center;
    font-size: 20px;
    color: #ffffff;
    margin-bottom: 25px;
    letter-spacing: 1px;
}}

/* UPLOADER BOX */
[data-testid="stFileUploader"] {{
    background: rgba(0,0,0,0.75) !important;
    border: 2px dashed #00ffe7 !important;
    border-radius: 15px !important;
    padding: 25px !important;
}}

/* REMOVE INNER WHITE */
[data-testid="stFileUploader"] section {{
    background: transparent !important;
    border: none !important;
}}

/* DROP YOUR AUDIO HERE - pink and bold */
[data-testid="stMarkdownContainer"] p {{
    color: #ff9de2 !important;
    font-weight: 800 !important;
    font-size: 20px !important;
}}

/* 200MB text - cyan and not bold */
[data-testid="stFileUploaderDropzone"] span {{
    color: #00ffe7 !important;
    font-weight: 400 !important;
    font-size: 14px !important;
    opacity: 1 !important;
}}

/* BUTTON */
[data-testid="stFileUploader"] button {{
    background: linear-gradient(45deg, #00ffe7, #0066ff) !important;
    border-radius: 10px !important;
}}

[data-testid="stFileUploader"] button p {{
    color: white !important;
    font-weight: bold !important;
}}

/* GLASS BOX */
.box {{
    padding: 20px;
    border-radius: 15px;
    background: rgba(0,0,0,0.6);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(0,255,231,0.3);
    box-shadow: 0 0 20px rgba(0,255,231,0.3);
    color: white !important;
    font-weight: 800 !important;
    font-size: 16px !important;
}}

/* SECTION HEADINGS - purple and bold */
.section {{
    font-size: 22px;
    color: #ffd700 !important;
    font-weight: 800 !important;
}}
/* 📱 MOBILE FIX */
@media (max-width: 768px) {{

    .title {{
        font-size: 32px !important;
    }}

    .subtitle {{
        font-size: 14px !important;
    }}

    [data-testid="stFileUploader"] {{
        padding: 15px !important;
    }}

    [data-testid="stFileUploader"] label {{
        font-size: 16px !important;
    }}

    [data-testid="stFileUploader"] button {{
        width: 100% !important;
    }}

    .box {{
        padding: 15px !important;
    }}
}}

/* FULL SCREEN HEIGHT + CENTER FIX */
html, body, .stApp {
    height: 100% !important;
}

.block-container {{
    min-height: 100vh !important;
    display: flex;
    flex-direction: column;
    justify-content: center;   /* vertical center */
    align-items: center;       /* horizontal center */
}}
}}

</style>
""", unsafe_allow_html=True)

# ---------- UI ----------
st.markdown('<div class="title">🌌 VoxAI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Voice → Intelligence → Action</div>', unsafe_allow_html=True)

st.divider()

uploaded_file = st.file_uploader("🎧 DROP YOUR AUDIO HERE", type=["wav", "mp3", "mp4"])

if uploaded_file is not None:

    file_path = os.path.join("output", uploaded_file.name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section">🧾 Transcribed Text</div>', unsafe_allow_html=True)
        text = transcribe_audio(file_path)
        st.markdown(f'<div class="box">{text}</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section">🧠 Detected Intent</div>', unsafe_allow_html=True)
        intent = detect_intent(text)
        st.markdown(f'<div class="box">{intent}</div>', unsafe_allow_html=True)

    st.divider()

    st.markdown('<div class="section">⚙️ Action Execution</div>', unsafe_allow_html=True)

    if intent == "create_file":
        result = create_file("ai_file.txt")
        st.success(result)

    elif intent == "write_code":
        code = generate_code_from_text(text)
        result = write_code("ai_generated.py", code)

        col3, col4 = st.columns(2)

        with col3:
            st.markdown('<div class="section">💻 Generated Code</div>', unsafe_allow_html=True)
            st.code(code, language="python")

        with col4:
            st.markdown('<div class="section">✅ Result</div>', unsafe_allow_html=True)
            st.success(result)