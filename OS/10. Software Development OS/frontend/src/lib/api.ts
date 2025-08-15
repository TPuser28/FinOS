import axios from 'axios';
import type { Module, Chat, Message, UploadJob } from './types';

const api = axios.create({
  baseURL: (import.meta as any).env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API functions
export const listModules = async (): Promise<Module[]> => {
  console.log('API: Calling /modules endpoint...');
  const response = await api.get('/modules');
  console.log('API: Response received:', response);
  console.log('API: Response data:', response.data);
  return response.data;
};

export const listChats = async (moduleKey: string): Promise<Chat[]> => {
  const response = await api.get(`/modules/${moduleKey}/chats`);
  return response.data;
};

export const createChat = async (moduleKey: string, title?: string): Promise<{ id: number }> => {
  const response = await api.post(`/modules/${moduleKey}/chats`, { title });
  return response.data;
};

export const getMessages = async (chatId: number): Promise<Message[]> => {
  const response = await api.get(`/chats/${chatId}/messages`);
  // Backend returns {chat: {...}, messages: [...]} - extract just the messages array
  return response.data.messages || [];
};

export const sendMessage = async (
  chatId: number, 
  content: string, 
  attachments?: string[]
): Promise<{ id: number }> => {
  // Backend currently only supports text messages, attachments not implemented yet
  const response = await api.post(`/chats/${chatId}/messages`, { text: content });
  return response.data;
};

export const uploadFile = async (file: File): Promise<UploadJob> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getJob = async (jobId: string): Promise<{ status: string; result?: any }> => {
  const response = await api.get(`/jobs/${jobId}`);
  return response.data;
};

export default api;
