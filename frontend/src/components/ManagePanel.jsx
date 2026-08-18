import React, { useState, useEffect } from "react";
import { Search, Trash2, FileText, Users, CreditCard, Shield, Car, Landmark, AlertTriangle, RefreshCw } from "lucide-react";
import { listDocuments, deleteDocument } from "../api/client";
import "./ManagePanel.css";

// Helper to choose relevant icon based on category
function getCategoryIcon(category) {
  const cat = (category || "").toLowerCase();
  if (cat.includes("nadra") || cat.includes("id")) return Users;
  if (cat.includes("passport")) return Shield;
  if (cat.includes("driving") || cat.includes("license")) return CreditCard;
  if (cat.includes("tax") || cat.includes("fbr")) return Landmark;
  if (cat.includes("vehicle")) return Car;
  return FileText;
}

// Generate friendly descriptions for standard documents
function getDocDescription(docName) {
  const name = docName.toLowerCase();
  if (name.includes("cnic_new")) return "Fresh Computerized National Identity Card application rules & eligibility.";
  if (name.includes("cnic_renewal")) return "Identity card expiration renewal guidelines, fees, and verification rules.";
  if (name.includes("cnic_correction")) return "Data modification, address update, and spelling correction procedures.";
  if (name.includes("child_registration")) return "Child Registration Certificate (B-Form) requirements for minors under 18.";
  if (name.includes("family_registration")) return "Family Registration Certificate (FRC) by birth & marriage.";
  if (name.includes("passport_fresh")) return "First-time Machine Readable Passport application at Regional Passport Offices.";
  if (name.includes("passport_renewal")) return "Passport renewal steps, online portal submission, and timelines.";
  if (name.includes("passport_lost")) return "Police report and duplicate passport replacement protocols.";
  if (name.includes("passport_urgent")) return "Full MRP & E-Passport fee schedule across normal and urgent tracks.";
  if (name.includes("learner_permit")) return "Learner driving permit requirements, 42-day practice period rules.";
  if (name.includes("driving_license_new")) return "Permanent license theory sign test & practical field driving track rules.";
  if (name.includes("driving_license_renewal")) return "Renewal grace period, medical fitness, and penalty tiers.";
  if (name.includes("international_permit")) return "UN Convention 1-year International Driving Permit booklet rules.";
  if (name.includes("ntn_registration")) return "Free online 13-digit CNIC NTN registration on FBR IRIS 2.0.";
  if (name.includes("salaried")) return "Annual income tax return filing & wealth statement for salaried filers.";
  if (name.includes("business")) return "Sole proprietorship & freelancer export tax return filing rules.";
  if (name.includes("late_filing")) return "Late filing penalties and Section 182A ATL surcharge activation.";
  if (name.includes("vehicle_registration_new")) return "New motor vehicle factory invoice registration and token taxes.";
  if (name.includes("ownership_transfer")) return "NADRA biometric vehicle ownership transfer and seller/buyer verification.";
  if (name.includes("number_plate")) return "Universal computerized embossed vehicle number plates replacement.";
  if (name.includes("domicile")) return "District domicile certificate issuance, domicile rules, and merit quotas.";
  if (name.includes("birth_certificate")) return "Union Council computerized NADRA CRMS birth registration certificate.";
  if (name.includes("marriage_registration")) return "Computerized Nikkah marriage registration certificate (MRC).";
  if (name.includes("faqs")) return "Cross-department office timings, mega centers, and 1Link PSID guidelines.";
  return "Official civic procedural document for public services navigation.";
}

