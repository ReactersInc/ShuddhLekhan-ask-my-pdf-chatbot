import React, { useState, useContext } from "react";
import { API_URL } from "../config.js";
import { saveAs } from "file-saver";
import { Document, Packer, Paragraph, TextRun } from "docx";
import { useNavigate } from "react-router-dom";
import { SelectedPDFContext } from "../context/selectedPDFContext.jsx";

function UploadPDF() {
  const navigate = useNavigate();
  const { setSelectedPDFUrl, setSelectedPDFName } = useContext(SelectedPDFContext);

  const [files, setFiles] = useState([]);
  const [originalFiles, setOriginalFiles] = useState([]); // state to store uploaded files for later reference
  const [message, setMessage] = useState("");
  const [summaries, setSummaries] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleOpenPDF = (file) => {
    const url = URL.createObjectURL(file);
    setSelectedPDFUrl(url);
    setSelectedPDFName(file.name.replace(/\.pdf$/i, ""));
    navigate("/pdf");
  };

  const handleFileChange = (e) => {
    const fileArray = Array.from(e.target.files);
    setFiles(fileArray);
    setOriginalFiles(fileArray); // <-- set backup files here
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
    } catch (err) {
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
    } catch (err) {
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
    <div style={{ display: "flex", gap: "2rem" }}>
      <div style={{ flex: 1 }}>
        <h2>Upload PDF(s)</h2>
        <input type="file" accept=".pdf" multiple onChange={handleFileChange} />
        <button onClick={handleUpload} disabled={loading}>
          {loading ? "Uploading..." : "Upload"}
        </button>

        {message && (
          <p className={message.toLowerCase().includes("success") ? "success" : "error"}>{message}</p>
        )}

        {files.length > 0 && (
          <div>
            <h3>Uploaded files:</h3>
            {files.map((file, i) => (
              <div
                key={i}
                onClick={() => handleOpenPDF(file)}
                style={{ cursor: "pointer", border: "1px solid #ccc", margin: "5px", padding: "5px" }}
              >
                {file.name}
              </div>
            ))}
          </div>
        )}

        {summaries.length > 0 && (
          <div style={{ marginTop: "1rem", whiteSpace: "pre-wrap" }}>
            <h3>Summaries:</h3>
            <button onClick={handleDownloadWord} style={{ marginBottom: "1rem" }}>
              Download All as Word Document
            </button>

            {summaries.map((item, idx) =>
              item ? (
                <div
                  key={idx}
                  style={{
                    marginBottom: "1rem",
                    padding: "1rem",
                    border: "1px solid #ccc",
                    borderRadius: "5px",
                    cursor: "pointer",
                    backgroundColor: "#f9f9f9",
                  }}
                  onClick={() => {
                    const blob = originalFiles.find(f => f.name === item.filename);
                    if (blob) {
                      const url = URL.createObjectURL(blob);
                      sessionStorage.setItem(item.filename.replace(/\.pdf$/i, ""), url);
                      setSelectedPDFUrl(url);
                      setSelectedPDFName(item.filename.replace(/\.pdf$/i, ""));
                      navigate(`/pdf/${item.filename.replace(/\.pdf$/i, "")}`);
                    }
                  }}
                  
                >
                  <strong>{item.filename}</strong>
                  <p>{item.summary}</p>
                </div>
              ) : null
            )}
          </div>
        )}
      </div>

      {/* <div style={{ flex: 1 }}>
        <AskQuestion />
      </div> */}
    </div>
  );
}

export default UploadPDF;
