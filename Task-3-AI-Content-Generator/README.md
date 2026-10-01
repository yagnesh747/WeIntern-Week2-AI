# ✨ Task 3: AI Content Generator

> **WeIntern Pvt Ltd — Week 2 Artificial Intelligence Internship**

A professional, production-ready AI content generation tool powered by **Google Gemini** and built with **Streamlit**. Generate high-quality Blog Posts, Social Media Captions, Text Summaries, Email Newsletters, and Product Descriptions — all with customizable tone and length.

---

## 🚀 Features

| Feature | Details |
|---------|---------|
| **5 Content Types** | Blog Post, Social Media Caption, Text Summary, Email Newsletter, Product Description |
| **5 Tone Options** | Professional, Casual, Friendly, Creative, Formal |
| **3 Length Options** | Short, Medium, Long |
| **Generate & Regenerate** | One-click generation and re-generation with same settings |
| **Copy to Clipboard** | Instant clipboard copy |
| **Download as .txt** | Save generated content locally |
| **Session History** | Last 10 generated items with type, topic, and word count |
| **Session Stats** | Total generated count and total word count |
| **Input Validation** | Empty topic, short input, character limit (3000), missing API key |
| **Error Handling** | Invalid key, rate limit, safety filter, network errors |
| **Secure API Key** | Loaded from `.env`, never hardcoded |

---

## 🏗️ Architecture

```
AI_Content_Generator/
├── app.py              # Streamlit UI + session management
├── generator.py        # Gemini API client & error handling
├── prompts.py          # Prompt engineering templates
├── requirements.txt    # Python dependencies
├── .env                # API key (not committed to git)
└── .env.example        # Template for API key setup
```

### Component Responsibilities

- **`app.py`** — Renders the UI, handles user interactions, manages session state, and orchestrates the generate/regenerate/clear flow
- **`generator.py`** — Wraps the `google-generativeai` SDK; handles configuration, API calls, and error translation
- **`prompts.py`** — Houses all prompt templates keyed by `[content_type][length]`, and tone instructions; exposes `build_prompt()` factory

---

## 🧠 Prompt Engineering

The system uses **structured, context-aware prompts** rather than generic requests:

### Template Strategy
Each content type × length combination has a dedicated prompt template:

```python
"Blog Post" → {
    "Short":  "Write a concise blog post (150-250 words)...",
    "Medium": "Write a well-structured blog post (400-600 words)...",
    "Long":   "Write a comprehensive blog post (800-1200 words)..."
}
```

### Tone Injection
A tone instruction string is prepended as a **system-level directive**:

```python
TONE_INSTRUCTIONS = {
    "Professional": "Use formal, authoritative, and expert language...",
    "Casual":       "Use relaxed, conversational language...",
    ...
}
```

### Full Prompt Structure
```
[System role instruction]
[Tone directive]
[Content type + length template with {topic} and {tone} substituted]
```

This produces deterministic, high-quality outputs without relying on vague prompts like "write something about X".

---

## 📋 Sample Inputs & Outputs

### Example 1: Blog Post
| Field | Value |
|-------|-------|
| Content Type | Blog Post |
| Topic | The impact of AI on modern education |
| Tone | Professional |
| Length | Medium |

**Generated output excerpt:**
```
## Transforming Classrooms: How AI is Reshaping Modern Education

Artificial intelligence is no longer a distant concept in education — it is actively
reshaping how students learn, how teachers instruct, and how institutions operate.
From personalized learning platforms to automated grading systems...
```

### Example 2: Social Media Caption
| Field | Value |
|-------|-------|
| Content Type | Social Media Caption |
| Topic | Launching a new productivity app |
| Tone | Creative |
| Length | Short |

**Generated output excerpt:**
```
🚀 Stop managing your time. Start owning it. ✨
Introducing the app that turns your chaos into clarity — launching TODAY.

#ProductivityApp #WorkSmart #Launch #Innovation #TechStartup
```

### Example 3: Text Summary
| Field | Value |
|-------|-------|
| Content Type | Text Summary |
| Topic | [Pasted research paper abstract] |
| Tone | Formal |
| Length | Short |

**Generated output excerpt:**
```
This study investigates the relationship between machine learning model complexity
and real-world deployment performance across three industry domains. Key findings
indicate that model simplicity correlates positively with deployment reliability...
```

---

## ⚙️ Setup & Installation

### 1. Clone / Navigate to folder
```bash
cd "week 2/AI_Content_Generator"
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Get a free Gemini API key
- Visit: https://aistudio.google.com/app/apikey
- Create a free API key (no billing required)

### 4. Configure the API key
```bash
# Copy the example file
copy .env.example .env

# Edit .env and add your key
GEMINI_API_KEY=your_gemini_api_key_here
```

### 5. Run the application
```bash
streamlit run app.py --server.port 8502
```

The app opens at **http://localhost:8502**

---

## 🔒 Security

- ✅ API key loaded exclusively from environment variable / `.env` file
- ✅ Key never logged, printed, or stored in session state as plaintext
- ✅ `.env` should be in `.gitignore` — never commit to version control
- ✅ Input sanitization against excessively long prompts (3000 char limit)

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.11 | Core language |
| Streamlit 1.28+ | Web UI framework |
| google-generativeai 0.8+ | Gemini API SDK |
| python-dotenv | .env file management |

### Model Used
**`gemini-1.5-flash`** — Fast, high-quality, free-tier available

### Generation Config
```python
temperature=0.8    # Creative but coherent
top_p=0.95         # Nucleus sampling
top_k=40           # Token diversity
max_output_tokens=2048
```

---

## 🎨 UI Design

- **Dark glassmorphism** theme with purple/blue gradient
- **Google Inter** font for modern typography
- Responsive 2-column layout (settings | output)
- Real-time character counter with color-coded warnings
- Animated sidebar with session history and stats
- Smooth hover effects and micro-interactions

---

## ✅ Validation & Error Handling

| Scenario | Behavior |
|----------|---------|
| Empty topic | Error: "Please enter a topic" |
| Topic < 5 chars | Error: "Topic is too short" |
| Topic > 3000 chars | Error: "Input exceeds limit" |
| No API key | Error: "API key not configured" |
| Invalid API key | Error: "Invalid API key. Please check..." |
| Rate limit (429) | Error: "Rate limit exceeded. Please wait..." |
| Safety filter block | Error: "Content blocked by safety filters" |
| Generic API failure | Error: descriptive message from SDK |

---

*Built for WeIntern Pvt Ltd — Week 2 AI Internship Assignment*
