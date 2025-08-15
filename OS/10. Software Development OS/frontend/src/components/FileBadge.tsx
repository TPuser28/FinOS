import { X, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { Button } from '../ui/Button';
import type { FileUpload } from '../lib/types';

interface FileBadgeProps {
  fileUpload: FileUpload;
  onRemove: () => void;
}

export default function FileBadge({ fileUpload, onRemove }: FileBadgeProps) {
  const getStatusIcon = () => {
    switch (fileUpload.status) {
      case 'uploading':
        return <Loader2 size={14} className="animate-spin" />;
      case 'uploaded':
        return <CheckCircle size={14} className="text-green-500" />;
      case 'failed':
        return <XCircle size={14} className="text-red-500" />;
      default:
        return null;
    }
  };

  const getStatusText = () => {
    switch (fileUpload.status) {
      case 'uploading':
        return 'Uploading...';
      case 'uploaded':
        return 'Uploaded';
      case 'failed':
        return 'Failed';
      default:
        return '';
    }
  };

  const getStatusColor = () => {
    switch (fileUpload.status) {
      case 'uploading':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'uploaded':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full border text-xs font-medium ${getStatusColor()}`}>
      {getStatusIcon()}
      <span className="truncate max-w-32">{fileUpload.filename || fileUpload.file.name}</span>
      <span className="text-xs opacity-75">({getStatusText()})</span>
      <Button
        variant="ghost"
        size="sm"
        onClick={onRemove}
        className="h-4 w-4 p-0 hover:bg-transparent"
      >
        <X size={12} />
      </Button>
    </div>
  );
}
