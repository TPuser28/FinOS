import React, { useState, useRef } from 'react';
import { Send, Paperclip, X } from 'lucide-react';
import './ChatInput.css';

const ChatInput = ({ onSendMessage, disabled, placeholder = "Type a message...", moduleId = null }) => {
  const [message, setMessage] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!message.trim() && !selectedFile) return;
    if (disabled) return;

    onSendMessage(message, selectedFile);
    setMessage('');
    setSelectedFile(null);
    
    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  // Handle Enter key press
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Auto-resize textarea
  const handleTextareaChange = (e) => {
    setMessage(e.target.value);
    
    // Auto-resize
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
  };

  // Get allowed file types based on module
  const getAllowedFileTypes = () => {
    if (moduleId === 'recruitment_module') {
      return {
        accept: '.pdf',
        types: ['PDF'],
        description: 'Resume files (PDF only)'
      };
    } else if (moduleId === 'feedback_module') {
      return {
        accept: '.csv',
        types: ['CSV'],
        description: 'Feedback survey files (CSV)'
      };
    }
    return {
      accept: '.pdf,.doc,.docx,.txt,.csv,.xlsx,.xls,.png,.jpg,.jpeg,.gif,.webp',
      types: ['PDF', 'DOC', 'TXT', 'CSV', 'Excel', 'Images'],
      description: 'Various file types'
    };
  };

  // Handle file selection
  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Check file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        alert('File size must be less than 10MB');
        // Reset the input
        e.target.value = '';
        return;
      }

      // Validate file type based on module
      const allowedTypes = getAllowedFileTypes();
      const fileExtension = file.name.split('.').pop().toLowerCase();
      
      if (moduleId === 'recruitment_module') {
        if (fileExtension !== 'pdf') {
          alert(`Invalid file type. Only ${allowedTypes.description} are allowed for recruitment.`);
          // Reset the input
          e.target.value = '';
          return;
        }
      } else if (moduleId === 'feedback_module') {
        if (fileExtension !== 'csv') {
          alert(`Invalid file type. Only ${allowedTypes.description} are allowed for feedback.`);
          // Reset the input
          e.target.value = '';
          return;
        }
      }

      setSelectedFile(file);
    }
  };

  // Remove selected file
  const removeFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Format file size
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="chat-input-container">
      {/* File Preview */}
      {selectedFile && (
        <div className="file-preview">
          <div className="file-preview-content">
            <Paperclip size={16} />
            <div className="file-info">
              <span className="file-name">{selectedFile.name}</span>
              <span className="file-size">{formatFileSize(selectedFile.size)}</span>
            </div>
            <button
              type="button"
              onClick={removeFile}
              className="file-remove"
              title="Remove file"
            >
              <X size={16} />
            </button>
          </div>
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="chat-input-form">
        <div className="input-wrapper">
          {/* File Upload Button - Only show for recruitment and feedback modules */}
          {(moduleId === 'recruitment_module' || moduleId === 'feedback_module') && (
            <>
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="file-upload-button"
                disabled={disabled}
                title={`Attach ${getAllowedFileTypes().description}`}
              >
                <Paperclip size={20} />
              </button>
              
              {/* Hidden File Input */}
              <input
                ref={fileInputRef}
                type="file"
                onChange={handleFileSelect}
                className="file-input"
                accept={getAllowedFileTypes().accept}
              />
            </>
          )}

          {/* Text Input */}
          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleTextareaChange}
            onKeyPress={handleKeyPress}
            placeholder={placeholder}
            disabled={disabled}
            className="message-input"
            rows="1"
          />

          {/* Send Button */}
          <button
            type="submit"
            disabled={disabled || (!message.trim() && !selectedFile)}
            className="send-button"
            title="Send message"
          >
            <Send size={20} />
          </button>
        </div>
      </form>

      {/* Help Text */}
      <div className="input-help">
        <p>
          Press Enter to send, Shift+Enter for new line. 
          {(moduleId === 'recruitment_module' || moduleId === 'feedback_module') && (
            <>Supported files: {getAllowedFileTypes().description} (max 10MB)</>
          )}
        </p>
      </div>
    </div>
  );
};

export default ChatInput;
