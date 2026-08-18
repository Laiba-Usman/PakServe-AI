import React from "react";
import SourcesPanel from "./SourcesPanel";
import "./MessageBubble.css";

/**
 * Format markdown text into React elements (headers, bold, lists, paragraphs).
 */
function renderFormattedText(text) {
  if (!text) return null;

  const lines = text.split("\n");
  const elements = [];
  let currentList = [];
  let listType = null; // 'ul' | 'ol'

  const flushList = () => {
    if (currentList.length > 0) {
      if (listType === "ol") {
        elements.push(<ol key={`ol-${elements.length}`}>{currentList}</ol>);
      } else {
        elements.push(<ul key={`ul-${elements.length}`}>{currentList}</ul>);
      }
      currentList = [];
      listType = null;
    }
  };

  const parseInline = (str) => {
    // Bold: **text**
    const parts = str.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return <strong key={i}>{part.slice(2, -2)}</strong>;
      }
      return part;
    });
  };

  lines.forEach((line, index) => {
    const trimmed = line.trim();

    if (!trimmed) {
      flushList();
      return;
    }

    // Horizontal Rule: ---
    if (trimmed === "---" || trimmed === "***") {
      flushList();
      elements.push(<hr key={`hr-${index}`} className="msg-hr" />);
      return;
    }

    // Headings: ### Heading or ## Heading
    if (trimmed.startsWith("### ")) {
      flushList();
      elements.push(<h4 key={`h4-${index}`} className="msg-h4">{parseInline(trimmed.slice(4))}</h4>);
      return;
    }
    if (trimmed.startsWith("## ")) {
      flushList();
      elements.push(<h3 key={`h3-${index}`} className="msg-h3">{parseInline(trimmed.slice(3))}</h3>);
      return;
    }
    if (trimmed.startsWith("# ")) {
      flushList();
      elements.push(<h2 key={`h2-${index}`} className="msg-h2">{parseInline(trimmed.slice(2))}</h2>);
      return;
    }

    // Unordered List: * or -
    if (trimmed.startsWith("* ") || trimmed.startsWith("- ")) {
      if (listType === "ol") flushList();
      listType = "ul";
      currentList.push(<li key={`li-${index}`}>{parseInline(trimmed.slice(2))}</li>);
      return;
    }

    // Ordered List: 1. 2.
    const orderedMatch = trimmed.match(/^(\d+)\.\s+(.*)$/);
    if (orderedMatch) {
      if (listType === "ul") flushList();
      listType = "ol";
      currentList.push(<li key={`li-${index}`}>{parseInline(orderedMatch[2])}</li>);
      return;
    }

    // Standard Paragraph
    flushList();
    elements.push(<p key={`p-${index}`} className="msg-p">{parseInline(trimmed)}</p>);
  });

  flushList();
  return elements;
}

export default function MessageBubble({ message }) {
  const isUser = message.sender === "user";

  if (isUser) {
    return (
      <div className="message-row user-row">
        <div className="user-bubble">
          <p>{message.text}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="message-row ai-row">
      <div className="ai-avatar">
        <span className="ai-avatar-badge">@</span>
      </div>

      <div className="ai-bubble-container">
        <div className="ai-bubble">
          <div className="ai-bubble-content">
            {renderFormattedText(message.text)}
          </div>

          {message.sources && message.sources.length > 0 && (
            <SourcesPanel sources={message.sources} />
          )}
        </div>
      </div>
    </div>
  );
}
