"""
app.py - AI Content Generator | Task 3 - WeIntern Pvt Ltd Week 2 Assignment
"""
import streamlit as st
import os
import time
from datetime import datetime
from dotenv import load_dotenv

from generator import ContentGenerator
from prompts import build_prompt, CONTENT_PROMPTS, TONE_INSTRUCTIONS

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Content Generator",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif; }

/* ── White background ── */
.stApp {
    background: #f8f9fc;
    color: #1a1a2e;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
    box-shadow: 2px 0 8px rgba(0,0,0,0.04);
}
[data-testid="stSidebar"] * {
    color: #1a1a2e !important;
}

/* ── Cards / Bordered Containers ── */
.content-card, [data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 16px !important;
    padding: 24px !important;
    margin-bottom: 20px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
}

/* ── Header ── */
.app-header {
    text-align: center;
    padding: 32px 0 24px 0;
}
.app-header h1 {
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(90deg, #6366f1, #8b5cf6, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
}
.app-header p {
    color: #64748b;
    font-size: 1.05rem;
    margin-top: 8px;
}

/* ── Stats bar ── */
.stats-bar {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 20px;
}
.stat-chip {
    background: #eef2ff;
    border: 1px solid #c7d2fe;
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 0.82rem;
    color: #4f46e5;
    font-weight: 500;
}

/* ── Generated content box ── */
.generated-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 20px;
    white-space: pre-wrap;
    line-height: 1.75;
    color: #1e293b;
    font-size: 0.95rem;
    min-height: 120px;
    max-height: 500px;
    overflow-y: auto;
}

/* ── History item ── */
.history-item {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 10px;
}
.history-item:hover {
    border-color: #a5b4fc;
    background: #eef2ff;
}

