import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { listModules } from '../lib/api';
import NewChatButton from './NewChatButton';

export default function Toolbar() {
  const { moduleKey, chatId } = useParams<{ moduleKey: string; chatId: string }>();
  
  const { data: modules } = useQuery({
    queryKey: ['modules'],
    queryFn: listModules,
  });

  const currentModule = modules?.find(m => m.key === moduleKey);
  const title = currentModule?.name || 'Software Development OS';

  return (
    <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-white">
      <div className="flex items-center gap-4">
        <h1 className="text-xl font-semibold text-gray-900">{title}</h1>
        {chatId && (
          <span className="text-sm text-gray-500">Chat #{chatId}</span>
        )}
      </div>
      
      <div className="flex items-center gap-3">
        {moduleKey && <NewChatButton />}
      </div>
    </div>
  );
}
