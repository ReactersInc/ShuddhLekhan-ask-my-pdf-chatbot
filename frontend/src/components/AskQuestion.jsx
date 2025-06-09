import React, { useState, useEffect } from "react";
import { API_URL } from "../config";
import "./AskQuestion.css";

function AskQuestion({ pdfName }) {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setQuestion("");
    setAnswer("");
    setError("");
  }, [pdfName]);

  const handleAsk = async () => {
    setAnswer("");
    setError("");

    if (!pdfName?.trim()) {
      setError("No PDF selected.");
      return;
    }
    if (!question.trim()) {
      setError("Please enter your question.");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/qa/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pdf_name: pdfName.trim(), question: question.trim() }),
      });

      const data = await res.json();
      if (res.ok) {
        setAnswer(data.answer);
      } else {
        setError(data.error || "Failed to get an answer.");
      }
    } catch {
      setError("Error contacting the server.");
    } finally {
      setLoading(false);
    }
  };

  if (!pdfName) {
    return <p>Please select a PDF to ask questions.</p>;
  }

  return (
    <div className="ask-container">
      <h2>Ask a Question about <em>{pdfName}</em></h2>
      <textarea
        placeholder="Enter your question"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        rows={4}
        className="ask-textarea"
        disabled={loading}
        aria-label={`Question about ${pdfName}`}
      />
      <button onClick={handleAsk} disabled={loading || !question.trim()} className="ask-button">
        {loading ? "Thinking..." : "Ask"}
      </button>

      {answer && (
        <div className="answer-box">
          <h4>Answer:</h4>
          <p>{answer}</p>
        </div>
      )}

      {error && <p className="error-message">{error}</p>}
    </div>
  );
}

export default AskQuestion;
