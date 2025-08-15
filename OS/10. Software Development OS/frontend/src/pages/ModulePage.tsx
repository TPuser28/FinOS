import { useState } from 'react';
import { useParams } from 'react-router-dom';

import Sidebar from '../components/Sidebar';
import Toolbar from '../components/Toolbar';
import NewChatButton from '../components/NewChatButton';
import type { Module } from '../lib/types';

interface ModulePageProps {
  modules: Module[];
}

export default function ModulePage({ modules }: ModulePageProps) {
  const { moduleKey } = useParams<{ moduleKey: string }>();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  const currentModule = modules.find(m => m.key === moduleKey);

  if (!currentModule) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center text-red-600">
          <p className="text-lg">Module not found</p>
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

        {/* Content Area */}
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="text-center max-w-md">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Welcome to {currentModule.name}
              </h2>
              <p className="text-gray-600 mb-6">
                Start a new conversation to begin working with this module. You can ask questions, 
                upload files, and get assistance with your development tasks.
              </p>
              <NewChatButton />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