/* ── Badges ── */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}
.badge-purple { background: #ede9fe; color: #7c3aed; }
.badge-blue   { background: #dbeafe; color: #1d4ed8; }
.badge-green  { background: #dcfce7; color: #16a34a; }
.badge-pink   { background: #fce7f3; color: #be185d; }
.badge-orange { background: #ffedd5; color: #c2410c; }

/* ── Buttons ── */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(99,102,241,0.25) !important;
}

/* ── SELECTBOX closed state ── */
.stSelectbox > div > div,
[data-testid="stSelectbox"] > div > div {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 10px !important;
    color: #1e293b !important;
    min-height: 42px !important;
}
.stSelectbox > div > div:hover,
[data-testid="stSelectbox"] > div > div:hover {
    border-color: #818cf8 !important;
}
.stSelectbox > div > div:focus-within,
[data-testid="stSelectbox"] > div > div:focus-within {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 2px rgba(99,102,241,0.15) !important;
}

/* ── Selectbox selected value text ── */
.stSelectbox span, .stSelectbox p, .stSelectbox div,
[data-testid="stSelectbox"] span, [data-testid="stSelectbox"] p,
[data-baseweb="select"] span, [data-baseweb="select"] div {
    color: #1e293b !important;
    -webkit-text-fill-color: #1e293b !important;
}
.stSelectbox svg { fill: #64748b !important; }

/* ── Dropdown popover ── */
[data-baseweb="popover"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.12) !important;
    overflow: hidden !important;
}
[data-baseweb="popover"] * { background: transparent !important; }

/* ── Dropdown list & options ── */
[data-baseweb="menu"], [role="listbox"] {
    background: #ffffff !important;
    border-radius: 12px !important;
    padding: 6px !important;
}
[role="option"], li[role="option"] {
    background: transparent !important;
    color: #1e293b !important;
    border-radius: 8px !important;
    padding: 10px 14px !important;
    font-size: 0.92rem !important;
    cursor: pointer !important;
    transition: background 0.15s ease !important;
}
[role="option"]:hover, li[role="option"]:hover {
    background: #eef2ff !important;
    color: #4f46e5 !important;
}
[role="option"][aria-selected="true"] {
    background: #e0e7ff !important;
    color: #4338ca !important;
    font-weight: 600 !important;
}

/* ── Inputs ── */
.stTextArea textarea, .stTextInput input {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 10px !important;
    color: #1e293b !important;
    font-size: 0.95rem !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 2px rgba(99,102,241,0.15) !important;
}

/* ── Labels ── */
.stSelectbox label, .stTextArea label, .stTextInput label {
    color: #374151 !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
}

/* ── Section titles ── */
.section-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 12px;
}

/* ── Divider ── */
hr { border-color: #e2e8f0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #f1f5f9; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

/* ── Alerts ── */
.stAlert { border-radius: 10px !important; }

/* ── Metrics ── */
[data-testid="stMetricValue"] { color: #1e293b !important; }
[data-testid="stMetricLabel"] { color: #64748b !important; }
</style>
""", unsafe_allow_html=True)
# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "generated_content" not in st.session_state:
    st.session_state.generated_content = ""
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""
# "api_key" holds the resolved key string (from .env or sidebar input).
# Stored as a plain string so it survives every Streamlit rerun reliably.
if "api_key" not in st.session_state:
    # Try to pre-populate from .env on first load
    st.session_state.api_key = os.getenv("GEMINI_API_KEY", "").strip()

# ── Module-level generator — re-configured on every rerun from session key ──
_generator = ContentGenerator()
if st.session_state.api_key:
    try:
        _generator.configure(st.session_state.api_key)
    except Exception:
        pass  # Invalid key is reported in the sidebar, not here

CONTENT_TYPES   = list(CONTENT_PROMPTS.keys())
TONES           = list(TONE_INSTRUCTIONS.keys())
LENGTHS         = ["Short", "Medium", "Long"]

BADGE_COLORS = {
    "Blog Post":            "badge-purple",
    "Social Media Caption": "badge-blue",
    "Text Summary":         "badge-green",
    "Email Newsletter":     "badge-pink",
    "Product Description":  "badge-orange",
}

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ✨ AI Content Generator")
    st.divider()

    # ── API Key section ──────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>🔑 API Configuration</div>", unsafe_allow_html=True)

    # Show current configuration status (never show the key itself)
    if st.session_state.api_key:
        st.success("✅ Gemini API key configured")
    else:
        st.warning("⚠️ Gemini API key not configured")

    # Always show input + button if no .env key (user can update at any time)
    env_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not env_key:
        sidebar_key_input = st.text_input(
            "Enter Gemini API Key",
            type="password",
            placeholder="AIza...",
            key="api_key_field",
            help="Get your free key at https://aistudio.google.com/app/apikey"
        )
        if st.button("🔓 Apply Key", use_container_width=True):
            entered = sidebar_key_input.strip()
            if entered:
                # Validate by attempting to configure
                test_gen = ContentGenerator()
                try:
                    test_gen.configure(entered)
                    # Key accepted — store in session state and rerun
                    st.session_state.api_key = entered
                    st.rerun()
                except Exception as e:
                    err = str(e)
                    if "API_KEY_INVALID" in err or "API key not valid" in err:
                        st.error("❌ Invalid API key. Please check and try again.")
                    else:
                        # Store anyway (network error etc.) and rerun
                        st.session_state.api_key = entered
                        st.rerun()
            else:
                st.warning("Please enter an API key first.")

        st.markdown("<div style='font-size:0.75rem;color:#64748b;margin-top:8px'>💡 Or create a .env file with GEMINI_API_KEY=your_key</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='font-size:0.75rem;color:#64748b;margin-top:4px'>Key loaded from .env file</div>", unsafe_allow_html=True)

    st.divider()

    # Stats
    st.markdown("<div class='section-title'>📊 Session Stats</div>", unsafe_allow_html=True)
    total = len(st.session_state.history)
    words = sum(h.get("word_count", 0) for h in st.session_state.history)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Generated", total)
    with col2:
        st.metric("Total Words", words)

    st.divider()

    # History
    st.markdown("<div class='section-title'>📜 History</div>", unsafe_allow_html=True)
    if st.session_state.history:
        for i, item in enumerate(reversed(st.session_state.history[-10:])):
            badge_cls = BADGE_COLORS.get(item["type"], "badge-purple")
            st.markdown(f"""
            <div class='history-item'>
                <span class='badge {badge_cls}'>{item['type']}</span>
                <div style='font-size:0.8rem;color:#334155;margin-top:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:200px'>{item['topic'][:50]}...</div>
                <div style='font-size:0.7rem;color:#64748b;margin-top:2px'>{item['timestamp']} · {item['word_count']} words</div>
            </div>
            """, unsafe_allow_html=True)
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.history = []
            st.rerun()
    else:
        st.markdown("<div style='color:#64748b;font-size:0.85rem;text-align:center;padding:20px 0'>No history yet.<br>Generate your first content!</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class='app-header'>
    <h1>✨ AI Content Generator</h1>
    <p>Powered by Google Gemini · Professional · Fast · Creative</p>
</div>
""", unsafe_allow_html=True)

# ── Two-column layout ──────────────────────────────────────────────────────
left_col, right_col = st.columns([1, 1.2], gap="large")

# ─────────────────────────────────────────────────────────────────────────────
# LEFT COLUMN - INPUTS
# ─────────────────────────────────────────────────────────────────────────────
with left_col:
    with st.container(border=True):
        st.markdown("<div class='section-title'>📝 Content Settings</div>", unsafe_allow_html=True)

        content_type = st.selectbox(
            "Content Type",
            CONTENT_TYPES,
            index=0,
            help="Choose the type of content to generate"
        )

        col_tone, col_length = st.columns(2)
        with col_tone:
            tone = st.selectbox("Tone", TONES, index=0)
        with col_length:
            length = st.selectbox("Length", LENGTHS, index=1)

        topic = st.text_area(
            "Topic / Content",
            placeholder="e.g. The future of AI in healthcare, or paste text to summarize...",
            height=160,
            help="Enter your topic, idea, or paste content you want to process"
        )

        # Character counter
        char_count = len(topic)
        MAX_CHARS = 3000
        color = "#34d399" if char_count < MAX_CHARS * 0.8 else ("#fb923c" if char_count < MAX_CHARS else "#f87171")
        st.markdown(f"<div style='text-align:right;font-size:0.78rem;color:{color};margin-top:-10px'>{char_count}/{MAX_CHARS} characters</div>", unsafe_allow_html=True)

    # Action buttons
    btn_col1, btn_col2, btn_col3 = st.columns([2, 1, 1])
    with btn_col1:
        generate_btn = st.button("⚡ Generate Content", use_container_width=True, type="primary")
    with btn_col2:
        regenerate_btn = st.button("🔄 Regenerate", use_container_width=True,
                                   disabled=not st.session_state.last_prompt)
    with btn_col3:
        clear_btn = st.button("🗑️ Clear", use_container_width=True)

    # Tone description
    if tone:
        tone_desc = TONE_INSTRUCTIONS.get(tone, "")
        st.markdown(f"<div style='font-size:0.78rem;color:#64748b;padding:8px 0'>💬 Tone: {tone_desc}</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# RIGHT COLUMN - OUTPUT
# ─────────────────────────────────────────────────────────────────────────────
with right_col:
    with st.container(border=True):
        st.markdown("<div class='section-title'>📄 Generated Content</div>", unsafe_allow_html=True)

        output_placeholder = st.empty()
        stats_placeholder  = st.empty()

        if st.session_state.generated_content:
            content_text = st.session_state.generated_content
            word_count   = len(content_text.split())
            char_count_out = len(content_text)

            output_placeholder.markdown(
                f"<div class='generated-box'>{content_text}</div>",
                unsafe_allow_html=True
            )

            stats_placeholder.markdown(f"""
            <div class='stats-bar' style='margin-top:12px'>
                <span class='stat-chip'>📝 {word_count} words</span>
                <span class='stat-chip'>🔡 {char_count_out} characters</span>
            </div>
            """, unsafe_allow_html=True)

            # Copy & Download row
            copy_col, dl_col = st.columns(2)
            with copy_col:
                st.download_button(
                    label="📋 Download .txt",
                    data=content_text,
                    file_name=f"content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with dl_col:
                if st.button("📋 Copy to Clipboard", use_container_width=True, key="copy_btn"):
                    safe_content = content_text.replace("`", "'").replace("\\", "\\\\")
                    st.markdown(
                        f"<script>navigator.clipboard.writeText(`{safe_content}`).then(()=>{{}})</script>",
                        unsafe_allow_html=True
                    )
                    st.toast("✅ Copied to clipboard!")
        else:
            output_placeholder.markdown("""
            <div class='generated-box' style='display:flex;align-items:center;justify-content:center;min-height:200px;flex-direction:column;gap:12px'>
                <div style='font-size:3rem'>✨</div>
                <div style='color:#64748b;text-align:center'>
                    Your generated content will appear here.<br>
                    <span style='font-size:0.85rem'>Configure settings and click Generate.</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# GENERATION LOGIC
# ─────────────────────────────────────────────────────────────────────────────
def run_generation(is_regenerate: bool = False):
    """Core generation logic."""
    # ── Guard: API key must be present ───────────────────────────────────────
    if not st.session_state.api_key:
        st.error("❌ Gemini API key not configured. Please enter your key in the sidebar.")
        return
    if not _generator.is_configured():
        st.error("❌ Gemini API key could not be applied. Please check your key in the sidebar.")
        return

    prompt_to_use = st.session_state.last_prompt if is_regenerate else ""

    if not is_regenerate:
        if not topic.strip():
            st.error("❌ Please enter a topic or content before generating.")
            return
        if len(topic.strip()) < 5:
            st.error("❌ Topic is too short. Please provide more detail.")
            return
        if len(topic) > MAX_CHARS:
            st.error(f"❌ Input exceeds {MAX_CHARS} characters. Please shorten it.")
            return
        prompt_to_use = build_prompt(content_type, topic.strip(), tone, length)
        st.session_state.last_prompt = prompt_to_use

    if not prompt_to_use:
        st.warning("⚠️ Nothing to regenerate. Generate content first.")
        return

    with st.spinner("🤖 Gemini is crafting your content..."):
        result = _generator.generate(prompt_to_use)

    if result["success"]:
        st.session_state.generated_content = result["content"]
        word_count = len(result["content"].split())

        # Determine topic label for history
        if is_regenerate:
            hist_topic = st.session_state.history[-1]["topic"] if st.session_state.history else "Regenerated"
        else:
            hist_topic = topic.strip()

        st.session_state.history.append({
            "type":       content_type,
            "topic":      hist_topic,
            "tone":       tone,
            "length":     length,
            "content":    result["content"],
            "word_count": word_count,
            "timestamp":  datetime.now().strftime("%H:%M")
        })
        st.rerun()
    else:
        st.error(f"❌ {result['error']}")

# ─────────────────────────────────────────────────────────────────────────────
# BUTTON HANDLERS
# ─────────────────────────────────────────────────────────────────────────────
if generate_btn:
    run_generation(is_regenerate=False)

if regenerate_btn:
    run_generation(is_regenerate=True)

if clear_btn:
    st.session_state.generated_content = ""
    st.session_state.last_prompt = ""
    st.rerun()
