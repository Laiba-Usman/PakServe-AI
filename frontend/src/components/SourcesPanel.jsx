import React, { useState } from "react";
import { ChevronDown, ChevronUp, FileText, ExternalLink } from "lucide-react";
import "./SourcesPanel.css";

export default function SourcesPanel({ sources }) {
  const [isOpen, setIsOpen] = useState(false);

  if (!sources || sources.length === 0) return null;

  return (
    <div className="sources-container">
      <button
        className={`sources-toggle-btn ${isOpen ? "open" : ""}`}
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
      >
        <span className="info-icon">ⓘ</span>
        <span className="toggle-label">Sources ({sources.length})</span>
        {isOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
      </button>

      {isOpen && (
        <div className="sources-dropdown">
          <div className="sources-grid">
            {sources.map((source, index) => {
              const scorePercent = Math.round((source.similarity_score || 0) * 100);
              return (
                <div key={index} className="source-card">
                  <div className="source-card-header">
                    <div className="source-title-wrap">
                      <FileText size={14} className="source-file-icon" />
                      <span className="source-doc-name" title={source.doc_name}>
                        {source.doc_name}
                      </span>
                    </div>
                    <span className="source-category-tag">{source.category}</span>
                  </div>

                  <p className="source-snippet">
                    {source.text ? source.text.slice(0, 190).trim() + "..." : ""}
                  </p>

                  <div className="source-card-footer">
                    <span className="source-match-score">
                      Relevance: <strong>{scorePercent}%</strong>
                    </span>
                    <span className="source-chunk-id">Chunk #{source.chunk_id ?? index}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
