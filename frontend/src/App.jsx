import React, { useState, useEffect, useRef } from 'react';
import { Send, Compass, Plane, Building2, MapPin, Loader2 } from 'lucide-react';

// Maps agent names to specific accent colors defined in CSS
const AGENT_COLORS = {
  "Triage Concierge": "var(--color-triage)",
  "Flight Specialist": "var(--color-flight)",
  "Hotel Specialist": "var(--color-hotel)",
  "Itinerary Specialist": "var(--color-itinerary)"
};

// Maps agent names to Lucide icons
const getAgentIcon = (name) => {
  const nameLower = name.lower ? name.toLowerCase() : String(name).toLowerCase();
  if (nameLower.includes("flight")) return <Plane size={18} />;
  if (nameLower.includes("hotel")) return <Building2 size={18} />;
  if (nameLower.includes("itinerary")) return <MapPin size={18} />;
  return <Compass size={18} />;
};

function App() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I am your travel assistant concierge. How can I help you plan your trip today?'
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [activeAgent, setActiveAgent] = useState('Triage Concierge');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom of messages container
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue('');
    setIsLoading(true);

    // Save previous history for sending to backend
    const currentHistory = [...messages];

    // Add user message to UI state immediately
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);

    try {
      // Map message history to schema format expected by FastAPI
      // We skip the first greeting message to avoid cluttering history if needed, or send everything
      const formattedHistory = currentHistory.map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      const response = await fetch('http://127.0.0.1:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          history: formattedHistory,
          active_agent: activeAgent
        }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      
      // Update agent state and history
      setActiveAgent(data.active_agent);
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: data.response }
      ]);
    } catch (error) {
      console.error('Error contacting agent API:', error);
      setMessages(prev => [
        ...prev,
        { 
          role: 'assistant', 
          content: 'I apologize, but I encountered an error communicating with the agent server. Please make sure the backend server (FastAPI) is running at http://localhost:8000.' 
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Helper function to render text with clean custom card formatting for booking references
  const renderMessageContent = (content) => {
    // Detect custom references like Flight: AA-101 or Bookings: FL-XYZ987 and highlight them
    const bookingRegex = /(FL-[A-Z0-9]{6}|HT-[A-Z0-9]{6}|HT-Grand|HT-Cozy|AA-101|DL-202|UA-303|BA-404)/gi;
    
    if (bookingRegex.test(content)) {
      // Add visual cards for specific structured data items
      return (
        <div>
          <p style={{ whiteSpace: 'pre-wrap' }}>{content}</p>
          <div className="booking-card" style={{ '--accent': AGENT_COLORS[activeAgent] }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase' }}>
              Detected Booking Reference
            </span>
            <span style={{ fontSize: '14px', fontWeight: 600, color: '#f3f4f6' }}>
              Confirmation code / ID generated.
            </span>
          </div>
        </div>
      );
    }

    return <p style={{ whiteSpace: 'pre-wrap' }}>{content}</p>;
  };

  const agentColor = AGENT_COLORS[activeAgent] || 'var(--color-triage)';

  return (
    <div className="app-container">
      <div className="chat-window">
        {/* Header Bar */}
        <header className="chat-header">
          <div className="brand-section">
            <div className="logo-icon">
              <Compass size={22} />
            </div>
            <div>
              <h1 className="brand-name">Vagabond</h1>
              <p style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>OpenAI Multi-Agent System</p>
            </div>
          </div>

          {/* Dynamic Active Agent badge */}
          <div className="agent-status-container">
            <div className="status-dot" style={{ backgroundColor: agentColor }}></div>
            <span className="agent-name-badge" style={{ color: agentColor }}>
              {activeAgent}
            </span>
            <div style={{ display: 'flex', color: agentColor, marginLeft: '4px' }}>
              {getAgentIcon(activeAgent)}
            </div>
          </div>
        </header>

        {/* Messages Body */}
        <main className="messages-container">
          {messages.map((msg, index) => (
            <div key={index} className={`message-wrapper ${msg.role}`}>
              <div className="avatar">
                {msg.role === 'user' ? 'U' : 'A'}
              </div>
              <div className="message-bubble">
                {msg.role === 'user' ? <p>{msg.content}</p> : renderMessageContent(msg.content)}
              </div>
            </div>
          ))}

          {/* Thinking / Typing indicator */}
          {isLoading && (
            <div className="message-wrapper assistant">
              <div className="avatar">A</div>
              <div className="message-bubble">
                <div className="typing-indicator">
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </main>

        {/* Input Panel */}
        <footer className="chat-footer">
          <form onSubmit={handleSend} className="input-container">
            <input
              type="text"
              className="chat-input"
              placeholder={`Ask the ${activeAgent}...`}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              disabled={isLoading}
              autoFocus
            />
            <button type="submit" className="send-button" disabled={!inputValue.trim() || isLoading}>
              <Send size={18} />
            </button>
          </form>
        </footer>
      </div>
    </div>
  );
}

export default App;
