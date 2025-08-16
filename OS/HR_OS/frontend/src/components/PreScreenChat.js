import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User } from 'lucide-react';
import './PreScreenChat.css';

const PreScreenChat = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages are added
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Add welcome message on component mount
  useEffect(() => {
    const welcomeMessage = {
      id: Date.now(),
      type: 'bot',
      content: "Hello! I'm PreScreenBot, and I'll be conducting your pre-screening interview today. To get started, could you please provide your full name and email address?",
      timestamp: new Date().toISOString()
    };
    setMessages([welcomeMessage]);
  }, []);

  // Handle sending a message
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Send to PreScreen Bot
      const response = await fetch('/prescreen', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: inputMessage
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Add bot response
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: data.reply || 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, botMessage]);

    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: 'Sorry, I\'m having trouble connecting right now. Please try again later.',
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle Enter key press
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  // Format timestamp
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="prescreen-chat">
      {/* Header */}
      <div className="prescreen-header">
        <div className="prescreen-header-info">
          <div className="prescreen-header-icon">
            <Bot size={24} className="text-blue-600" />
          </div>
          <div className="prescreen-header-text">
            <h2 className="prescreen-title">Pre-Screening Interview</h2>
            <p className="prescreen-subtitle">Conducted by PreScreenBot</p>
          </div>
        </div>
        <div className="prescreen-status">
          <div className={`status-indicator ${isLoading ? 'status-loading' : 'status-ready'}`}></div>
          <span className="status-text">
            {isLoading ? 'Typing...' : 'Online'}
          </span>
        </div>
      </div>

      {/* Messages Area */}
      <div className="prescreen-messages">
        {messages.map((message) => (
          <div key={message.id} className={`prescreen-message ${message.type === 'user' ? 'message-user' : 'message-bot'}`}>
            <div className="message-container">
              {/* Avatar */}
              <div className={`message-avatar ${message.type === 'user' ? 'avatar-user' : 'avatar-bot'}`}>
                {message.type === 'user' ? (
                  <User size={16} />
                ) : (
                  <Bot size={16} />
                )}
              </div>

              {/* Content */}
              <div className="message-content">
                <div className="message-header">
                  <span className="message-sender">
                    {message.type === 'user' ? 'You' : 'PreScreenBot'}
                  </span>
                  <span className="message-time">
                    {formatTime(message.timestamp)}
                  </span>
                </div>
                
                <div className="message-text">
                  {message.content}
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="prescreen-message message-bot">
            <div className="message-container">
              <div className="message-avatar avatar-bot">
                <Bot size={16} />
              </div>
              <div className="message-content">
                <div className="loading-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="prescreen-input-container">
        <form onSubmit={handleSendMessage} className="prescreen-input-form">
          <div className="input-wrapper">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your response..."
              disabled={isLoading}
              className="message-input"
            />
            <button
              type="submit"
              disabled={isLoading || !inputMessage.trim()}
              className="send-button"
              title="Send message"
            >
              <Send size={20} />
            </button>
          </div>
        </form>
        <div className="input-help">
          <p>Please answer the questions honestly and completely. This interview will help us understand your qualifications better.</p>
        </div>
      </div>
    </div>
  );
};

export default PreScreenChat;
