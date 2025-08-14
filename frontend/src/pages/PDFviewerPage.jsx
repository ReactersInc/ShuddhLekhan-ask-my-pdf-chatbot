import React, { useContext, useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { API_URL } from "../config/config";
import AskQuestion from "../components/AskQuestion";
import { SelectedPDFContext } from "../context/selectedPDFContext";
import "./PDFViewerPage.css";

function PDFViewerPage() {
  const { selectedPDFUrl, selectedPDFName } = useContext(SelectedPDFContext);
  const { name } = useParams();
  const navigate = useNavigate();

  const [url, setUrl] = useState(null);
  const [pdfName, setPdfName] = useState(null);

  useEffect(() => {
    if (selectedPDFUrl && selectedPDFName) {
      setUrl(selectedPDFUrl);
      setPdfName(selectedPDFName);
    } else if (name) {
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
    <div className="viewer-page">
      <div className="viewer-left">
        <button
          className="back-button"
          onClick={() => {
            URL.revokeObjectURL(url);
            navigate("/");
          }}
        >
          ← Back to Upload
        </button>
        <iframe
          src={url}
          title={pdfName}
          className="pdf-iframe"
        />
      </div>
      <div className="viewer-right">
        <AskQuestion pdfName={pdfName} />
      </div>
    </div>
  );
}

export default PDFViewerPage;
