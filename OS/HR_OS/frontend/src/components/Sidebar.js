import React from 'react';
import { 
  Users, 
  HelpCircle, 
  MessageSquare, 
  BookOpen, 
  UserPlus,
  Settings
} from 'lucide-react';
import './Sidebar.css';

// Icon mapping
const iconMap = {
  Users,
  HelpCircle,
  MessageSquare,
  BookOpen,
  UserPlus
};

const Sidebar = ({ modules, activeModule, onModuleSelect }) => {
  const getIcon = (iconName, isActive) => {
    const IconComponent = iconMap[iconName] || Users;
    return (
      <IconComponent 
        size={20} 
        className={isActive ? 'text-blue-600' : 'text-gray-600'}
      />
    );
  };

  return (
    <div className="sidebar">
      {/* Header */}
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <div className="logo-icon">
            <Users size={24} className="text-blue-600" />
          </div>
          <div className="logo-text">
            <h1 className="logo-title">HR OS</h1>
            <p className="logo-subtitle">Operating System</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        <div className="nav-section">
          <h2 className="nav-section-title">Modules</h2>
          <ul className="nav-list">
            {modules.map((module) => (
              <li key={module.id}>
                <button
                  onClick={() => onModuleSelect(module.id)}
                  className={`nav-item ${activeModule === module.id ? 'nav-item-active' : ''}`}
                  title={module.description}
                >
                  <div className="nav-item-icon">
                    {getIcon(module.icon, activeModule === module.id)}
                  </div>
                  <div className="nav-item-content">
                    <span className="nav-item-name">{module.name}</span>
                    <span className="nav-item-description">{module.description}</span>
                  </div>
                </button>
              </li>
            ))}
          </ul>
        </div>
      </nav>

      {/* Footer */}
      <div className="sidebar-footer">
        <button className="settings-button">
          <Settings size={18} className="text-gray-600" />
          <span>Settings</span>
        </button>
        <div className="user-info">
          <div className="user-avatar">
            <span>HR</span>
          </div>
          <div className="user-details">
            <span className="user-name">HR Manager</span>
            <span className="user-role">Administrator</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
