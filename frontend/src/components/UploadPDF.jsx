import React, { useState, useContext } from "react";
import { API_URL } from "../config.js";
import { saveAs } from "file-saver";
import { Document, Packer, Paragraph, TextRun } from "docx";
import { useNavigate } from "react-router-dom";
import { SelectedPDFContext } from "../context/selectedPDFContext.jsx";
import "./UploadPDF.css";

// Helper: Tree builder
function buildSummaryTree(summaries) {
  const root = {};

  for (const { filename, summary } of summaries) {
    const parts = filename.split('/');
    let node = root;

    parts.forEach((part, i) => {
      if (!node[part]) {
        node[part] = i === parts.length - 1
          ? { __summary: summary }
          : {};
      }
      node = node[part];
    });
  }

  return root;
}

// Helper: Highlight matched query
function highlightMatch(text, query) {
  if (!query) return text;
  const regex = new RegExp(`(${query})`, "gi");
  const parts = text.split(regex);
  return parts.map((part, i) =>
    regex.test(part) ? <mark key={i}>{part}</mark> : part
  );
}

// Recursive Tree Viewer
const SummaryTree = ({ tree, path = "", onOpen, searchQuery = "" }) => {
  const [openFolders, setOpenFolders] = useState({});

  const toggleFolder = (folderPath) => {
    setOpenFolders(prev => ({
      ...prev,
      [folderPath]: !prev[folderPath]
    }));
  };

  return (
    <ul style={{ listStyle: "none", paddingLeft: "1rem" }}>
      {Object.entries(tree).map(([name, value]) => {
        const currentPath = path ? `${path}/${name}` : name;

        if (value.__summary) {
          const matches = name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          value.__summary.toLowerCase().includes(searchQuery.toLowerCase());
          if (!matches && searchQuery) return null;

          return (
            <li
              key={currentPath}
              onClick={() => onOpen(currentPath)}
              style={{ cursor: "pointer", marginBottom: "0.5rem" }}
            >
              📄 <strong>{highlightMatch(name, searchQuery)}</strong>
              <p style={{ fontSize: "0.875rem", marginLeft: "1.5rem", color: "#555" }}>
                {highlightMatch(value.__summary, searchQuery)}
              </p>
            </li>
          );
        }

        const hasMatchingChild = Object.entries(value).some(([childName, childVal]) => {
          if (childVal.__summary) {
            return childName.toLowerCase().includes(searchQuery.toLowerCase()) ||
                   childVal.__summary.toLowerCase().includes(searchQuery.toLowerCase());
          }
          return true;
        });

        if (!hasMatchingChild && searchQuery) return null;

        const isOpen = openFolders[currentPath] ?? true;

        return (
          <li key={currentPath} style={{ marginBottom: "0.5rem" }}>
            <div
              style={{ cursor: "pointer" }}
              onClick={() => toggleFolder(currentPath)}
            >
              {isOpen ? "📂" : "📁"} <strong>{highlightMatch(name, searchQuery)}</strong>
            </div>
            {isOpen && (
              <SummaryTree
                tree={value}
                path={currentPath}
                onOpen={onOpen}
                searchQuery={searchQuery}
              />
            )}
          </li>
        );
      })}
    </ul>
  );
};

