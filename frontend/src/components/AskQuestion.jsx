import React, { useState } from "react";
import { API_URL } from "../config";

function AskQuestion() {
    const [pdf, setPdf] = useState("");
    const [question, setQuestion] = useState("");
    const [answer, setAnswer] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleAsk = async () => {
        setAnswer("");
        setError("");
        if (!pdf.trim() || !question.trim()) {
            setError("Please enter both the PDF name and your question.");
            return;
        }

        setLoading(true);
        try {
            const res = await fetch(`${API_URL}/qa/ask`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ pdf_name: pdf.trim(), question: question.trim() }),
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

    return (
        <div style={styles.container}>
            <h2 style={styles.heading}>Ask a Question About Your PDF</h2>

            <input
                type="text"
                placeholder="PDF name (without .pdf)"
                value={pdf}
                onChange={(e) => setPdf(e.target.value)}
                style={styles.input}
            />

            <textarea
                placeholder="Enter your question"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                rows={4}
                style={styles.textarea}
            />

            <button onClick={handleAsk} disabled={loading} style={styles.button}>
                {loading ? "Thinking..." : "Ask"}
            </button>

            {answer && (
                <div style={styles.answerBox}>
                    <h3>Answer:</h3>
                    <p style={styles.success}>{answer}</p>
                </div>
            )}

            {error && <p style={styles.error}>{error}</p>}
        </div>
    );
}

const styles = {
    container: {
        maxWidth: "600px",
        margin: "0 auto",
        padding: "20px",
        fontFamily: "Arial, sans-serif",
    },
    heading: {
        marginBottom: "20px",
        textAlign: "center",
    },
    input: {
        width: "100%",
        padding: "10px",
        marginBottom: "10px",
        fontSize: "16px",
    },
    textarea: {
        width: "100%",
        padding: "10px",
        fontSize: "16px",
        marginBottom: "10px",
    },
    button: {
        padding: "10px 20px",
        fontSize: "16px",
        backgroundColor: "#007bff",
        color: "white",
        border: "none",
        cursor: "pointer",
    },
    answerBox: {
        marginTop: "20px",
        padding: "10px",
        backgroundColor: "#f1f1f1",
        borderRadius: "5px",
    },
    success: {
        color: "#2e7d32",
        fontWeight: "bold",
    },
    error: {
        color: "#d32f2f",
        marginTop: "10px",
    },
};

export default AskQuestion;
