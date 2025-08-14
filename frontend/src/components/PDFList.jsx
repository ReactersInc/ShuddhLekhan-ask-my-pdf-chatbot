import React, { useEffect, useState } from "react";
import { API_URL } from "../config/config";
import "./PDFList.css";

function PDFList() {
  const [pdfs, setPdfs] = useState([]);

  useEffect(() => {
    fetch(`${API_URL}/pdfs/`)
      .then((res) => res.json())
      .then(setPdfs)
      .catch(() => setPdfs([]));
  }, []);

  return (
    <div className="pdf-list-container">
      <h2>Uploaded PDFs & Summaries</h2>
      {pdfs.length === 0 && <p>No PDFs uploaded yet.</p>}
      <ul>
        {pdfs.map(({ filename, summary }) => (
          <li key={filename} className="pdf-item">
            <strong>{filename}</strong>
            <p>{summary}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default PDFList;
