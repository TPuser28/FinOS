import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import type { Module } from '../lib/types';

interface HomeProps {
  modules: Module[];
}

export default function Home({ modules }: HomeProps) {
  const navigate = useNavigate();

  useEffect(() => {
    if (modules.length > 0) {
      navigate(`/m/${modules[0].key}`, { replace: true });
    }
  }, [modules, navigate]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Redirecting to {modules[0]?.name || 'first module'}...</p>
      </div>
    </div>
  );
}
