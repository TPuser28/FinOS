import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus } from 'lucide-react';
import { Button } from '../ui/Button';
import { createChat } from '../lib/api';

export default function NewChatButton() {
  const navigate = useNavigate();
  const { moduleKey } = useParams<{ moduleKey: string }>();
  const queryClient = useQueryClient();
  const [isCreating, setIsCreating] = useState(false);

  const createChatMutation = useMutation({
    mutationFn: (title?: string) => createChat(moduleKey!, title),
    onSuccess: (data) => {
      // Invalidate chats list to refresh
      queryClient.invalidateQueries({ queryKey: ['chats', moduleKey] });
      
      // Navigate to the new chat
      navigate(`/m/${moduleKey}/c/${data.id}`);
      setIsCreating(false);
    },
    onError: (error) => {
      console.error('Failed to create chat:', error);
      setIsCreating(false);
    },
  });

  const handleCreateChat = () => {
    if (!moduleKey) return;
    
    setIsCreating(true);
    createChatMutation.mutate(undefined);
  };

  if (!moduleKey) return null;

  return (
    <Button
      onClick={handleCreateChat}
      disabled={isCreating}
      className="flex items-center gap-2"
    >
      <Plus size={16} />
      {isCreating ? 'Creating...' : 'New Chat'}
    </Button>
  );
}
