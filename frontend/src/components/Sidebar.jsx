import React, { useState } from "react";
import { MessageSquare, UploadCloud, FileText, BarChart3, Plus, Clock, X, ChevronDown, ChevronUp } from "lucide-react";
import "./Sidebar.css";

export default function Sidebar({ activeTab, setActiveTab, onNewChat, chatHistory = [], onRestoreSession, onDeleteSession }) {
  const [historyOpen, setHistoryOpen] = useState(false);

  const navItems = [
    { id: "chat", label: "Chat", icon: MessageSquare },
    { id: "upload", label: "Upload Document", icon: UploadCloud },
    { id: "manage", label: "Manage Documents", icon: FileText },
    { id: "analytics", label: "Analytics", icon: BarChart3 },
  ];

  const formatTime = (isoString) => {
    try {
      const date = new Date(isoString);
      const now = new Date();
      const diff = now - date;
      if (diff < 60000) return "Just now";
      if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
      if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
      return date.toLocaleDateString("en-PK", { day: "numeric", month: "short" });
    } catch {
      return "";
    }
  };

  return (
    <aside className="sidebar">
      {/* Brand Header */}
      <div className="sidebar-brand">
        <div className="brand-logo">
          <div className="logo-badge">
            <span className="crescent-emblem">☪</span>
          </div>
        </div>
        <div className="brand-info">
          <h2 className="brand-title">PakServe AI</h2>
          <span className="brand-subtitle">AI Assistant</span>
        </div>
      </div>

      {/* New Request Button */}
      <button className="new-request-btn" onClick={onNewChat}>
        <Plus size={18} strokeWidth={2.5} />
        <span>New Request</span>
      </button>

      {/* Primary Navigation */}
      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              className={`nav-item ${isActive ? "active" : ""}`}
              onClick={() => setActiveTab(item.id)}
            >
              <Icon size={18} className="nav-icon" />
              <span className="nav-label">{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Chat History Section */}
      <div className="chat-history-section">
        <button
          className="history-toggle-btn"
          onClick={() => setHistoryOpen(!historyOpen)}
        >
          <Clock size={15} className="history-icon" />
          <span className="history-label">Chat History</span>
          {chatHistory.length > 0 && (
            <span className="history-count">{chatHistory.length}</span>
          )}
          {historyOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </button>

        {historyOpen && (
          <div className="history-list">
            {chatHistory.length === 0 ? (
              <p className="history-empty">No previous chats yet</p>
            ) : (
              chatHistory.map((session) => (
                <div
                  key={session.id}
                  className="history-item"
                  onClick={() => onRestoreSession(session.id)}
                  title={session.title}
                >
                  <div className="history-item-content">
                    <span className="history-item-title">{session.title}</span>
                    <span className="history-item-time">{formatTime(session.timestamp)}</span>
                  </div>
                  <button
                    className="history-delete-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteSession(session.id);
                    }}
                    title="Remove from history"
                  >
                    <X size={13} />
                  </button>
                </div>
              ))
            )}
          </div>
        )}
      </div>

    </aside>
  );
}
