import React from 'react';
import { User, Bot, AlertCircle, Paperclip } from 'lucide-react';
import './ChatMessage.css';

const ChatMessage = ({ message, moduleName }) => {
  const isUser = message.type === 'user';
  const isError = message.isError;

  // Format timestamp
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Format message content with basic markdown-like formatting
  const formatContent = (content) => {
    if (!content) return '';
    
    // Convert newlines to line breaks
    let formatted = content.replace(/\n/g, '<br />');
    
    // Bold text **text**
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Italic text *text*
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Code blocks ```code```
    formatted = formatted.replace(/```(.*?)```/gs, '<pre><code>$1</code></pre>');
    
    // Inline code `code`
    formatted = formatted.replace(/`(.*?)`/g, '<code>$1</code>');
    
    return formatted;
  };

  // Render file attachment
  const renderFileAttachment = (file) => {
    if (!file) return null;
    
    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    return (
      <div className="message-attachment">
        <Paperclip size={16} />
        <div className="attachment-info">
          <span className="attachment-name">{file.name}</span>
          <span className="attachment-size">{formatFileSize(file.size)}</span>
        </div>
      </div>
    );
  };

  return (
    <div className={`message ${isUser ? 'message-user' : 'message-agent'} ${isError ? 'message-error' : ''}`}>
      <div className="message-container">
        {/* Avatar */}
        <div className={`message-avatar ${isUser ? 'avatar-user' : 'avatar-agent'} ${isError ? 'avatar-error' : ''}`}>
          {isUser ? (
            <User size={16} />
          ) : isError ? (
            <AlertCircle size={16} />
          ) : (
            <Bot size={16} />
          )}
        </div>

        {/* Content */}
        <div className="message-content">
          <div className="message-header">
            <span className="message-sender">
              {isUser ? 'You' : (isError ? 'System' : moduleName || 'Assistant')}
            </span>
            <span className="message-time">
              {formatTime(message.timestamp)}
            </span>
          </div>
          
          {/* File attachment */}
          {message.file && renderFileAttachment(message.file)}
          
          {/* Message text */}
          {message.content && (
            <div 
              className="message-text"
              dangerouslySetInnerHTML={{ __html: formatContent(message.content) }}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
