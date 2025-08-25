import React, { useState } from "react";
import { X, Send, Bot, User } from "lucide-react";
import "./AIChat.css";
import { API_URL } from "../../config/config";
import ReactMarkdown from "react-markdown";

const AIChat = ({ onClose, selectedFile }) => {
  const [messages, setMessages] = useState([
    {
      id: "1",
      type: "ai",
      content: "Hello! Ask me anything about your documents.",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg = {
      id: Date.now().toString(),
      type: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      // Extract the PDF name from selectedFolder
      const pdfPath = selectedFile?.relative_path || selectedFile?.name;
      console.log("selected", pdfPath);

      if (!pdfPath) {
        throw new Error("No PDF found in selected folder.");
      }

      const res = await fetch(`${API_URL}/qa/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          pdf_name: pdfPath,
          question: userMsg.content,
        }),
      });

      const data = await res.json();

      const aiResponse = {
        id: Date.now().toString(),
        type: "ai",
        content:
          data.answer || data.error || "Sorry, I couldn't understand that.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiResponse]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          type: "ai",
          content: `Error: ${err.message}`,
          timestamp: new Date(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ai-chat">
      <div className="ai-header">
        <div>
          <Bot size={18} /> AI Assistant
        </div>
        <button onClick={onClose}>
          <X size={16} />
        </button>
      </div>

      <div className="ai-body">
        {messages.map((msg) => (
          <div key={msg.id} className={`ai-msg ${msg.type}`}>
            <div className="ai-icon">
              {msg.type === "user" ? <User size={14} /> : <Bot size={14} />}
            </div>
            <div className="ai-bubble">
              <ReactMarkdown>{msg.content}</ReactMarkdown>
              <small>{msg.timestamp.toLocaleTimeString()}</small>
            </div>
          </div>
        ))}
        {loading && (
          <div className="ai-msg ai">
            <div className="ai-icon">
              <Bot size={14} />
            </div>
            <div className="ai-bubble loading">
              <div className="dots">
                <span>.</span>
                <span>.</span>
                <span>.</span>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="ai-footer">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Ask about your documents..."
        />
        <button onClick={sendMessage} disabled={!input.trim() || loading}>
          <Send size={16} />
        </button>
      </div>
    </div>
  );
};

export default AIChat;
