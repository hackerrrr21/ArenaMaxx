import React, { useState, useRef, useEffect } from 'react';
import { Sparkles, X, Send, User, Bot, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function GeminiChat() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'bot', text: 'Hello! I am your ArenaMaxx Assistant powered by Google Gemini. How can I help you navigate the stadium today?' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg = input.trim();
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:5000/api/gemini/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg })
      });
      const data = await response.json();
      
      let reply = data.reply || "Sorry, I'm having trouble connecting right now.";
      
      // Handle Navigation Actions
      if (reply.includes('ACTION:NAVIGATE:')) {
        const parts = reply.split('ACTION:NAVIGATE:');
        const path = parts[1].trim().split(' ')[0]; // Extract /path
        const cleanReply = parts[0].trim();
        
        setMessages(prev => [...prev, { role: 'bot', text: cleanReply, action: path }]);
        
        // Auto-navigate after a short delay
        setTimeout(() => {
          navigate(path);
          setIsOpen(false);
        }, 1500);
      } else {
        setMessages(prev => [...prev, { role: 'bot', text: reply }]);
      }
    } catch (err) {
      setMessages(prev => [...prev, { role: 'bot', text: "Error: Could not reach the assistant server." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ position: 'fixed', bottom: '20px', right: '20px', zIndex: 2000 }}>
      {/* Floating Button */}
      {!isOpen && (
        <button 
          onClick={() => setIsOpen(true)}
          style={{
            width: '60px',
            height: '60px',
            borderRadius: '50%',
            backgroundColor: '#4f46e5',
            color: 'white',
            border: 'none',
            boxShadow: '0 4px 20px rgba(79, 70, 229, 0.4)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'transform 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
          }}
          className="pulse-animation"
          onMouseEnter={(e) => e.target.style.transform = 'scale(1.1)'}
          onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
          aria-label="Open AI Concierge"
        >
          <Sparkles size={28} />
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="glass-panel" style={{ 
          width: '350px', 
          height: '500px', 
          backgroundColor: 'white', 
          display: 'flex', 
          flexDirection: 'column',
          overflow: 'hidden',
          boxShadow: '0 10px 40px rgba(0,0,0,0.15)',
          border: '1px solid #e2e8f0'
        }}>
          {/* Header */}
          <div style={{ padding: '15px 20px', backgroundColor: '#4f46e5', color: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Sparkles size={18} />
              <span style={{ fontWeight: 'bold' }}>ArenaMaxx AI Concierge</span>
            </div>
            <button 
              onClick={() => setIsOpen(false)} 
              style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer' }}
              aria-label="Close Chat"
            >
              <X size={20} />
            </button>
          </div>

          {/* Messages area */}
          <div style={{ flex: 1, padding: '15px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '12px', backgroundColor: '#fcfcfd' }}>
            {messages.map((m, idx) => (
              <div key={idx} style={{ 
                display: 'flex', 
                flexDirection: 'column',
                alignItems: m.role === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '100%'
              }}>
                <div style={{ 
                  padding: '10px 14px', 
                  borderRadius: '12px', 
                  fontSize: '0.94rem',
                  lineHeight: '1.4',
                  backgroundColor: m.role === 'user' ? '#4f46e5' : '#f1f5f9',
                  color: m.role === 'user' ? 'white' : '#1e293b',
                  border: m.role === 'bot' ? '1px solid #e2e8f0' : 'none',
                  boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
                }}>
                  {m.text}
                </div>
                {m.action && (
                  <div style={{ fontSize: '0.8rem', color: '#4f46e5', marginTop: '4px', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    Redirecting to {m.action}... <ArrowRight size={12} />
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div style={{ padding: '10px 14px', borderRadius: '12px', backgroundColor: '#f1f5f9', width: 'fit-content' }}>
                <div className="typing-loader"></div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Input Area */}
          <form onSubmit={handleSend} style={{ padding: '15px', borderTop: '1px solid #e2e8f0', display: 'flex', gap: '8px' }}>
            <input 
              type="text" 
              placeholder="Ask anything..." 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              style={{ flex: 1, border: '1px solid #e2e8f0', borderRadius: '8px', padding: '10px 12px', outline: 'none', fontSize: '0.9rem' }}
            />
            <button 
              type="submit" 
              disabled={isLoading || !input.trim()}
              style={{ 
                backgroundColor: '#4f46e5', 
                color: 'white', 
                border: 'none', 
                borderRadius: '8px', 
                width: '40px', 
                display: 'flex', 
                alignItems: 'center', 
               justifyContent: 'center',
                cursor: isLoading ? 'not-allowed' : 'pointer',
                opacity: isLoading ? 0.6 : 1
              }}
              aria-label="Send Message"
            >
              <Send size={18} />
            </button>
          </form>
        </div>
      )}

      <style>{`
        .pulse-animation {
          animation: pulse 2s infinite;
        }
        @keyframes pulse {
          0% { box-shadow: 0 0 0 0 rgba(79, 70, 229, 0.7); }
          70% { box-shadow: 0 0 0 15px rgba(79, 70, 229, 0); }
          100% { box-shadow: 0 0 0 0 rgba(79, 70, 229, 0); }
        }
        .typing-loader {
          width: 30px;
          height: 10px;
          background: radial-gradient(circle at 2px 5px, #64748b 2px, transparent 0),
                      radial-gradient(circle at 15px 5px, #64748b 2px, transparent 0),
                      radial-gradient(circle at 28px 5px, #64748b 2px, transparent 0);
          animation: typing 1s infinite alternate;
        }
        @keyframes typing {
          0% { opacity: 0.3; }
          100% { opacity: 1; }
        }
      `}</style>
    </div>
  );
}
