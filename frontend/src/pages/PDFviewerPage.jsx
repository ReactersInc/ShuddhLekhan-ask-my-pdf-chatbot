import React, { useContext, useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { API_URL } from "../config";
import AskQuestion from "../components/AskQuestion";
import { SelectedPDFContext } from "../context/selectedPDFContext";

function PDFViewerPage() {
  const { selectedPDFUrl, selectedPDFName } = useContext(SelectedPDFContext);
  const { name } = useParams(); // gets pdf name from URL
  const navigate = useNavigate();

  const [url, setUrl] = useState(null);
  const [pdfName, setPdfName] = useState(null);

  useEffect(() => {
    if (selectedPDFUrl && selectedPDFName) {
      setUrl(selectedPDFUrl);
      setPdfName(selectedPDFName);
    } else if (name) {
      
      // Trys to reconstruct PDF url from uploaded file name
      const fileFromCache = sessionStorage.getItem(name);
      if (fileFromCache) {
        const blob = new Blob([new Uint8Array(JSON.parse(fileFromCache))], { type: "application/pdf" });
        const objectUrl = URL.createObjectURL(blob);
        setUrl(objectUrl);
        setPdfName(name);
      } else {
        navigate("/");
      }
    } else {
      navigate("/");
    }

    return () => {
      if (url) URL.revokeObjectURL(url);
    };
  }, [selectedPDFUrl, selectedPDFName, name]);

  if (!url || !pdfName) return null;

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <div style={{ flex: 1, padding: "1rem" }}>
        <button
          onClick={() => {
            URL.revokeObjectURL(url); // freeing memory
            navigate("/");
          }}
          style={{ marginBottom: "1rem" }}
        >
          ← Back to Upload
        </button>
        <iframe
          src={url}
          width="100%"
          height="90%"
          title={pdfName}
          style={{ border: "1px solid #ccc" }}
        />
      </div>
      <div style={{ flex: 1, padding: "1rem", borderLeft: "1px solid #eee", overflowY: "auto" }}>
        <AskQuestion pdfName={pdfName} />
      </div>
    </div>
  );
}

export default PDFViewerPage;
