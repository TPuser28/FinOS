import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import { Button } from '../ui/Button';
import { Separator } from '../ui/Separator';
import ModuleList from './ModuleList';
import ChatList from './ChatList';
import type { Module } from '../lib/types';

interface SidebarProps {
  modules: Module[];
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
}

export default function Sidebar({ modules, isCollapsed = false, onToggleCollapse }: SidebarProps) {
  const navigate = useNavigate();
  const { moduleKey } = useParams<{ moduleKey: string }>();
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  const handleModuleSelect = (moduleKey: string) => {
    navigate(`/m/${moduleKey}`);
    setIsMobileOpen(false);
  };

  const handleChatSelect = (chatId: number) => {
    if (moduleKey) {
      navigate(`/m/${moduleKey}/c/${chatId}`);
      setIsMobileOpen(false);
    }
  };

  const sidebarContent = (
    <div className="flex flex-col h-full bg-gray-50 border-r border-gray-200">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <h1 className="text-xl font-bold text-gray-900">Software Dev OS</h1>
        {onToggleCollapse && (
          <Button
            variant="ghost"
            size="icon"
            onClick={onToggleCollapse}
            className="lg:hidden"
          >
            <X size={20} />
          </Button>
        )}
      </div>

      {/* Module List */}
      <div className="flex-1 overflow-hidden">
        <ModuleList
          modules={modules}
          activeModuleKey={moduleKey}
          onModuleSelect={handleModuleSelect}
        />
        
        <Separator className="mx-4 my-2" />
        
        {/* Chat History */}
        {moduleKey && (
          <ChatList
            moduleKey={moduleKey}
            onChatSelect={handleChatSelect}
          />
        )}
      </div>
    </div>
  );

  return (
    <>
      {/* Mobile menu button */}
      <Button
        variant="ghost"
        size="icon"
        onClick={() => setIsMobileOpen(true)}
        className="lg:hidden fixed top-4 left-4 z-50"
      >
        <Menu size={20} />
      </Button>

      {/* Mobile sidebar overlay */}
      {isMobileOpen && (
        <div className="lg:hidden fixed inset-0 z-40 bg-black bg-opacity-50" onClick={() => setIsMobileOpen(false)} />
      )}

      {/* Mobile sidebar */}
      <div className={`
        lg:hidden fixed left-0 top-0 z-50 h-full w-80 transform transition-transform duration-300 ease-in-out
        ${isMobileOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        {sidebarContent}
      </div>

      {/* Desktop sidebar */}
      <div className={`
        hidden lg:block w-80 flex-shrink-0
        ${isCollapsed ? 'w-20' : 'w-80'}
      `}>
        {sidebarContent}
      </div>
    </>
  );
}
