"""
tests/test_chatbot.py
=====================
Automated test suite for the WeIntern AI Chatbot.
Covers 31 diverse inputs across all 12 intents + edge cases.

Run with:  python tests/test_chatbot.py
"""

import sys
import os

# Add project root to path so we can import chatbot.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from chatbot import WeInternChatbot

# ---------------------------------------------------------------------------
# Test cases: (input_text, expected_intent, description)
# ---------------------------------------------------------------------------
TEST_CASES = [
    # --- Greetings ---
    ("hello",                        "greeting",      "Simple hello"),
    ("hey there!",                   "greeting",      "Casual greeting"),
    ("good morning",                 "greeting",      "Time-based greeting"),

    # --- About ---
    ("what is weintern?",            "about",         "Company inquiry"),
    ("tell me about yourself",       "about",         "Bot identity question"),

    # --- Services ---
    ("what services do you offer?",  "services",      "Services inquiry"),
    ("what programs are available",  "services",      "Program inquiry"),

    # --- Order Status ---
    ("track my application",         "order_status",  "Application tracking"),
    ("where is my order?",           "order_status",  "Order location query"),
    ("check my application status",  "order_status",  "Status check"),

    # --- Delivery ---
    ("when will i get my certificate?", "delivery",   "Certificate delivery"),
    ("how long does it take?",       "delivery",      "Processing time query"),
    ("delivery timeframe",           "delivery",      "Timeframe keyword"),

    # --- Refund ---
    ("i want a refund",              "refund",        "Direct refund request"),
    ("refund policy",                "refund",        "Policy inquiry"),
    ("how to get money back",        "refund",        "Informal refund request"),

    # --- Cancellation ---
    ("how do i cancel my order?",    "cancellation",  "Cancel order"),
    ("cancel my enrollment",         "cancellation",  "Cancel enrollment"),

    # --- Payment ---
    ("what payment methods are accepted?", "payment", "Payment methods"),
    ("my payment failed",            "payment",       "Payment failure"),
    ("how much does it cost?",       "payment",       "Pricing inquiry"),

    # --- Contact ---
    ("how do i contact support?",    "contact",       "Contact support"),
    ("what is your phone number?",   "contact",       "Phone number query"),

    # --- Working Hours ---
    ("what are your working hours?", "working_hours", "Hours inquiry"),
    ("are you open on sunday?",      "working_hours", "Weekend hours"),

    # --- Thanks ---
    ("thank you so much!",           "thanks",        "Thanks expression"),

    # --- Goodbye ---
    ("bye!",                         "goodbye",       "Simple farewell"),
    ("take care",                    "goodbye",       "Parting phrase"),

    # --- Fallback ---
    ("xyzabc random gibberish",      "fallback",      "Gibberish -- fallback"),
    ("12345",                        "fallback",      "Numbers only -- fallback"),
    ("that was really helpful",      "fallback",      "Implicit thanks -- fallback"),
]

# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------
def run_tests():
    print("=" * 72)
    print("  WeIntern AI Chatbot -- Automated Test Suite")
    print(f"  Total tests: {len(TEST_CASES)}")
    print("=" * 72)

    bot = WeInternChatbot(intents_path="intents.json")

    passed = 0
    failed = 0
    results = []

    for i, (user_msg, expected_intent, description) in enumerate(TEST_CASES, 1):
        result        = bot.respond(user_msg)
        actual_intent = result["intent"]
        confidence    = result["confidence"]
        ok            = actual_intent == expected_intent

        status = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        else:
            failed += 1

        results.append((i, status, description, user_msg, expected_intent, actual_intent, confidence))

    # --- Print results table ---
    header = f"{'#':<4} {'St':<5} {'Description':<35} {'Input':<32} {'Expected':<16} {'Got':<16} {'Conf':>6}"
    print(f"\n{header}")
    print("-" * len(header))

    for (i, status, desc, msg, exp, got, conf) in results:
        tick = "[OK]" if status == "PASS" else "[X] "
        print(
            f"{i:<4} {tick} {desc:<35} {msg[:30]:<32} {exp:<16} {got:<16} {conf:>6.3f}"
        )

    # --- Summary ---
    print("=" * 72)
    pct = (passed / len(TEST_CASES)) * 100
    print(f"  Results: {passed} passed / {failed} failed  ({pct:.1f}% accuracy)")
    print("=" * 72)

    if failed > 0:
        print("\nFailed tests:")
        for (i, status, desc, msg, exp, got, conf) in results:
            if status == "FAIL":
                print(f"  [{i}] '{msg}' -> expected '{exp}', got '{got}' (conf={conf:.3f})")

    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)