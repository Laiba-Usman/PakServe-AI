import React, { useState, useEffect } from "react";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import UploadPanel from "./components/UploadPanel";
import ManagePanel from "./components/ManagePanel";
import AnalyticsPanel from "./components/AnalyticsPanel";
import "./styles/theme.css";

const ACTIVE_CHAT_KEY = "pakserve_active_chat";
const HISTORY_KEY = "pakserve_chat_sessions";

function loadActiveChat() {
  try {
    const stored = localStorage.getItem(ACTIVE_CHAT_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      if (Array.isArray(parsed) && parsed.length > 0) return parsed;
    }
  } catch (e) {
    console.warn("Failed to load active chat:", e);
  }
  return [];
}

function loadChatHistory() {
  try {
    const stored = localStorage.getItem(HISTORY_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      if (Array.isArray(parsed)) return parsed;
    }
  } catch (e) {
    console.warn("Failed to load chat history:", e);
  }
  return [];
}

function saveChatHistory(sessions) {
  try {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(sessions));
  } catch (e) {
    console.warn("Failed to save chat history:", e);
  }
}

export default function App() {
  const [activeTab, setActiveTab] = useState("chat");
  const [messages, setMessages] = useState(loadActiveChat);
  const [chatHistory, setChatHistory] = useState(loadChatHistory);

  // Persist active chat to localStorage whenever messages change
  useEffect(() => {
    try {
      localStorage.setItem(ACTIVE_CHAT_KEY, JSON.stringify(messages));
    } catch (e) {
      console.warn("Failed to save active chat:", e);
    }
  }, [messages]);

  // Handle "+ New Request": save current chat to history, then clear
  const handleNewChat = () => {
    // Only save to history if there are messages in the current chat
    if (messages.length > 0) {
      const firstUserMsg = messages.find((m) => m.sender === "user");
      const title = firstUserMsg
        ? firstUserMsg.text.slice(0, 60) + (firstUserMsg.text.length > 60 ? "..." : "")
        : "Untitled Chat";

      const session = {
        id: Date.now(),
        title,
        timestamp: new Date().toISOString(),
        messages: [...messages],
      };

      const updatedHistory = [session, ...chatHistory].slice(0, 20); // Keep last 20
      setChatHistory(updatedHistory);
      saveChatHistory(updatedHistory);
    }

    setActiveTab("chat");
    setMessages([]);
    localStorage.removeItem(ACTIVE_CHAT_KEY);
  };

  // Restore a past chat session from history
  const handleRestoreSession = (sessionId) => {
    const session = chatHistory.find((s) => s.id === sessionId);
    if (session) {
      // Save current active chat to history first (if non-empty)
      if (messages.length > 0) {
        const firstUserMsg = messages.find((m) => m.sender === "user");
        const title = firstUserMsg
          ? firstUserMsg.text.slice(0, 60) + (firstUserMsg.text.length > 60 ? "..." : "")
          : "Untitled Chat";

        const currentSession = {
          id: Date.now(),
          title,
          timestamp: new Date().toISOString(),
          messages: [...messages],
        };

        const updatedHistory = [currentSession, ...chatHistory.filter((s) => s.id !== sessionId)].slice(0, 20);
        setChatHistory(updatedHistory);
        saveChatHistory(updatedHistory);
      } else {
        // Just remove the restored session from history
        const updatedHistory = chatHistory.filter((s) => s.id !== sessionId);
        setChatHistory(updatedHistory);
        saveChatHistory(updatedHistory);
      }

      setMessages(session.messages);
      setActiveTab("chat");
    }
  };

  // Delete a session from history
  const handleDeleteSession = (sessionId) => {
    const updatedHistory = chatHistory.filter((s) => s.id !== sessionId);
    setChatHistory(updatedHistory);
    saveChatHistory(updatedHistory);
  };

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onNewChat={handleNewChat}
        chatHistory={chatHistory}
        onRestoreSession={handleRestoreSession}
        onDeleteSession={handleDeleteSession}
      />

      {/* Main Content Viewport */}
      <main className="main-content">
        {activeTab === "chat" && (
          <ChatWindow
            messages={messages}
            setMessages={setMessages}
          />
        )}

        {activeTab === "upload" && (
          <UploadPanel
            onUploadSuccess={() => {}}
          />
        )}

        {activeTab === "manage" && (
          <ManagePanel />
        )}

        {activeTab === "analytics" && (
          <AnalyticsPanel />
        )}
      </main>
    </div>
  );
}
