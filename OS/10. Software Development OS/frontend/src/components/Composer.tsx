import { useState, useRef, useCallback } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Send, Upload, Paperclip } from 'lucide-react';
import { Button } from '../ui/Button';
import { Textarea } from '../ui/Textarea';
import { uploadFile, sendMessage } from '../lib/api';
import FileBadge from './FileBadge';
import type { FileUpload } from '../lib/types';

interface ComposerProps {
  chatId: number;
  onMessageSent?: () => void;
}

const ACCEPTED_FILE_TYPES = [
  '.zip', '.tar', '.gz', '.diff', '.patch', '.md', '.yaml', '.yml', 
  '.json', '.pdf', '.log', '.txt', '.xml', '.info', '.lcov', '.coverage',
  '.jpg', '.png'
];

export default function Composer({ chatId, onMessageSent }: ComposerProps) {
  const [message, setMessage] = useState('');
  const [fileUploads, setFileUploads] = useState<FileUpload[]>([]);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();

  const sendMessageMutation = useMutation({
    mutationFn: (data: { content: string; attachments?: string[] }) =>
      sendMessage(chatId, data.content, data.attachments),
    onSuccess: () => {
      setMessage('');
      setFileUploads([]);
      queryClient.invalidateQueries({ queryKey: ['messages', chatId] });
      onMessageSent?.();
    },
    onError: (error) => {
      console.error('Failed to send message:', error);
    },
  });

  const uploadFileMutation = useMutation({
    mutationFn: uploadFile,
    onSuccess: (data, file) => {
      setFileUploads(prev => prev.map(fu => 
        fu.file === file 
          ? { ...fu, status: 'uploaded' as const, jobId: data.job_id, filename: data.filename }
          : fu
      ));
    },
    onError: (_, file) => {
      setFileUploads(prev => prev.map(fu => 
        fu.file === file 
          ? { ...fu, status: 'failed' as const, error: 'Upload failed' }
          : fu
      ));
    },
  });

  const handleFileSelect = useCallback((files: FileList | null) => {
    if (!files) return;

    const newFileUploads: FileUpload[] = Array.from(files).map(file => ({
      file,
      status: 'uploading' as const,
    }));

    setFileUploads(prev => [...prev, ...newFileUploads]);

    // Upload each file
    newFileUploads.forEach(fileUpload => {
      uploadFileMutation.mutate(fileUpload.file);
    });
  }, [uploadFileMutation]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    handleFileSelect(files);
  }, [handleFileSelect]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
  }, []);

  const handleRemoveFile = (fileToRemove: File) => {
    setFileUploads(prev => prev.filter(fu => fu.file !== fileToRemove));
  };

  const handleSend = () => {
    if (!message.trim() && fileUploads.length === 0) return;

    const uploadedFilenames = fileUploads
      .filter(fu => fu.status === 'uploaded' && fu.filename)
      .map(fu => fu.filename!);

    sendMessageMutation.mutate({
      content: message.trim(),
      attachments: uploadedFilenames.length > 0 ? uploadedFilenames : undefined,
    });
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const hasUploadingFiles = fileUploads.some(fu => fu.status === 'uploading');
  const canSend = message.trim().length > 0 || fileUploads.some(fu => fu.status === 'uploaded');

  return (
    <div className="border-t border-gray-200 bg-white p-4">
      {/* File Uploads */}
      {fileUploads.length > 0 && (
        <div className="mb-3 flex flex-wrap gap-2">
          {fileUploads.map((fileUpload, index) => (
            <FileBadge
              key={index}
              fileUpload={fileUpload}
              onRemove={() => handleRemoveFile(fileUpload.file)}
            />
          ))}
        </div>
      )}

      {/* Message Input */}
      <div className="flex gap-3">
        <div className="flex-1 relative">
          <Textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message... (Shift+Enter for new line)"
            className="min-h-[60px] max-h-32 resize-none pr-20"
            disabled={hasUploadingFiles}
          />
          
          {/* Upload Button */}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => fileInputRef.current?.click()}
            className="absolute right-2 top-2 h-8 w-8"
            disabled={hasUploadingFiles}
          >
            <Paperclip size={16} />
          </Button>
        </div>

        <Button
          onClick={handleSend}
          disabled={!canSend || hasUploadingFiles || sendMessageMutation.isPending}
          className="px-6"
        >
          {sendMessageMutation.isPending ? (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
          ) : (
            <Send size={16} />
          )}
        </Button>
      </div>

      {/* File Input */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept={ACCEPTED_FILE_TYPES.join(',')}
        onChange={(e) => handleFileSelect(e.target.files)}
        className="hidden"
      />

      {/* Drop Zone */}
      <div
        className={`mt-2 border-2 border-dashed rounded-lg p-4 text-center transition-colors ${
          hasUploadingFiles
            ? 'border-gray-300 bg-gray-50'
            : 'border-gray-300 bg-gray-50 hover:border-gray-400 hover:bg-gray-100'
        }`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >
        <Upload size={20} className="mx-auto text-gray-400 mb-2" />
        <p className="text-sm text-gray-600">
          Drag and drop files here, or click the paperclip to browse
        </p>
        <p className="text-xs text-gray-500 mt-1">
          Supported: {ACCEPTED_FILE_TYPES.join(', ')}
        </p>
      </div>
    </div>
  );
}
