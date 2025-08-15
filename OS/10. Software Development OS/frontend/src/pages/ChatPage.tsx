import { useState } from 'react';
import { useParams } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import Toolbar from '../components/Toolbar';
import ChatView from '../components/ChatView';
import Composer from '../components/Composer';
import type { Module } from '../lib/types';

interface ChatPageProps {
  modules: Module[];
}

export default function ChatPage({ modules }: ChatPageProps) {
  const { moduleKey, chatId } = useParams<{ moduleKey: string; chatId: string }>();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  const currentModule = modules.find(m => m.key === moduleKey);
  const chatIdNum = parseInt(chatId || '0', 10);

  if (!currentModule || !chatIdNum) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center text-red-600">
          <p className="text-lg">Module or chat not found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <Sidebar
        modules={modules}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Toolbar */}
        <Toolbar />

        {/* Chat Area */}
        <div className="flex-1 flex flex-col bg-white">
          {/* Messages */}
          <ChatView chatId={chatIdNum} />
          
          {/* Composer */}
          <Composer chatId={chatIdNum} />
        </div>
      </div>
    </div>
  );
}
