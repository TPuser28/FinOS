import { useQuery } from '@tanstack/react-query';
import { listModules } from '../lib/api';
import { Skeleton } from '../ui/Skeleton';
import type { Module } from '../lib/types';

interface ModuleListProps {
  modules: Module[];
  activeModuleKey?: string;
  onModuleSelect: (moduleKey: string) => void;
}

export default function ModuleList({ modules, activeModuleKey, onModuleSelect }: ModuleListProps) {
  const { data: fetchedModules, isLoading } = useQuery({
    queryKey: ['modules'],
    queryFn: listModules,
    initialData: modules,
  });

  if (isLoading) {
    return (
      <div className="p-4 space-y-2">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="h-10 w-full" />
        ))}
      </div>
    );
  }

  const displayModules = fetchedModules || modules;

  return (
    <div className="p-4">
      <h2 className="text-sm font-semibold text-gray-700 mb-3">Modules</h2>
      <div className="space-y-1">
        {displayModules.map((module) => (
          <button
            key={module.key}
            onClick={() => onModuleSelect(module.key)}
            className={`
              w-full text-left px-3 py-2 rounded-lg text-sm font-medium transition-colors
              ${activeModuleKey === module.key
                ? 'bg-blue-100 text-blue-900 border border-blue-200'
                : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
              }
            `}
          >
            {module.name}
          </button>
        ))}
      </div>
    </div>
  );
}
