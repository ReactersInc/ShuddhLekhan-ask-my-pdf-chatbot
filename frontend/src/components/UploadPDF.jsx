import React, { useState, useContext } from "react";
import { API_URL } from "../config/config.js";
import { saveAs } from "file-saver";
import { Document, Packer, Paragraph, TextRun } from "docx";
import { useNavigate } from "react-router-dom";
import { SelectedPDFContext } from "../context/selectedPDFContext.jsx";
import "./UploadPDF.css";

function UploadPDF() {
  const navigate = useNavigate();
  const { setSelectedPDFUrl, setSelectedPDFName } = useContext(SelectedPDFContext);

  const [files, setFiles] = useState([]);
  const [originalFiles, setOriginalFiles] = useState([]);
  const [message, setMessage] = useState("");
  const [summaries, setSummaries] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploadedPaths, setUploadedPaths] = useState([]);

  const handleFileChange = (e) => {
    const fileArray = Array.from(e.target.files);
    setFiles(fileArray);
    setOriginalFiles(fileArray);
    setMessage("");
    setSummaries([]);
    setUploadedPaths([]);
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
        setMessage("Files uploaded successfully. Click 'Start Processing' to begin.");
        setFiles([]);
        setUploadedPaths(data.uploaded_files);
        document.querySelector('input[type="file"]').value = null;
      } else {
        setMessage(data.error || "File upload failed");
      }
    } catch {
      setMessage("Error uploading file");
    } finally {
      setLoading(false);
    }
  };

  const handleStartProcessing = async () => {
    try {
      const res = await fetch(`${API_URL}/upload/start_processing`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({})
      });

      const data = await res.json();

      if (res.ok) {
        data.forEach(({ task_id, filename, processing_method }, index) => {
          pollTaskStatus(task_id, filename, index, processing_method);
        });
      } else {
        setMessage("Processing failed");
      }
    } catch {
      setMessage("Error starting processing");
    }
  };

  const pollTaskStatus = async (taskId, filename, index, processingMethod = "standard") => {
    try {
      const res = await fetch(`${API_URL}/upload/task_status/${taskId}`);
      const data = await res.json();

      if (data.status === "completed") {
        setSummaries((prev) => [
          ...prev,
          { 
            filename, 
            summary: data.summary || "No summary found",
            language: data.detected_language || "english",
            processingMethod: data.processing_method || processingMethod,
            chunksProcessed: data.chunks_processed,
            processingTime: data.processing_time
          }
        ]);
      } else if (data.status === "failed") {
        setSummaries((prev) => [
          ...prev,
          { 
            filename, 
            summary: `Task failed: ${data.error}`,
            language: "english",
            processingMethod: processingMethod
          }
        ]);
      } else if (data.status === "processing") {
        // Show progress message for agentic processing
        setMessage(`Processing ${filename}: ${data.message || "In progress..."} (${data.progress || 0}%)`);
        setTimeout(() => pollTaskStatus(taskId, filename, index, processingMethod), 1000);
      } else {
        setTimeout(() => pollTaskStatus(taskId, filename, index, processingMethod), 2000);
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

        {uploadedPaths.length > 0 && (
          <button onClick={handleStartProcessing} style={{ marginTop: "10px" }}>
            Start Processing
          </button>
        )}

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
            <button onClick={handleDownloadWord} style={{ marginBottom: "1rem" }}>
              Download All as Word Document
            </button>
            <div>
              {summaries.map((item, index) => (
                <div
                  key={index}
                  className="summary-item clickable"
                  onClick={() => {
                    const normalizedFilename = item.filename.replace(/^\.?\/*/, "").trim();
                    const matchingFile = originalFiles.find(
                      f => f.webkitRelativePath.replace(/^\.?\/*/, "").trim() === normalizedFilename
                    );
                    console.log(matchingFile);
                    console.log(normalizedFilename);
                    
                    if (matchingFile) {
                      const url = URL.createObjectURL(matchingFile);
                      setSelectedPDFUrl(url);
                      setSelectedPDFName(matchingFile.name.replace(/\.pdf$/i, ""));
                      navigate(`/pdf/${matchingFile.name.replace(/\.pdf$/i, "")}`);
                    } else {
                      setMessage(`PDF not found: ${item.filename}`);
                    }
                  }}

                >
                  <div className="summary-header">
                    <strong>{item.filename}</strong>
                  </div>
                  <p className={`summary-content ${item.language === 'hindi' ? 'hindi-text' : ''}`}>
                    {item.summary}
                  </p>
                </div>
              ))}


            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default UploadPDF;
