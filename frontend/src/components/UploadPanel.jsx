import React, { useState, useRef } from "react";
import { UploadCloud, FileText, CheckCircle2, Clock, AlertCircle, Sparkles } from "lucide-react";
import { uploadDocument } from "../api/client";
import "./UploadPanel.css";

const CATEGORY_OPTIONS = [
  "NADRA",
  "Passport",
  "Driving License",
  "Tax (FBR)",
  "Vehicle Registration",
  "Civil Documents",
  "General",
];

export default function UploadPanel({ onUploadSuccess }) {
  const [selectedCategory, setSelectedCategory] = useState("General");
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [statusMessage, setStatusMessage] = useState(null);
  const [recentUploads, setRecentUploads] = useState([
    {
      id: 1,
      name: "nadra_cnic_renewal.txt",
      size: "4.1 KB",
      time: "Today, 10:42 AM",
      category: "NADRA",
      status: "Processed",
    },
    {
      id: 2,
      name: "vehicle_registration_new.txt",
      size: "4.8 KB",
      time: "Yesterday, 14:15 PM",
      category: "Vehicle Registration",
      status: "Processed",
    },
    {
      id: 3,
      name: "fbr_tax_filing_salaried.txt",
      size: "4.7 KB",
      time: "Aug 15, 09:00 AM",
      category: "Tax (FBR)",
      status: "Processed",
    },
  ]);
  const fileInputRef = useRef(null);

  const handleFileSelect = async (file) => {
    if (!file) return;

    if (!file.name.endsWith(".txt")) {
      setStatusMessage({
        type: "error",
        text: "Please upload a plain text (.txt) document for knowledge base indexing.",
      });
      return;
    }

    setIsUploading(true);
    setStatusMessage(null);

    try {
      const res = await uploadDocument(file, selectedCategory);

      // Add to recent list
      const newEntry = {
        id: Date.now(),
        name: file.name,
        size: `${(file.size / 1024).toFixed(1)} KB`,
        time: "Just now",
        category: selectedCategory,
        status: "Processed",
      };

      setRecentUploads((prev) => [newEntry, ...prev]);
      setStatusMessage({
        type: "success",
        text: `✓ Successfully indexed '${file.name}' with ${res.chunks_added} chunks into ChromaDB!`,
      });

      if (onUploadSuccess) onUploadSuccess();
    } catch (err) {
      console.error("Upload failed:", err);
      setStatusMessage({
        type: "error",
        text: `Upload failed: ${err.message}`,
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="upload-screen">
      {/* Header */}
      <div className="screen-header">
        <h1 className="screen-title">Secure Document Upload</h1>
        <p className="screen-subtitle">
          Upload official civic documents for AI processing, verification, and procedural indexing.
        </p>
      </div>

      {/* Category selector */}
      <div className="upload-category-selector">
        <label className="selector-label">Target Civic Category:</label>
        <div className="category-pill-group">
          {CATEGORY_OPTIONS.map((cat) => (
            <button
              key={cat}
              className={`cat-pill ${selectedCategory === cat ? "active" : ""}`}
              onClick={() => setSelectedCategory(cat)}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Drag & Drop Box */}
      <div
        className={`dropzone-box ${isDragging ? "dragging" : ""} ${isUploading ? "uploading" : ""}`}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          type="file"
          ref={fileInputRef}
          accept=".txt"
          style={{ display: "none" }}
          onChange={(e) => {
            if (e.target.files?.length) handleFileSelect(e.target.files[0]);
          }}
        />

        <div className="dropzone-icon-wrap">
          <UploadCloud size={30} className="cloud-icon" />
        </div>

        <h3 className="dropzone-heading">
          {isUploading ? "Embedding & Indexing..." : "Drag and drop files here"}
        </h3>
        <p className="dropzone-sub">
          {isUploading ? "Generating vectors for ChromaDB..." : "or click to browse your device"}
        </p>
        <span className="dropzone-support">
          Supported format: Plain text (.txt procedural documents, max 15MB)
        </span>
      </div>

      {/* Status feedback */}
      {statusMessage && (
        <div className={`status-banner ${statusMessage.type}`}>
          {statusMessage.type === "success" ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
          <span>{statusMessage.text}</span>
        </div>
      )}

      {/* Recently Uploaded Section */}
      <div className="recent-uploads-section">
        <h2 className="section-title">Recently Uploaded</h2>

        <div className="recent-list">
          {recentUploads.map((item) => (
            <div key={item.id} className="recent-card">
              <div className="recent-left">
                <div className="file-icon-box">
                  <FileText size={18} />
                </div>
                <div className="file-meta">
                  <span className="file-name">{item.name}</span>
                  <span className="file-sub">
                    {item.time} • {item.size}
                  </span>
                </div>
              </div>

              <div className="recent-right">
                <span className="badge badge-rust">{item.category}</span>
                <span className="status-indicator">
                  <CheckCircle2 size={14} className="status-icon success" />
                  <span className="status-text">{item.status}</span>
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
