# WeIntern AI Chatbot
### Week 2 Artificial Intelligence Internship Assignment — Task 1
**Organization:** WeIntern Pvt Ltd

---

## Project Overview

An NLP-powered customer support chatbot built with **Python + Flask** on the backend and **Vanilla HTML/CSS/JS** on the frontend. It uses **TF-IDF vectorization** combined with **Cosine Similarity** for intent recognition, and supports multi-turn context-aware conversation.

> No paid APIs. No external AI services. Fully local and lightweight.

---

## Features

| Feature | Details |
|---|---|
| **12 Intents** | greeting, goodbye, thanks, about, services, order_status, delivery, refund, cancellation, payment, contact, working_hours |
| **NLP Engine** | TF-IDF + Cosine Similarity via scikit-learn |
| **Multi-turn context** | Previous intent boosts related follow-up matches |
| **Fallback handling** | Graceful unknown-query responses |
| **Modern Chat UI** | Dark-mode responsive design with 3-column layout |
| **Session history** | Conversation persists across page reloads |
| **Clear chat** | One-click reset |
| **Confidence display** | Live intent + confidence score debug panel |
| **Typing indicator** | Animated three-dot loader |
| **Timestamps** | Every message shows formatted time |
| **Character counter** | Input capped at 500 chars |
| **Error handling** | Network errors, empty inputs, long messages all handled |

---

## Architecture

```
week 2/
├── app.py              # Flask server + REST API routes
├── chatbot.py          # NLP engine (TF-IDF, lemmatizer, intent matcher)
├── intents.json        # Knowledge base (12 intents, 100+ utterances)
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html      # Chat UI markup
├── static/
│   ├── style.css       # Full CSS design system (dark theme)
│   └── script.js       # Frontend logic (fetch, render, events)
└── tests/
    └── test_chatbot.py # 31 automated test cases
```

### Request Flow

```
Browser  →  GET /           →  Flask renders index.html
User msg →  POST /api/chat  →  chatbot.respond()  →  JSON response
                                  │
                         ┌────────▼────────┐
                         │  Preprocess     │  lowercase, strip punct,
                         │  (NLTK)         │  tokenize, lemmatize,
                         └────────┬────────┘  remove stopwords
                                  │
                         ┌────────▼────────┐
                         │  TF-IDF         │  transform user query
                         │  Vectorizer     │  against trained matrix
                         └────────┬────────┘
                                  │
                         ┌────────▼────────┐
                         │  Cosine         │  score each training
                         │  Similarity     │  pattern vs query
                         └────────┬────────┘
                                  │
                         ┌────────▼────────┐
                         │  Context Boost  │  +0.10 for same intent
                         │  (multi-turn)   │  +0.05 for related group
                         └────────┬────────┘
                                  │
                         ┌────────▼────────┐
                         │  Intent Select  │  best score >= 0.15
                         │  + Fallback     │  else → fallback
                         └─────────────────┘
```

---

## NLP / TF-IDF Explanation

**TF-IDF (Term Frequency–Inverse Document Frequency)** converts text into numerical vectors:

- **TF** — how often a word appears in a document  
- **IDF** — penalizes words that appear in many documents (common words matter less)  

Each training utterance becomes a TF-IDF vector. When the user sends a message, it is vectorized the same way and its **Cosine Similarity** (angle between vectors) is measured against every training pattern. The intent with the highest similarity score wins.

**Preprocessing pipeline (NLTK):**
1. Lowercase
2. Remove punctuation
3. Tokenize (word_tokenize)
4. Lemmatize (WordNetLemmatizer) — "running" → "run"
5. Remove stopwords ("the", "a", "is" …)

**Confidence threshold:** 0.15 — scores below this trigger the fallback response.

**Context boost:** The previous intent gets +0.10 added to all its matching patterns, making follow-up questions in the same topic more likely to match correctly.

---

## Installation

