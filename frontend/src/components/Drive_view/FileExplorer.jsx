import React, { useState, useEffect } from "react";
import {
  Search,
  Upload,
  MessageSquare,
  Download,
  Trash2,
  X,
  Bot,
} from "lucide-react";
import "./FileExplorer.css";

const FileExplorer = ({
  selectedFolder,
  searchQuery,
  onSearchChange,
  onAIChatToggle,
  onFileSelect,
}) => {
  const [files, setFiles] = useState([]);
  const [selectedPDF, setSelectedPDF] = useState(null);
  const [pdfBlobUrl, setPdfBlobUrl] = useState(null);
  const [searchMode, setSearchMode] = useState("search");
  const [summaries, setSummaries] = useState([]);
  const [isLoadingSummaries, setIsLoadingSummaries] = useState(false);

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        const res = await fetch("http://localhost:5000/documents/list");
        const data = await res.json();
        setFiles(data);
      } catch (err) {
        console.error("Failed to load files:", err);
      }
    };
    fetchFiles();
  }, []);

  const mockSummaries = [
    {
      id: "1",
      title: "AI Research.pdf",
      summary:
        "This document presents breakthroughs in AI models and benchmarks their performance on vision-language tasks.",
      pages: 18,
      lastModified: "2 days ago",
    },
    {
      id: "2",
      title: "Project Plan.pdf",
      summary:
        "Outlines the roadmap and timelines for launching the new analytics dashboard.",
      pages: 10,
      lastModified: "1 week ago",
    },
  ];

const handleAskAI = async () => {
  setSearchMode("ai");
  if (searchQuery.trim().length > 0) {
    setIsLoadingSummaries(true);
    try {
      const res = await fetch("http://localhost:5000/agent/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: searchQuery }),
      });
      const data = await res.json();

      if (data.error) {
        console.error("AI Error:", data.error);
        setSummaries([]);
      } else if (data.action === "summarize_folder") {
        setSummaries(
          data.summaries.map((s, idx) => ({
            id: idx,
            title: s.file,
            summary: s.summary,
            pages: "",
            lastModified: "N/A",
          }))
        );
      } else if (data.action === "summarize_file") {
        setSummaries([
          {
            id: 1,
            title: data.summary.file,
            summary: data.summary.summary,
            pages: "",
            lastModified: "N/A",
          },
        ]);
      } else if (data.action === "file_topic_lookup") {
        setSummaries(
          data.results.map((r, idx) => ({
            id: idx,
            title: r.file,
            summary: r.summary,
            pages: r.num_relevant_chunks || "?",
            lastModified: "N/A",
          }))
        );
      } else {
        console.log("Raw AI Response:", data);
        setSummaries([]);
      }
    } catch (err) {
      console.error("AI request failed:", err);
      setSummaries([]);
    } finally {
      setIsLoadingSummaries(false);
    }
  }
};


  const handleSearchFiles = () => {
    setSearchMode("search");
    setSummaries([]);
    setIsLoadingSummaries(false);
  };

  const getFolderPath = (folderId) => {
    const folderMap = {
      "1-1": "Research Papers / Machine Learning",
      "2-1": "Legal Documents / Contracts",
      "3": "Reports",
    };
    return folderMap[folderId] || "All Files";
  };

  const filteredFiles = files.filter(
    (file) =>
      (!selectedFolder || file.folderId === selectedFolder) &&
      file.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleFileClick = async (file) => {
    try {
      const res = await fetch(
        `http://localhost:5000/documents/view/${file.relative_path}`
      );
      if (!res.ok) throw new Error("Failed to fetch PDF");
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      setPdfBlobUrl(url);
      setSelectedPDF(file);
      onFileSelect(file);
    } catch (err) {
      console.error("Error loading PDF:", err);
    }
  };

  const handleClosePDF = () => {
    if (pdfBlobUrl) {
      URL.revokeObjectURL(pdfBlobUrl);
    }
    setPdfBlobUrl(null);
    setSelectedPDF(null);
  };

  const handleInputChange = (e) => {
    onSearchChange(e.target.value);
    if (searchMode === "search") {
      setSummaries([]);
      setIsLoadingSummaries(false);
    }
  };

  const SummaryCard = ({ summary }) => (
    <div className="summary-card">
      <div className="summary-header">
        <div>
          <strong>{summary.title}</strong>
          <small>
            {summary.pages} pages • {summary.lastModified}
          </small>
        </div>
      </div>
      <p>{summary.summary}</p>
    </div>
  );

  return (
    <div className="file-explorer-wrapper">
      {/* Header */}
      <div className="file-header">
        <div>
          <h2>{getFolderPath(selectedFolder)}</h2>
          {selectedFolder && (
            <div className="file-count">
              <small>{filteredFiles.length} files</small>
            </div>
          )}
        </div>
        <button className="ai-button" onClick={onAIChatToggle}>
          <MessageSquare size={16} />
          <span>AI Assistant</span>
        </button>
      </div>

      {/* Search and Toggle Buttons */}
      <div className="file-search-bar full">
        <Search size={16} className="search-icon" />
        <input
          type="text"
          value={searchQuery}
          onChange={handleInputChange}
          placeholder={
            searchMode === "ai"
              ? "Ask AI about your documents..."
              : "Search files..."
          }
        />
        <button
          className={`toggle-btn ${searchMode === "search" ? "active" : ""}`}
          onClick={handleSearchFiles}
        >
          <Search size={14} /> Search Files
        </button>
        <button
          className={`toggle-btn ${searchMode === "ai" ? "active" : ""}`}
          onClick={handleAskAI}
        >
          <Bot size={14} /> Ask AI
        </button>
      </div>

      {/* Viewer or File Grid */}
      {selectedPDF && pdfBlobUrl ? (
        <div className="pdf-viewer-container">
          <div className="viewer-toolbar">
            <span>{selectedPDF.name}</span>
            <button onClick={handleClosePDF}>
              <X size={18} />
            </button>
          </div>
          <iframe
            src={pdfBlobUrl}
            title={selectedPDF.name}
            className="pdf-iframe"
          />
        </div>
      ) : searchMode === "ai" ? (
        <div className="summary-section">
          <h3>AI Generated Summaries</h3>
          {isLoadingSummaries ? (
            <p className="loading-msg">Generating summaries...</p>
          ) : summaries.length > 0 ? (
            <div className="summary-list">
              {summaries.map((summary) => (
                <SummaryCard key={summary.id} summary={summary} />
              ))}
            </div>
          ) : (
            <p className="no-summary-msg">Type a query to get summaries.</p>
          )}
        </div>
      ) : (
        <div className="file-grid">
          {filteredFiles.length ? (
            filteredFiles.map((file) => (
              <div
                key={file.id}
                className="file-card"
                onClick={() => handleFileClick(file)}
              >
                <div className="file-info">
                  <div className="file-icon">PDF</div>
                  <div className="file-meta">
                    <strong>{file.name}</strong>
                    <small>
                      {file.size} • Uploaded {file.uploadDate}
                    </small>
                  </div>
                </div>
                <div className="file-actions">
                  <Download size={14} />
                  <Trash2 size={14} />
                </div>
              </div>
            ))
          ) : (
            <div className="file-empty">
              <Upload size={48} />
              <p>No files found</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FileExplorer;
