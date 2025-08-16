import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ChatPanel from './components/ChatPanel';
import PreScreenPage from './pages/PreScreenPage';
import './App.css';

// Available HR modules
const HR_MODULES = [
  {
    id: 'recruitment_module',
    name: 'Recruitment',
    description: 'Resume screening, interview scheduling, and candidate management',
    icon: 'Users'
  },
  {
    id: 'hr_support_module',
    name: 'HR Support',
    description: 'Employee tickets, policy queries, and helpdesk support',
    icon: 'HelpCircle'
  },
  {
    id: 'feedback_module',
    name: 'Feedback',
    description: 'Employee surveys, sentiment analysis, and engagement reports',
    icon: 'MessageSquare'
  },
  {
    id: 'lnd_module',
    name: 'Learning & Development',
    description: 'Personalized learning paths and skill development',
    icon: 'BookOpen'
  },
  {
    id: 'onboarding_module',
    name: 'Onboarding',
    description: 'New hire onboarding workflows and milestone tracking',
    icon: 'UserPlus'
  }
];

function App() {
  // State for active module
  const [activeModule, setActiveModule] = useState('recruitment_module');
  
  // State for conversations - stored in localStorage
  const [conversations, setConversations] = useState({});

  // Load conversations from localStorage on component mount
  useEffect(() => {
    const savedConversations = localStorage.getItem('hr-os-conversations');
    if (savedConversations) {
      try {
        setConversations(JSON.parse(savedConversations));
      } catch (error) {
        console.error('Error loading conversations from localStorage:', error);
        setConversations({});
      }
    }
  }, []);

  // Save conversations to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('hr-os-conversations', JSON.stringify(conversations));
  }, [conversations]);

  // Check if we're on the prescreen page
  const isPreScreenPage = window.location.pathname === '/prescreen' || window.location.search.includes('candidate=');
  
  // If it's prescreen page, render the prescreen interface
  if (isPreScreenPage) {
    return <PreScreenPage />;
  }

  // Handle module selection
  const handleModuleSelect = (moduleId) => {
    setActiveModule(moduleId);
  };

  // Add a new message to the conversation
  const addMessage = (moduleId, message) => {
    setConversations(prev => ({
      ...prev,
      [moduleId]: [
        ...(prev[moduleId] || []),
        {
          id: Date.now() + Math.random(),
          ...message,
          timestamp: new Date().toISOString()
        }
      ]
    }));
  };

  // Get current conversation
  const currentConversation = conversations[activeModule] || [];

  // Get active module info
  const activeModuleInfo = HR_MODULES.find(module => module.id === activeModule);

  return (
    <div className="app">
      <Sidebar 
        modules={HR_MODULES}
        activeModule={activeModule}
        onModuleSelect={handleModuleSelect}
      />
      <ChatPanel 
        module={activeModuleInfo}
        messages={currentConversation}
        onAddMessage={addMessage}
      />
    </div>
  );
}

export default App;
