import React, { useState } from "react";
import { API_URL } from "../config";

function AskQuestion() {
    const [pdf, setPdf] = useState("");
    const [question, setQuestion] = useState("");
    const [answer, setAnswer] = useState("");
    const [error, setError] = useState("");

    const handleAsk = async () => {
        setAnswer("");
        setError("");
        if (!pdf || !question) {
            setError("Please enter PDF name (without .pdf) and question");
            return;
        }

        try {
            const res = await fetch(`${API_URL}/ask/ask`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ pdf, question }),
            });

            const data = await res.json();
            if (res.ok) {
                setAnswer(data.answer);
            } else {
                setError(data.error || "Failed to get answer");
            }
        } catch {
            setError("Error contacting server");
        }
    };

    return (
        <div>
            <h2>Ask Question</h2>
            <input
                type="text"
                placeholder="PDF name (without .pdf)"
                value={pdf}
                onChange={(e) => setPdf(e.target.value)}
            />

            <br />

            <textarea
                placeholder="Enter your question"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
            />

            <br />

            <button onClick={handleAsk}>Ask</button>

            {answer && (
                <>
                    <h3>Answer:</h3>
                    <p className="success">{answer}</p>
                </>
            )}

            {error && <p className="error">{error}</p>}

        </div>
    );
}

export default AskQuestion;