function UploadPDF() {
  const navigate = useNavigate();
  const { setSelectedPDFUrl, setSelectedPDFName } = useContext(SelectedPDFContext);

  const [files, setFiles] = useState([]);
  const [originalFiles, setOriginalFiles] = useState([]);
  const [message, setMessage] = useState("");
  const [summaries, setSummaries] = useState([]);
  const [loading, setLoading] = useState(false);
  const [summarySearch, setSummarySearch] = useState("");

  const handleOpenPDF = (filePath) => {
    const blob = originalFiles.find(
      f => f.webkitRelativePath === filePath || f.name === filePath
    );
    if (blob) {
      const url = URL.createObjectURL(blob);
      sessionStorage.setItem(filePath.replace(/\.pdf$/i, ""), url);
      setSelectedPDFUrl(url);
      setSelectedPDFName(filePath.replace(/\.pdf$/i, ""));
      navigate(`/pdf/${filePath.replace(/\.pdf$/i, "")}`);
    }
  };

  const handleFileChange = (e) => {
    const fileArray = Array.from(e.target.files);
    setFiles(fileArray);
    setOriginalFiles(fileArray);
    setMessage("");
    setSummaries([]);
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      setMessage("Please select at least one file");
      return;
    }

    setLoading(true);
    setMessage("");
    setSummaries([]);

    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));

    try {
      const res = await fetch(`${API_URL}/upload/`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (res.ok) {
        setMessage("Files uploaded successfully. Processing...");
        setFiles([]);
        document.querySelector('input[type="file"]').value = null;

        data.forEach(({ task_id, filename }, index) => {
          pollTaskStatus(task_id, filename, index);
        });
      } else {
        setMessage(data.error || "File upload failed");
      }
    } catch {
      setMessage("Error uploading file");
    } finally {
      setLoading(false);
    }
  };

  const pollTaskStatus = async (taskId, filename, index) => {
    try {
      const res = await fetch(`${API_URL}/upload/task_status/${taskId}`);
      const data = await res.json();

      if (data.status === "completed") {
        setSummaries((prev) => {
          const newSummaries = [...prev];
          newSummaries[index] = { filename, summary: data.summary || "No summary found" };
          return newSummaries;
        });
      } else if (data.status === "failed") {
        setSummaries((prev) => {
          const newSummaries = [...prev];
          newSummaries[index] = { filename, summary: `Task failed: ${data.error}` };
          return newSummaries;
        });
      } else {
        setTimeout(() => pollTaskStatus(taskId, filename, index), 2000);
      }
    } catch {
      setMessage("Error fetching task status");
    }
  };

  const handleDownloadWord = async () => {
    const doc = new Document({
      sections: [
        {
          children: summaries.map((item) =>
            new Paragraph({
              children: [
                new TextRun({ text: item.filename, bold: true, size: 26 }),
                new TextRun("\n" + item.summary + "\n\n")
              ]
            })
          )
        }
      ]
    });

    const blob = await Packer.toBlob(doc);
    saveAs(blob, "Summaries.docx");
  };

  return (
    <div className="upload-container">
      <div className="upload-box">
        <h2>Upload PDF(s)</h2>
        <input
          type="file"
          accept=".pdf"
          multiple
          webkitdirectory="true"
          directory="true"
          onChange={handleFileChange}
        />
        <button onClick={handleUpload} disabled={loading}>
          {loading ? "Uploading..." : "Upload"}
        </button>

        {message && (
          <p className={message.toLowerCase().includes("success") ? "success" : "error"}>{message}</p>
        )}

        {files.length > 0 && (
          <div>
            <h3>Selected files:</h3>
            {files.map((file, i) => (
              <div key={i} className="file-item">{file.webkitRelativePath || file.name}</div>
            ))}
          </div>
        )}

        {summaries.length > 0 && (
          <div className="summary-section">
            <h3>Summaries:</h3>

            <input
              type="text"
              placeholder="Search summaries..."
              value={summarySearch}
              onChange={(e) => setSummarySearch(e.target.value)}
              style={{
                padding: "0.5rem",
                width: "100%",
                marginBottom: "1rem",
                border: "1px solid #ccc",
                borderRadius: "4px",
              }}
            />

            <button onClick={handleDownloadWord} style={{ marginBottom: "1rem" }}>
              Download All as Word Document
            </button>

            <SummaryTree
              tree={buildSummaryTree(summaries)}
              onOpen={handleOpenPDF}
              searchQuery={summarySearch}
            />
          </div>
        )}
      </div>
    </div>
  );
}

export default UploadPDF;
