import React, { useState } from 'react';
import { X, Send, Bot, User } from 'lucide-react';
import './AIChat.css'

const AIChat = ({ onClose, selectedFolder }) => {
  const [messages, setMessages] = useState([
    {
      id: '1',
      type: 'ai',
      content: 'Hello! Ask me anything about your documents.',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = () => {
    if (!input.trim()) return;
    const userMsg = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    setTimeout(() => {
      const aiResponse = {
        id: Date.now().toString(),
        type: 'ai',
        content: `Responding to: "${userMsg.content}" (from ${selectedFolder || 'all folders'})`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiResponse]);
      setLoading(false);
    }, 1000);
  };

  return (
    <div className="ai-chat">
      <div className="ai-header">
        <div><Bot size={18} /> AI Assistant</div>
        <button onClick={onClose}><X size={16} /></button>
      </div>

      <div className="ai-body">
        {messages.map(msg => (
          <div key={msg.id} className={`ai-msg ${msg.type}`}>
            <div className="ai-icon">
              {msg.type === 'user' ? <User size={14} /> : <Bot size={14} />}
            </div>
            <div className="ai-bubble">
              <p>{msg.content}</p>
              <small>{msg.timestamp.toLocaleTimeString()}</small>
            </div>
          </div>
        ))}
        {loading && (
          <div className="ai-msg ai">
            <div className="ai-icon"><Bot size={14} /></div>
            <div className="ai-bubble loading">
              <div className="dots"><span>.</span><span>.</span><span>.</span></div>
            </div>
          </div>
        )}
      </div>

      <div className="ai-footer">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendMessage()}
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
