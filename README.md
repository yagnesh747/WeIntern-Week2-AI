# WeIntern Week 2 — Artificial Intelligence Internship

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0%2B-lightgrey.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-red.svg)
![scikit--learn](https://img.shields.io/badge/scikit--learn-1.4%2B-orange.svg)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-Flash-blueviolet.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

> **Internship Program:** WeIntern Pvt Ltd — Week 2 Artificial Intelligence Internship Assignment  
> **Author:** AI Internship Team  
> **Repository:** `WeIntern-Week2-AI`

---

## 📌 Repository Overview

This repository contains the complete, production-ready deliverables for the **WeIntern Week 2 AI Internship**. The project comprises three distinct AI/NLP applications demonstrating local natural language processing, transparent heuristic-semantic candidate ranking, and modern cloud generative AI integration.

```
WeIntern-Week2-AI/
├── Task-1-AI-Chatbot/               # Task 1: Offline NLP Support Chatbot
├── Task-2-Resume-Screening-AI/      # Task 2: Multi-Factor Resume Screening & Ranking
├── Task-3-AI-Content-Generator/     # Task 3: Generative AI Multi-Format Content Studio
├── .gitignore                       # Standard repository hygiene & secrets filter
└── README.md                        # Master documentation (this file)
```

---

## 🚀 Projects Summary

| Task | Project Name | Tech Stack | Local URL | Primary NLP / AI Approach |
| :--- | :--- | :--- | :--- | :--- |
| **Task 1** | **AI Customer Support Chatbot** | Flask, HTML5/CSS3/JS, scikit-learn, NLTK | `http://localhost:5000` | TF-IDF + Cosine Similarity + Multi-Turn Context (100% Offline) |
| **Task 2** | **AI Resume Screening & Candidate Ranking** | Streamlit, scikit-learn, PyPDF2, python-docx | `http://localhost:8501` | 4-Factor Transparent Scoring Model (50% Semantic + 35% Skills + 10% Edu + 5% Exp) |
| **Task 3** | **AI Content Generator Studio** | Streamlit, Google GenAI SDK (`gemini-flash-latest`) | `http://localhost:8502` | Few-Shot Prompt Engineering, System Directives, Temperature Calibration |

---

## 📂 Project Details & Features

### 1️⃣ Task 1 — AI Customer Support Chatbot
A fast, lightweight, offline conversational agent designed for automated customer support.

* **Key Features:**
  * **12 Intent Categories:** Greetings, about, services, application tracking, delivery, refund policy, cancellation, payment, contact, working hours, thanks, and farewells.
  * **Multi-Turn Context:** Tracks prior intents to boost relevancy for conversational follow-up queries (+10% intent boost).
  * **Fallback System:** Graceful handling of out-of-scope or gibberish user inputs.
  * **Modern Responsive UI:** Clean light theme, quick-topic launcher chips, live typing indicator, character counters, and chat history clearing.
* **Architecture:** Preprocessing (Tokenization, WordNet Lemmatization, Stopword Filtering) ➔ Sublinear TF-IDF Vectorization ➔ Cosine Similarity Matrix.

---

### 2️⃣ Task 2 — AI Resume Screening & Candidate Ranking
An intelligent candidate ranking dashboard that matches applicant PDF/DOCX resumes against Job Descriptions with mathematical transparency.

* **Key Features:**
  * **Deterministic 4-Factor Scoring Formula:**
    * **50% Semantic / Text Similarity:** TF-IDF n-gram vectorization + Cosine Similarity.
    * **35% Required Skill Match:** Boundary-safe regex matching across 6 technical categories (Programming, Web, DB, ML/AI, Cloud, Core CS).
    * **10% Education Relevance:** Degree level heuristic evaluation (PhD/Master's/Bachelor's/Diploma).
    * **5% Experience Relevance:** Ratio of candidate experience vs. required JD years.
  * **Leaderboard & Analytics:** Ranked candidate table, matching vs. missing skill chips, score breakdown pills, and one-click CSV export.
  * **Sample Data Included:** Bundled sample JDs (AI/ML & Java) and 5 realistic test resumes.

---

### 3️⃣ Task 3 — AI Content Generator Studio
A modern generative studio powered by Google's latest Gemini Flash model for rapid, structured multi-format copy creation.

* **Key Features:**
  * **5 Content Types:** Blog Posts, Social Media Captions, Text Summaries, Email Newsletters, Product Descriptions.
  * **5 Writing Tones:** Professional, Casual, Friendly, Creative, Formal.
  * **3 Output Lengths:** Short, Medium, Long (calibrated word counts & structure).
  * **Productivity Tools:** Live character count meter, session stats tracking, one-click copy to clipboard, `.txt` file export, and instant regeneration.
  * **Flexible API Configuration:** Auto-loads from `.env` or accepts runtime sidebar key entry stored securely in session state.

---

## 🛠️ Global Installation & Setup

### Prerequisites
* **Python 3.10+** (Tested on Python 3.10 and 3.11)
* **Git** installed on your system
* *(Optional)* A free Google AI Studio API Key for Task 3 ([Get Key](https://aistudio.google.com/app/apikey))

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/WeIntern-Week2-AI.git
cd WeIntern-Week2-AI
```

### 2. Environment Setup (Recommended)
Create and activate an isolated Python virtual environment:

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 🖥️ How to Run Each Project

### Running Task 1: AI Chatbot
```bash
cd Task-1-AI-Chatbot
pip install -r requirements.txt
python app.py
```
👉 Open your browser at: **`http://localhost:5000`**

---

### Running Task 2: Resume Screening AI
```bash
cd Task-2-Resume-Screening-AI
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```
👉 Open your browser at: **`http://localhost:8501`**

---

### Running Task 3: AI Content Generator
```bash
cd Task-3-AI-Content-Generator
pip install -r requirements.txt

# (Optional) Copy .env.example to .env and insert your API key
cp .env.example .env

streamlit run app.py --server.port 8502
```
👉 Open your browser at: **`http://localhost:8502`**  
*(Note: You can also enter your Gemini API key directly into the sidebar at runtime).*

---

## 🧪 Automated Testing & Verification

Each project includes dedicated unit test suites:

| Task | Test Command | Test Suite Location | Coverage |
| :--- | :--- | :--- | :--- |
| **Task 1** | `python tests/test_chatbot.py` | `Task-1-AI-Chatbot/tests/` | 31 test cases (All 12 intents, fallbacks, edge cases) — 100% Pass |
| **Task 2** | `python tests/test_screening.py` | `Task-2-Resume-Screening-AI/tests/` | 8 unit tests (Skill extraction, entity parsing, 4-factor scoring) — 100% Pass |
| **Task 3** | `python tests/test_generator.py` | `Task-3-AI-Content-Generator/tests/` | 4 unit tests (Prompt formatting, tones, config error handling) — 100% Pass |

To run all tests sequentially:
```bash
python Task-1-AI-Chatbot/tests/test_chatbot.py
python Task-2-Resume-Screening-AI/tests/test_screening.py
python Task-3-AI-Content-Generator/tests/test_generator.py
```

---

## 🔒 Security & Safe Publishing Guarantee

This repository follows best practices for secure publishing:
* **No Hardcoded Secrets:** Zero API keys, passwords, or personal credentials are coded into any file.
* **Safe Configuration:** Task 3 uses `.env.example` with placeholder strings. Real `.env` files are excluded by `.gitignore`.
* **Synthetic Test Data:** Resumes in Task 2 use synthetic candidate profiles (`example.com` domains and 555-numbers) created solely for demonstration.

---

## 🔮 Future Enhancements

* **Task 1 (Chatbot):** Integrate speech-to-text (Web Speech API) and multi-language support.
* **Task 2 (Resume Screener):** Integrate dense vector embeddings (e.g. Sentence-BERT) for deep semantic matching alongside the TF-IDF engine.
* **Task 3 (Content Generator):** Add direct Markdown export, social media auto-scheduler integrations, and custom system-prompt fine tuning.

---

## 📄 License
This project is developed for educational and evaluation purposes as part of the **WeIntern AI Internship Program**.
