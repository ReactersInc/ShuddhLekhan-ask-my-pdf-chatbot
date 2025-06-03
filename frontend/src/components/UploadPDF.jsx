import React, { useState } from "react";
import { API_URL } from "../config.js";

function UploadPDF() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setMessage("");
    setSummary("");
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage("Please select a file first");
      return;
    }

    setLoading(true);
    setMessage("");
    setSummary("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_URL}/upload/`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (res.ok) {
        setMessage(data.message);
        setSummary(data.summary || "");
        setFile(null);
        // Optional: clear the file input element value as well
        document.querySelector('input[type="file"]').value = null;
      } else {
        setMessage(data.error || "File upload failed");
      }
    } catch (err) {
      setMessage("Error uploading file");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Upload PDF</h2>
      <input type="file" accept=".pdf" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Uploading..." : "Upload"}
      </button>

      {message && (
        <p className={message.includes("successfully") ? "success" : "error"}>
          {message}
        </p>
      )}

      {summary && (
        <div style={{ marginTop: "1rem", whiteSpace: "pre-wrap" }}>
          <h3>Summary:</h3>
          <p>{summary}</p>
        </div>
      )}
    </div>
  );
}

export default UploadPDF;
