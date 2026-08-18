import React, { useState, useRef, useEffect } from "react";
import { Send, AlertCircle } from "lucide-react";
import MessageBubble from "./MessageBubble";
import { sendChatMessage } from "../api/client";
import "./ChatWindow.css";

const SUGGESTIONS = [
  "CNIC renewal requirements?",
  "Passport application process?",
  "Tax filing deadlines",
  "Driving license learner permit test rules",
];



export default function ChatWindow({ messages, setMessages }) {
  const [inputQuery, setInputQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSendMessage = async (queryToSend = null) => {
    const query = (queryToSend || inputQuery).trim();
    if (!query || isLoading) return;

    setErrorMsg(null);
    setInputQuery("");

    // Add user message
    const userMsg = {
      id: Date.now(),
      sender: "user",
      text: query,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const data = await sendChatMessage(query);

      const aiMsg = {
        id: Date.now() + 1,
        sender: "ai",
        text: data.answer || "I could not generate an answer based on the provided documents.",
        sources: data.sources || [],
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      console.error("Chat error:", err);
      const fallbackMsg = {
        id: Date.now() + 1,
        sender: "ai",
        text: "⚠️ **Connection Error**: Could not connect to the backend server (http://localhost:8000). Please verify the FastAPI backend is running.",
        sources: [],
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, fallbackMsg]);
      setErrorMsg("Failed to communicate with backend server.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="chat-window">

      {/* Main Chat Scroll Container */}
      <div className="chat-scroll-area">
        {messages.length === 0 ? (
          /* Welcome State */
          <div className="welcome-state">
            <div className="welcome-emblem">
              <div className="emblem-card">
                <span>☪</span>
              </div>
            </div>

            <h1 className="welcome-title">Assalam-o-Alaikum,<br />how can I help you today?</h1>
            
            <p className="welcome-subtitle">
              Your official AI assistant for navigating public services, document requirements, and civic procedures.
            </p>

            <div className="suggestions-container">
              {SUGGESTIONS.map((sug, idx) => (
                <button
                  key={idx}
                  className="suggestion-chip"
                  onClick={() => handleSendMessage(sug)}
                >
                  {sug}
                </button>
              ))}
            </div>
          </div>
        ) : (
          /* Messages List */
          <div className="messages-list">
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}

            {/* Thinking / Typing State */}
            {isLoading && (
              <div className="message-row ai-row">
                <div className="ai-avatar">
                  <span className="ai-avatar-badge">@</span>
                </div>
                <div className="ai-bubble typing-bubble">
                  <div className="typing-indicator">
                    <span className="dot"></span>
                    <span className="dot"></span>
                    <span className="dot"></span>
                  </div>
                  <span className="typing-label">
                    Retrieving verified procedural documents & thinking...
                  </span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Floating Bottom Input Bar */}
      <div className="chat-input-wrapper">
        {errorMsg && (
          <div className="chat-error-banner">
            <AlertCircle size={14} />
            <span>{errorMsg}</span>
          </div>
        )}

        <div className="chat-input-box">
          <input
            type="text"
            className="chat-text-input"
            placeholder="Ask about any government service..."
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            autoFocus
          />

          <div className="input-actions">
            <button
              className={`send-btn ${inputQuery.trim() ? "active" : ""}`}
              onClick={() => handleSendMessage()}
              disabled={!inputQuery.trim() || isLoading}
              aria-label="Send query"
            >
              <Send size={16} strokeWidth={2.5} />
            </button>
          </div>
        </div>

        <p className="disclaimer-text">
          AI responses may not reflect the latest regulatory changes. Always verify critical information.
        </p>
      </div>
    </div>
  );
}