export default function ManagePanel() {
  const [documents, setDocuments] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deletingDoc, setDeletingDoc] = useState(null);
  const [confirmingDoc, setConfirmingDoc] = useState(null);

  const fetchDocs = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await listDocuments();
      setDocuments(data || []);
    } catch (err) {
      console.error("Failed to load documents:", err);
      setError("Could not load documents from vector database. Make sure backend is running.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  const handleDeleteClick = (docName) => {
    setConfirmingDoc(docName);
  };

  const handleDeleteConfirm = async (docName) => {
    setConfirmingDoc(null);
    setDeletingDoc(docName);
    try {
      await deleteDocument(docName);
      setDocuments((prev) => prev.filter((d) => d.doc_name !== docName));
    } catch (err) {
      alert(`Delete failed: ${err.message}`);
    } finally {
      setDeletingDoc(null);
    }
  };

  const handleDeleteCancel = () => {
    setConfirmingDoc(null);
  };

  // Filter documents by search term
  const filteredDocs = documents.filter((d) => {
    const q = searchQuery.toLowerCase();
    return (
      d.doc_name.toLowerCase().includes(q) ||
      d.category.toLowerCase().includes(q) ||
      getDocDescription(d.doc_name).toLowerCase().includes(q)
    );
  });

  // Group by category
  const groupedDocs = filteredDocs.reduce((acc, doc) => {
    const cat = doc.category || "General";
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(doc);
    return acc;
  }, {});

  return (
    <div className="manage-screen">
      {/* Header with Search Bar */}
      <div className="manage-header">
        <div className="manage-title-area">
          <h1 className="screen-title">Document Repository</h1>
          <p className="screen-subtitle">
            Manage and review uploaded civic documents across categories.
          </p>
        </div>

        <div className="manage-search-box">
          <Search size={16} className="search-icon" />
          <input
            type="text"
            className="manage-search-input"
            placeholder="Search Documents"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* Content Area */}
      {isLoading ? (
        <div className="manage-loading">
          <RefreshCw size={24} className="spin-icon" />
          <span>Loading documents from ChromaDB vector repository...</span>
        </div>
      ) : error ? (
        <div className="manage-error">
          <AlertTriangle size={20} />
          <span>{error}</span>
          <button className="btn-primary" onClick={fetchDocs}>Retry</button>
        </div>
      ) : Object.keys(groupedDocs).length === 0 ? (
        <div className="manage-empty">
          <FileText size={40} className="empty-icon" />
          <h3>No documents found</h3>
          <p>Try refining your search query or upload new documents.</p>
        </div>
      ) : (
        <div className="category-sections">
          {Object.entries(groupedDocs).map(([category, docs]) => (
            <div key={category} className="category-group">
              <div className="category-group-header">
                <h2 className="category-group-title">{category}</h2>
                <span className="badge badge-rust">{docs.length} {docs.length === 1 ? "Item" : "Items"}</span>
              </div>

              <div className="documents-grid">
                {docs.map((doc) => {
                  const Icon = getCategoryIcon(doc.category);
                  const isBeingDeleted = deletingDoc === doc.doc_name;
                  const isConfirming = confirmingDoc === doc.doc_name;

                  return (
                    <div key={doc.doc_name} className={`doc-card ${isBeingDeleted ? "deleting" : ""}`}>
                      {/* Inline Confirm Overlay */}
                      {isConfirming && (
                        <div className="delete-confirm-overlay">
                          <p className="confirm-text">Are you sure you want to delete?</p>
                          <div className="confirm-actions">
                            <button className="confirm-yes-btn" onClick={() => handleDeleteConfirm(doc.doc_name)}>Yes, Delete</button>
                            <button className="confirm-no-btn" onClick={handleDeleteCancel}>Cancel</button>
                          </div>
                        </div>
                      )}

                      <div className="doc-card-top">
                        <div className="doc-icon-box">
                          <Icon size={18} />
                        </div>
                        <button
                          className="doc-delete-btn"
                          title={`Delete ${doc.doc_name}`}
                          onClick={() => handleDeleteClick(doc.doc_name)}
                          disabled={isBeingDeleted}
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>

                      <div className="doc-card-body">
                        <h3 className="doc-card-title" title={doc.doc_name}>
                          {doc.doc_name}
                        </h3>
                        <p className="doc-card-desc">
                          {getDocDescription(doc.doc_name)}
                        </p>
                      </div>

                      <div className="doc-card-footer">
                        <div className="doc-tags">
                          <span className="badge badge-rust">{doc.category}</span>
                          <span className="badge badge-green">{doc.chunk_count} Chunks</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
