import { useQuery } from '@tanstack/react-query';
import { listChats } from '../lib/api';
import { Skeleton } from '../ui/Skeleton';
import { ScrollArea } from '../ui/ScrollArea';


interface ChatListProps {
  moduleKey: string;
  onChatSelect: (chatId: number) => void;
}

export default function ChatList({ moduleKey, onChatSelect }: ChatListProps) {
  const { data: chats, isLoading } = useQuery({
    queryKey: ['chats', moduleKey],
    queryFn: () => listChats(moduleKey),
    enabled: !!moduleKey,
  });

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
    
    if (diffInDays === 0) return 'Today';
    if (diffInDays === 1) return 'Yesterday';
    if (diffInDays < 7) return `${diffInDays} days ago`;
    return date.toLocaleDateString();
  };

  if (isLoading) {
    return (
      <div className="p-4 space-y-2">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">Chat History</h2>
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-12 w-full" />
        ))}
      </div>
    );
  }

  if (!chats || chats.length === 0) {
    return (
      <div className="p-4">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">Chat History</h2>
        <p className="text-sm text-gray-500 text-center py-4">No chats yet</p>
      </div>
    );
  }

  return (
    <div className="p-4">
      <h2 className="text-sm font-semibold text-gray-700 mb-3">Chat History</h2>
      <ScrollArea className="h-64">
        <div className="space-y-1">
          {chats.slice(0, 30).map((chat) => (
            <button
              key={chat.id}
              onClick={() => onChatSelect(chat.id)}
              className="w-full text-left p-2 rounded-lg text-sm hover:bg-gray-100 transition-colors group"
            >
              <div className="font-medium text-gray-900 truncate">
                {chat.title || `Chat ${chat.id}`}
              </div>
              <div className="text-xs text-gray-500">
                {formatDate(chat.created_at)}
              </div>
            </button>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}
