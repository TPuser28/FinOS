import { Routes, Route, Navigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useEffect } from 'react';

import { listModules } from './lib/api';
import type { Module } from './lib/types';

// Explicit imports with type declarations
import Home from './pages/Home';
import ModulePage from './pages/ModulePage';
import ChatPage from './pages/ChatPage';

function App() {
  const { data: modules, isLoading, error } = useQuery({
    queryKey: ['modules'],
    queryFn: listModules,
    staleTime: 0, // Always consider data stale
    gcTime: 0, // Don't cache data (new property name)
  });

  // Debug logging
  console.log('App.tsx - modules data:', modules);
  console.log('App.tsx - modules type:', typeof modules);
  console.log('App.tsx - modules isArray:', Array.isArray(modules));
  console.log('App.tsx - isLoading:', isLoading);
  console.log('App.tsx - error:', error);

  // Temporary fix: handle case where modules is returned as string
  let processedModules = modules;
  if (typeof modules === 'string') {
    try {
      console.log('App.tsx - Attempting to parse string as JSON...');
      processedModules = JSON.parse(modules);
      console.log('App.tsx - Successfully parsed string to:', processedModules);
    } catch (parseError) {
      console.error('App.tsx - Failed to parse string as JSON:', parseError);
      processedModules = [];
    }
  }

  // Manual API test
  useEffect(() => {
    console.log('App.tsx - Testing manual API call...');
    listModules().then(data => {
      console.log('App.tsx - Manual API call result:', data);
      console.log('App.tsx - Manual API call result type:', typeof data);
      console.log('App.tsx - Manual API call result isArray:', Array.isArray(data));
      if (typeof data === 'string') {
        console.log('App.tsx - WARNING: API returned string instead of array!');
        console.log('App.tsx - String content:', data);
      }
    }).catch(err => {
      console.error('App.tsx - Manual API call error:', err);
      console.error('App.tsx - Error response:', err.response);
      if (err.response) {
        console.error('App.tsx - Response status:', err.response.status);
        console.error('App.tsx - Response headers:', err.response.headers);
        console.error('App.tsx - Response data:', err.response.data);
      }
    });
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  if (!processedModules || processedModules.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg text-red-600">No modules available</div>
        <div className="text-sm text-gray-500 mt-2">Debug: modules = {JSON.stringify(modules)}</div>
        <div className="text-sm text-gray-500 mt-2">Debug: processedModules = {JSON.stringify(processedModules)}</div>
      </div>
    );
  }

  return (
    <Routes>
      <Route path="/" element={<Home modules={processedModules} />} />
      <Route path="/m/:moduleKey" element={<ModulePage modules={processedModules} />} />
      <Route path="/m/:moduleKey/c/:chatId" element={<ChatPage modules={processedModules} />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
