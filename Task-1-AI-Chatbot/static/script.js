/**
 * script.js — WeIntern AI Chatbot Frontend
 */
"use strict";

const API_CHAT    = "/api/chat";
const API_CLEAR   = "/api/clear";
const API_HISTORY = "/api/history";

const state = { isTyping: false };

const messagesArea    = document.getElementById("messages-area");
const userInput       = document.getElementById("user-input");
const sendBtn         = document.getElementById("send-btn");
const clearBtn        = document.getElementById("clear-btn");
const typingIndicator = document.getElementById("typing-indicator");
const charCounter     = document.getElementById("char-counter");

/* --- Utilities --- */
function formatTime(isoStr) {
  const d = isoStr ? new Date(isoStr + "Z") : new Date();
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function autoResize(el) {
  el.style.height = "auto";
  el.style.height = el.scrollHeight + "px";
}

function scrollToBottom() {
  messagesArea.scrollTop = messagesArea.scrollHeight;
}

function escapeHTML(str) {
  return str
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

/* --- SVG Icons --- */
const BOT_ICON_SVG = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16"><rect x="3" y="11" width="18" height="10" rx="2"></rect><circle cx="12" cy="5" r="2"></circle><path d="M12 7v4"></path><line x1="8" y1="16" x2="8.01" y2="16"></line><line x1="16" y1="16" x2="16.01" y2="16"></line></svg>`;
const USER_ICON_SVG = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="15" height="15"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>`;

/* --- Render --- */
function appendMessage(role, text, meta = {}) {
  const row = document.createElement("div");
  row.classList.add("msg-row", role);

  const avatar = document.createElement("div");
  avatar.classList.add("msg-avatar");
  avatar.setAttribute("aria-hidden", "true");
  avatar.innerHTML = role === "bot" ? BOT_ICON_SVG : USER_ICON_SVG;

  const content = document.createElement("div");
  content.classList.add("msg-content");

  const bubble = document.createElement("div");
  bubble.classList.add("msg-bubble");
  if (meta.is_fallback) bubble.classList.add("is-fallback");
  bubble.innerHTML = escapeHTML(text).replace(/\n/g, "<br>");

  const time = document.createElement("span");
  time.classList.add("msg-time");
  time.textContent = formatTime(meta.timestamp || null);

  content.appendChild(bubble);
  content.appendChild(time);
  row.appendChild(avatar);
  row.appendChild(content);
  messagesArea.appendChild(row);
  scrollToBottom();
}

function renderWelcomeBanner() {
  const banner = document.createElement("div");
  banner.classList.add("welcome-banner");
  banner.innerHTML = `
    <div class="welcome-icon" aria-hidden="true">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="28" height="28" style="color:#ffffff;">
        <rect x="3" y="11" width="18" height="10" rx="2"></rect>
        <circle cx="12" cy="5" r="2"></circle>
        <path d="M12 7v4"></path>
        <line x1="8" y1="16" x2="8.01" y2="16"></line>
        <line x1="16" y1="16" x2="16.01" y2="16"></line>
      </svg>
    </div>
    <h2>Welcome to WeIntern Support</h2>
    <p>I'm your intelligent customer support assistant. How can I help you today?</p>
    <div class="chips" role="group" aria-label="Suggested questions">
      <button class="chip" data-msg="What services does WeIntern offer?">🎓 Our Services</button>
      <button class="chip" data-msg="How can I track my application status?">📦 Track Application</button>
      <button class="chip" data-msg="What is your refund policy?">💰 Refund Policy</button>
      <button class="chip" data-msg="How do I contact customer support?">📞 Contact Support</button>
    </div>
  `;

  // Attach click events to suggestion chips
  banner.querySelectorAll(".chip").forEach(chip => {
    chip.addEventListener("click", () => {
      const msg = chip.dataset.msg;
      if (!msg || state.isTyping) return;
      userInput.value = msg;
      autoResize(userInput);
      charCounter.textContent = `${msg.length} / 500`;
      sendMessage();
    });
  });

  messagesArea.appendChild(banner);
  scrollToBottom();
}

/* --- API --- */
async function sendMessage() {
  const text = userInput.value.trim();
  if (!text || state.isTyping) return;

  appendMessage("user", text);
  userInput.value = "";
  autoResize(userInput);
  charCounter.textContent = "0 / 500";
  sendBtn.disabled = true;
  state.isTyping   = true;

  // Immediately display the typing indicator
  typingIndicator.hidden = false;
  scrollToBottom();

  const minTypingDuration = new Promise(resolve => setTimeout(resolve, 350));

  try {
    const [res] = await Promise.all([
      fetch(API_CHAT, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ message: text }),
      }),
      minTypingDuration
    ]);

    typingIndicator.hidden = true;

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      appendMessage("bot", `⚠️ Error: ${err.error || "Something went wrong. Please try again."}`);
      return;
    }

    const data = await res.json();
    appendMessage("bot", data.response, { timestamp: data.timestamp, is_fallback: data.is_fallback });

  } catch (e) {
    typingIndicator.hidden = true;
    appendMessage("bot", "⚠️ Network error. Check your connection and try again.");
    console.error("Chat error:", e);
  } finally {
    state.isTyping   = false;
    sendBtn.disabled = false;
    userInput.focus();
  }
}

async function clearChat() {
  try { await fetch(API_CLEAR, { method: "POST" }); } catch (_) {}
  messagesArea.innerHTML = "";
  renderWelcomeBanner();
  userInput.focus();
}

/* --- Events --- */
sendBtn.addEventListener("click", sendMessage);

userInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});

userInput.addEventListener("input", () => {
  autoResize(userInput);
  const len = userInput.value.length;
  charCounter.textContent = `${len} / 500`;
  charCounter.style.color = len > 450 ? "#ef4444" : "";
});

clearBtn.addEventListener("click", clearChat);

document.querySelectorAll(".topic-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const msg = btn.dataset.msg;
    if (!msg || state.isTyping) return;
    userInput.value = msg;
    autoResize(userInput);
    charCounter.textContent = `${msg.length} / 500`;
    sendMessage();
  });
});

/* --- Init --- */
(async function init() {
  renderWelcomeBanner();
  try {
    const res = await fetch(API_HISTORY);
    if (res.ok) {
      const { history } = await res.json();
      if (history && history.length > 0) {
        messagesArea.innerHTML = "";
        history.forEach(e => appendMessage(e.role, e.text, { timestamp: e.timestamp, is_fallback: e.is_fallback }));
      }
    }
  } catch (_) {}
  userInput.focus();
})();