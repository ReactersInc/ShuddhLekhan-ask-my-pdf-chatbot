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
import { authFetchJson, authFetch } from "../../utils/authFetch";

const FileExplorer = ({
  selectedFolder,
  searchQuery,
  onSearchChange,
  onAIChatToggle,
  onFileSelect,
}) => {
  const [files, setFiles] = useState([]); // Initialize as empty array
  const [selectedPDF, setSelectedPDF] = useState(null);
  const [pdfBlobUrl, setPdfBlobUrl] = useState(null);
  const [searchMode, setSearchMode] = useState("search");
  const [summaries, setSummaries] = useState([]);
  const [isLoadingSummaries, setIsLoadingSummaries] = useState(false);

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        let url = '/documents/list';
        // Add folder filter if selectedFolder is provided
        if (selectedFolder) {
          url += `?folder=${encodeURIComponent(selectedFolder)}`;
        }
        
        console.log('Fetching files with URL:', url, 'selectedFolder:', selectedFolder);
        
        const data = await authFetchJson(url);
        console.log('Files response:', data);
        // Backend returns { status: 'success', pdfs: [...], files: [...], total_files: 5 }
        // Extract the files array from the response (check both pdfs and files)
        const fileList = data?.pdfs || data?.files || [];
        if (Array.isArray(fileList)) {
          console.log('Setting files:', fileList.length, 'files found for folder:', selectedFolder);
          setFiles(fileList);
        } else {
          console.warn('Unexpected response format:', data);
          setFiles([]); // Fallback to empty array
        }
      } catch (err) {
        console.error("Failed to load files:", err);
        setFiles([]); // Ensure files is always an array
      }
    };
    fetchFiles();
  }, [selectedFolder]); // Re-fetch when selectedFolder changes

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

  const handleAskAI = () => {
    setSearchMode("ai");
    if (searchQuery.trim().length > 0) {
      setIsLoadingSummaries(true);
      setTimeout(() => {
        setSummaries(mockSummaries);
        setIsLoadingSummaries(false);
      }, 1200);
    }
  };

  const handleSearchFiles = () => {
    setSearchMode("search");
    setSummaries([]);
    setIsLoadingSummaries(false);
  };

  const getFolderPath = () => {
    if (selectedFolder) {
      return `${selectedFolder} (${filteredFiles.length} files)`;
    }
    return `All Files (${filteredFiles.length} files)`;
  };

  const filteredFiles = Array.isArray(files) ? files.filter(
    (file) =>
      (file.filename || file.original_filename || '').toLowerCase().includes(searchQuery.toLowerCase())
  ) : [];

  const handleFileClick = async (file) => {
    try {
      console.log('File clicked:', file);
      
      // Check if file is PDF first
      const fileName = file.original_filename || file.filename || file.name || '';
      if (!fileName.toLowerCase().endsWith('.pdf')) {
        alert('This file is not a PDF document and cannot be viewed in the PDF viewer.');
        return;
      }
      
      // Handle both legacy (relative_path) and new (file_path) field names
      const filePath = file.relative_path || file.file_path;
      console.log('File path for viewing:', filePath);
      
      const response = await authFetch(`/documents/view/${filePath}`);
      console.log('PDF fetch response:', response);
      
      if (response.status === 403) {
        throw new Error("You don't have permission to view this file");
      } else if (response.status === 400) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || "File is not a valid PDF document");
      } else if (!response.ok) {
        throw new Error(`Failed to fetch PDF: ${response.status} ${response.statusText}`);
      }
      
      const blob = await response.blob();
      console.log('PDF blob created, size:', blob.size);
      
      const url = URL.createObjectURL(blob);
      setPdfBlobUrl(url);
      setSelectedPDF(file);
      onFileSelect && onFileSelect(file);
      
      console.log('PDF viewer opened successfully');
    } catch (err) {
      console.error("Error loading PDF:", err);
      alert(`Failed to open PDF: ${err.message}`);
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
          <h2>{getFolderPath()}</h2>
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
            <span>{selectedPDF.original_filename || selectedPDF.filename || selectedPDF.name}</span>
            <button onClick={handleClosePDF}>
              <X size={18} />
            </button>
          </div>
          <iframe
            src={pdfBlobUrl}
            title={selectedPDF.original_filename || selectedPDF.filename || selectedPDF.name}
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
                key={file.file_id || file.id}
                className="file-card"
                onClick={() => handleFileClick(file)}
              >
                <div className="file-info">
                  <div className="file-icon">PDF</div>
                  <div className="file-meta">
                    <strong>{file.original_filename || file.filename || file.name}</strong>
                    <small>
                      {file.file_size ? `${Math.round(file.file_size / 1024)} KB` : (file.size || 'Unknown size')} • Uploaded {file.uploaded_at ? new Date(file.uploaded_at).toLocaleDateString() : (file.uploadDate || 'Unknown date')}
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
