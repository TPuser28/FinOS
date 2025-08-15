export type Module = { 
  key: string; 
  name: string; 
};

export type Chat = { 
  id: number; 
  title?: string; 
  module_key: string; 
  created_at: string; 
};

export type Message = { 
  id: number; 
  chat_id: number; 
  role: "user" | "assistant"; 
  content: string; 
  created_at: string; 
};

export type UploadJob = { 
  job_id: string; 
  filename: string; 
};

export type FileUpload = {
  file: File;
  status: 'uploading' | 'uploaded' | 'failed';
  jobId?: string;
  filename?: string;
  error?: string;
};
