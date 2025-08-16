import React, { useState, useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import CandidateDashboard from './CandidateDashboard';
import { 
  Users, 
  HelpCircle, 
  MessageSquare, 
  BookOpen, 
  UserPlus,
  MessageCircle,
  BarChart3
} from 'lucide-react';
import './ChatPanel.css';

// Icon mapping
const iconMap = {
  Users,
  HelpCircle,
  MessageSquare,
  BookOpen,
  UserPlus
};

const ChatPanel = ({ module, messages, onAddMessage }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [activeView, setActiveView] = useState('chat'); // 'chat' or 'dashboard'
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages are added
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle sending a message
  const handleSendMessage = async (messageText, file = null) => {
    if (!messageText.trim() && !file) return;

    // Add user message immediately
    const userMessage = {
      type: 'user',
      content: messageText,
      file: file ? { name: file.name, size: file.size, type: file.type } : null
    };

    onAddMessage(module.id, userMessage);
    setIsLoading(true);

    try {
      let response;
      let data;

      if (file && (module.id === 'recruitment_module' || module.id === 'feedback_module')) {
        // Handle file upload for recruitment and feedback modules
        const formData = new FormData();
        formData.append('file', file);
        formData.append('message', messageText || '');

        response = await fetch(`/chat/${module.id}/upload`, {
          method: 'POST',
          body: formData
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }

        data = await response.json();
      } else {
        // Regular text message
        response = await fetch(`/chat/${module.id}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            text: messageText
          })
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        data = await response.json();
      }

      // Add agent response
      const agentMessage = {
        type: 'agent',
        content: data.reply || 'Sorry, I encountered an error processing your request.',
        fileProcessed: data.file_processed || null,
        ocrCompleted: data.ocr_completed || false
      };

      onAddMessage(module.id, agentMessage);

    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add error message
      const errorMessage = {
        type: 'agent',
        content: error.message || 'Sorry, I\'m having trouble connecting to the server right now. Please try again later.',
        isError: true
      };

      onAddMessage(module.id, errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // Get module icon
  const getModuleIcon = () => {
    const IconComponent = iconMap[module?.icon] || Users;
    return <IconComponent size={24} className="text-blue-600" />;
  };

  // Generate welcome message for empty conversations
  const getWelcomeMessage = () => {
    const welcomeMessages = {
      recruitment_module: "👋 Hi! I'm your Recruitment Assistant. I can help you screen resumes, schedule interviews, and manage candidates. Upload a resume (PDF only) or ask me to evaluate a candidate!",
      hr_support_module: "👋 Hello! I'm your HR Support Assistant. I can help you manage employee tickets, answer policy questions, and provide HR guidance. What can I help you with today?",
      feedback_module: "👋 Hi there! I'm your Feedback Analysis Assistant. I can analyze employee surveys, generate engagement reports, and provide insights on workplace satisfaction. Upload a CSV survey file or ask me about feedback analysis!",
      lnd_module: "👋 Welcome! I'm your Learning & Development Coach. I can create personalized learning paths, recommend courses, and help with skill development planning. Tell me about an employee's learning needs!",
      onboarding_module: "👋 Hello! I'm your Onboarding Assistant. I can create personalized onboarding plans, guide you through onboarding processes, and help with new hire workflows. How can I assist with onboarding today?"
    };

    return welcomeMessages[module?.id] || "👋 Hello! How can I assist you today?";
  };

  if (!module) {
    return (
      <div className="chat-panel">
        <div className="chat-empty">
          <Users size={48} className="text-gray-400" />
          <h2>Welcome to HR OS</h2>
          <p>Select a module from the sidebar to get started</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-panel">
      {/* Header */}
      <div className="chat-header">
        <div className="chat-header-info">
          <div className="chat-header-icon">
            {getModuleIcon()}
          </div>
          <div className="chat-header-text">
            <h2 className="chat-title">{module.name}</h2>
            <p className="chat-subtitle">{module.description}</p>
          </div>
        </div>
        <div className="chat-header-actions">
          {/* View Toggle for Recruitment Module */}
          {module.id === 'recruitment_module' && (
            <div className="view-toggle">
              <button
                onClick={() => setActiveView('chat')}
                className={`toggle-button ${activeView === 'chat' ? 'active' : ''}`}
                title="Chat View"
              >
                <MessageCircle size={16} />
                Chat
              </button>
              <button
                onClick={() => setActiveView('dashboard')}
                className={`toggle-button ${activeView === 'dashboard' ? 'active' : ''}`}
                title="Candidate Dashboard"
              >
                <BarChart3 size={16} />
                Dashboard
              </button>
            </div>
          )}
          <div className="chat-status">
            <div className={`status-indicator ${isLoading ? 'status-loading' : 'status-ready'}`}></div>
            <span className="status-text">
              {isLoading ? 'Processing...' : 'Ready'}
            </span>
          </div>
        </div>
      </div>

      {/* Content Area */}
      {activeView === 'dashboard' && module.id === 'recruitment_module' ? (
        <CandidateDashboard />
      ) : (
        <>
          {/* Messages Area */}
          <div className="chat-messages">
            {messages.length === 0 && (
              <div className="welcome-message">
                <div className="welcome-content">
                  <div className="welcome-icon">
                    {getModuleIcon()}
                  </div>
                  <div className="welcome-text">
                    <h3>Welcome to {module.name}</h3>
                    <p>{getWelcomeMessage()}</p>
                  </div>
                </div>
              </div>
            )}
            
            {messages.map((message) => (
              <ChatMessage
                key={message.id}
                message={message}
                moduleName={module.name}
              />
            ))}
            
            {isLoading && (
              <div className="loading-message">
                <div className="loading-avatar">
                  {getModuleIcon()}
                </div>
                <div className="loading-content">
                  <div className="loading-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <ChatInput 
            onSendMessage={handleSendMessage}
            disabled={isLoading}
            placeholder={`Message ${module.name}...`}
            moduleId={module.id}
          />
        </>
      )}
    </div>
  );
};

export default ChatPanel;
