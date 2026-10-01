"""
chatbot.py - Core NLP Engine for WeIntern Customer Support Chatbot
==================================================================
Uses TF-IDF vectorization + Cosine Similarity for intent recognition.
Implements context-aware multi-turn conversation management.

Author  : WeIntern AI Team
Version : 1.0.0
"""

import json
import random
import re
import string
import logging
from datetime import datetime
from typing import Optional

import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# ---------------------------------------------------------------------------
# Setup logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Download required NLTK data (silent after first run)
# ---------------------------------------------------------------------------
def _download_nltk_data() -> None:
    """Download required NLTK corpora if not already present."""
    resources = [
        ("tokenizers/punkt", "punkt"),
        ("tokenizers/punkt_tab", "punkt_tab"),
        ("corpora/stopwords", "stopwords"),
        ("corpora/wordnet", "wordnet"),
    ]
    for path, name in resources:
        try:
            nltk.data.find(path)
        except LookupError:
            logger.info(f"Downloading NLTK resource: {name}")
            nltk.download(name, quiet=True)

_download_nltk_data()

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# ---------------------------------------------------------------------------
# WeInternChatbot
# ---------------------------------------------------------------------------
class WeInternChatbot:
    """
    NLP-based customer support chatbot for WeIntern Pvt Ltd.

    Intent recognition pipeline:
    1. Text preprocessing  (lowercase, strip punctuation, lemmatize, remove stopwords)
    2. TF-IDF vectorisation of all training utterances
    3. Cosine similarity against the user query vector
    4. Highest-scoring intent above a confidence threshold is selected
    5. Random response drawn from that intent's response pool

    Context management:
    - Tracks the last successful intent
    - Applies context boost for semantically related follow-up messages
    """

    CONFIDENCE_THRESHOLD = 0.15   # Minimum similarity score to accept an intent
    CONTEXT_BOOST        = 0.10   # Extra weight given to the previous intent

    # Intents that are "terminal" — after them context is cleared
    TERMINAL_INTENTS = {"goodbye"}

    # Related intent groups — same group gets a context boost
    RELATED_INTENTS = [
        {"refund", "cancellation", "payment"},
        {"order_status", "delivery"},
        {"greeting", "about", "services"},
        {"contact", "working_hours"},
    ]

    def __init__(self, intents_path: str = "intents.json") -> None:
        self.lemmatizer   = WordNetLemmatizer()
        self.stop_words   = set(stopwords.words("english"))
        self.intents      = []
        self.vectorizer   = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
        self.tfidf_matrix = None
        self.pattern_map  = []   # [(intent_tag, pattern_text)]
        self._load_intents(intents_path)
        self._build_tfidf_index()
        logger.info("WeInternChatbot initialised successfully.")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    def _load_intents(self, path: str) -> None:
        """Load and validate intents from JSON file."""
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            self.intents = data.get("intents", [])
            logger.info(f"Loaded {len(self.intents)} intents from '{path}'.")
        except FileNotFoundError:
            logger.error(f"Intents file not found: {path}")
            raise
        except json.JSONDecodeError as exc:
            logger.error(f"Invalid JSON in intents file: {exc}")
            raise

    def _preprocess(self, text: str) -> str:
        """
        Clean and normalise raw text:
        lowercase → remove punctuation → tokenise → lemmatise → remove stopwords
        """
        text = text.lower().strip()
        # Remove punctuation (keep spaces)
        text = text.translate(str.maketrans("", "", string.punctuation))
        # Tokenise
        tokens = word_tokenize(text)
        # Lemmatise and remove stopwords / single chars
        tokens = [
            self.lemmatizer.lemmatize(tok)
            for tok in tokens
            if tok not in self.stop_words and len(tok) > 1
        ]
        return " ".join(tokens)

    def _build_tfidf_index(self) -> None:
        """
        Build TF-IDF matrix from all training patterns.
        Each row corresponds to one (intent, pattern) pair.
        Patterns from the 'fallback' intent are excluded from the index.
        """
        for intent in self.intents:
            if intent["tag"] == "fallback":
                continue
            for pattern in intent["patterns"]:
                processed = self._preprocess(pattern)
                if processed:
                    self.pattern_map.append((intent["tag"], processed))

        if not self.pattern_map:
            raise ValueError("No training patterns found in intents.json")

        corpus = [text for _, text in self.pattern_map]
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
        logger.info(
            f"TF-IDF index built: {self.tfidf_matrix.shape[0]} patterns, "
            f"{self.tfidf_matrix.shape[1]} features."
        )

    def _get_related_group(self, tag: str) -> Optional[set]:
        """Return the relatedness group that contains 'tag', or None."""
        for group in self.RELATED_INTENTS:
            if tag in group:
                return group
        return None

    def _find_intent(
        self, query: str, context_intent: Optional[str] = None
    ) -> tuple[str, float]:
        """
        Vectorise the query and find the best matching intent via cosine
        similarity.  Returns (intent_tag, confidence_score).
        """
        processed = self._preprocess(query)
        if not processed:
            return "fallback", 0.0

        query_vec  = self.vectorizer.transform([processed])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        # Apply context boost
        if context_intent:
            ctx_group = self._get_related_group(context_intent)
            for idx, (tag, _) in enumerate(self.pattern_map):
                if tag == context_intent:
                    similarities[idx] += self.CONTEXT_BOOST
                elif ctx_group and tag in ctx_group:
                    similarities[idx] += self.CONTEXT_BOOST * 0.5

        best_idx   = int(np.argmax(similarities))
        best_score = float(similarities[best_idx])
        best_tag   = self.pattern_map[best_idx][0]

        logger.info(
            f"Query: '{query}' → Intent: '{best_tag}' "
            f"(confidence: {best_score:.3f})"
        )

        if best_score < self.CONFIDENCE_THRESHOLD:
            return "fallback", best_score
        return best_tag, best_score

    def _get_response(self, intent_tag: str) -> str:
        """Return a random response for the given intent tag."""
        for intent in self.intents:
            if intent["tag"] == intent_tag:
                return random.choice(intent["responses"])
        # Safety net — return fallback
        for intent in self.intents:
            if intent["tag"] == "fallback":
                return random.choice(intent["responses"])
        return "I'm having trouble right now. Please try again later."

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def respond(
        self,
        user_message: str,
        context_intent: Optional[str] = None
    ) -> dict:
        """
        Process a user message and return a structured response dict.

        Parameters
        ----------
        user_message : str
            Raw text from the user.
        context_intent : str | None
            The intent from the previous turn (for context awareness).

        Returns
        -------
        dict with keys:
            - response      : str   – bot reply
            - intent        : str   – detected intent tag
            - confidence    : float – similarity score (0-1)
            - timestamp     : str   – ISO-8601 timestamp
            - is_fallback   : bool  – True when no intent matched
        """
        if not isinstance(user_message, str) or not user_message.strip():
            return {
                "response"  : "Please type a message before sending.",
                "intent"    : "fallback",
                "confidence": 0.0,
                "timestamp" : datetime.utcnow().isoformat(),
                "is_fallback": True,
            }

        intent_tag, confidence = self._find_intent(
            user_message, context_intent
        )
        response = self._get_response(intent_tag)

        return {
            "response"  : response,
            "intent"    : intent_tag,
            "confidence": round(confidence, 4),
            "timestamp" : datetime.utcnow().isoformat(),
            "is_fallback": intent_tag == "fallback",
        }

    def get_intent_list(self) -> list[str]:
        """Return all intent tags (excluding fallback)."""
        return [i["tag"] for i in self.intents if i["tag"] != "fallback"]
