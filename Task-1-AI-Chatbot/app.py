"""
app.py - Flask Web Application for WeIntern AI Chatbot
=======================================================
Serves the chat UI and exposes REST API endpoints for
the NLP chatbot engine defined in chatbot.py.

Routes:
    GET  /              -> Chat UI (templates/index.html)
    POST /api/chat      -> Process user message, return JSON
    POST /api/clear     -> Clear session conversation history
    GET  /api/history   -> Retrieve session history
    GET  /api/health    -> Health-check endpoint

Author  : WeIntern AI Team
Version : 1.0.0
"""

import logging
from datetime import datetime
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session,
)
from chatbot import WeInternChatbot

# ---------------------------------------------------------------------------
# App configuration
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = "weintern_chatbot_secret_key_2024_week2_assignment"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Initialise chatbot (single instance, shared across requests)
# ---------------------------------------------------------------------------
try:
    chatbot = WeInternChatbot(intents_path="intents.json")
    logger.info("Chatbot loaded successfully.")
except Exception as exc:
    logger.critical(f"Failed to load chatbot: {exc}")
    raise


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------
def _init_session() -> None:
    """Ensure session variables are initialised."""
    if "history" not in session:
        session["history"] = []
    if "context_intent" not in session:
        session["context_intent"] = None
    if "turn_count" not in session:
        session["turn_count"] = 0


def _format_history_entry(role: str, text: str, meta: dict = None) -> dict:
    """Create a standardised history entry."""
    entry = {
        "role"     : role,           # "user" or "bot"
        "text"     : text,
        "timestamp": datetime.utcnow().isoformat(),
    }
    if meta:
        entry.update(meta)
    return entry


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    """Render the main chat interface."""
    _init_session()
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Process a user message and return the bot's response.

    Request body (JSON):
        { "message": "user text here" }

    Response (JSON):
        {
            "response"    : "bot reply",
            "intent"      : "detected_intent",
            "confidence"  : 0.85,
            "is_fallback" : false,
            "turn"        : 3,
            "timestamp"   : "2024-..."
        }
    """
    _init_session()

    # --- Input validation ---
    data = request.get_json(silent=True)
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' field in request body."}), 400

    user_message = str(data["message"]).strip()
    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    if len(user_message) > 500:
        return jsonify({"error": "Message too long (max 500 characters)."}), 400

    # --- Generate response ---
    try:
        context = session.get("context_intent")
        result  = chatbot.respond(user_message, context_intent=context)
    except Exception as exc:
        logger.error(f"Chatbot error: {exc}")
        return jsonify({"error": "Internal server error. Please try again."}), 500

    # --- Update session ---
    session["turn_count"] = session.get("turn_count", 0) + 1

    # Update context (clear after goodbye)
    if result["intent"] == "goodbye":
        session["context_intent"] = None
    elif not result["is_fallback"]:
        session["context_intent"] = result["intent"]

    # Append to history (keep last 50 turns to avoid session bloat)
    history = session.get("history", [])
    history.append(_format_history_entry("user", user_message))
    history.append(_format_history_entry("bot", result["response"], {
        "intent"    : result["intent"],
        "confidence": result["confidence"],
        "is_fallback": result["is_fallback"],
    }))
    session["history"] = history[-100:]   # cap at 50 pairs

    response_payload = {
        "response"   : result["response"],
        "intent"     : result["intent"],
        "confidence" : result["confidence"],
        "is_fallback": result["is_fallback"],
        "turn"       : session["turn_count"],
        "timestamp"  : result["timestamp"],
    }
    logger.info(
        f"Turn {session['turn_count']} | Intent: {result['intent']} "
        f"({result['confidence']:.3f}) | User: '{user_message[:60]}'"
    )
    return jsonify(response_payload)


@app.route("/api/clear", methods=["POST"])
def clear_chat():
    """Clear conversation history and reset context."""
    _init_session()
    session["history"]        = []
    session["context_intent"] = None
    session["turn_count"]     = 0
    logger.info("Session cleared.")
    return jsonify({"status": "ok", "message": "Conversation cleared."})


@app.route("/api/history", methods=["GET"])
def get_history():
    """Return the current session conversation history."""
    _init_session()
    return jsonify({
        "history"   : session.get("history", []),
        "turn_count": session.get("turn_count", 0),
    })


@app.route("/api/health", methods=["GET"])
def health():
    """Simple health-check endpoint."""
    return jsonify({
        "status"  : "ok",
        "service" : "WeIntern AI Chatbot",
        "version" : "1.0.0",
        "intents" : len(chatbot.get_intent_list()),
    })


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("  WeIntern AI Chatbot — Flask Dev Server")
    print("  Visit: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=5000)