### Prerequisites
- Python 3.9+
- pip

### Steps

```bash
# 1. Navigate to project directory
cd "week 2"

# 2. (Optional) Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. NLTK data downloads automatically on first run
#    (punkt, stopwords, wordnet — ~10 MB total)
```

---

## How to Run

```bash
# Start the Flask development server
python app.py
```

Open your browser at: **http://127.0.0.1:5000**

### API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Chat UI |
| POST | `/api/chat` | Send a message, receive bot reply |
| POST | `/api/clear` | Clear session history |
| GET | `/api/history` | Retrieve session conversation |
| GET | `/api/health` | Service health check |

### Run Tests

```bash
python tests/test_chatbot.py
```

---

## Test Cases & Expected Results

| # | Input | Expected Intent | Notes |
|---|---|---|---|
| 1 | "hello" | greeting | Direct keyword match |
| 2 | "hey there!" | greeting | Casual variant |
| 3 | "good morning" | greeting | Time-based greeting |
| 4 | "what is weintern?" | about | Company question |
| 5 | "tell me about yourself" | about | Bot identity |
| 6 | "what services do you offer?" | services | Services query |
| 7 | "what programs are available" | services | Program variant |
| 8 | "track my application" | order_status | Application tracking |
| 9 | "where is my order?" | order_status | Order location |
| 10 | "check my application status" | order_status | Status check |
| 11 | "when will I get my certificate?" | delivery | Certificate ETA |
| 12 | "how long does it take?" | delivery | Generic ETA |
| 13 | "delivery timeframe" | delivery | Keyword match |
| 14 | "I want a refund" | refund | Direct request |
| 15 | "refund policy" | refund | Policy question |
| 16 | "how to get money back" | refund | Informal phrasing |
| 17 | "how do I cancel my order?" | cancellation | Cancel order |
| 18 | "cancel my enrollment" | cancellation | Cancel enrollment |
| 19 | "what payment methods are accepted?" | payment | Payment methods |
| 20 | "my payment failed" | payment | Failure scenario |
| 21 | "how much does it cost?" | payment | Pricing |
| 22 | "how do I contact support?" | contact | Contact query |
| 23 | "what is your phone number?" | contact | Phone inquiry |
| 24 | "what are your working hours?" | working_hours | Hours |
| 25 | "are you open on sunday?" | working_hours | Weekend check |
| 26 | "thank you so much!" | thanks | Gratitude |
| 27 | "that was really helpful" | thanks | Implicit gratitude |
| 28 | "bye!" | goodbye | Farewell |
| 29 | "take care" | goodbye | Parting phrase |
| 30 | "xyzabc random gibberish" | fallback | Unknown input |
| 31 | "12345" | fallback | Numeric-only input |

---

## Technologies Used

| Technology | Purpose |
|---|---|
| Python 3 | Core language |
| Flask 3.x | Web framework + REST API |
| scikit-learn | TF-IDF vectorizer + cosine similarity |
| NLTK | Tokenization, lemmatization, stopwords |
| NumPy | Similarity matrix operations |
| HTML5 | Chat UI structure |
| Vanilla CSS | Dark theme, custom design system |
| Vanilla JS | Fetch API, DOM manipulation |

---

## Future Improvements

- [ ] Named-entity recognition (extract names, order IDs from messages)
- [ ] Deep learning model (BERT / DistilBERT) for higher accuracy
- [ ] Admin dashboard to add/edit intents without restarting
- [ ] User authentication & personalized history
- [ ] Voice input/output (Web Speech API)
- [ ] Multi-language support (Hindi, Tamil, etc.)
- [ ] Integration with real ticketing system (Zendesk, Freshdesk)
- [ ] Proactive suggestions based on conversation context
- [ ] Analytics dashboard (most asked intents, fallback rate)

---

*Submitted as part of Week 2 AI Internship — Task 1 | WeIntern Pvt Ltd*
