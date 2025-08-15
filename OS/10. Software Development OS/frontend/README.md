# Software Development OS Frontend

A modern React frontend for the Software Development OS, featuring a chat interface with module-based organization, file uploads, and markdown support.

## Features

- **Module-based Organization**: Choose from Code Quality, Project Management, DevOps, Documentation, Testing, and Security modules
- **Chat Interface**: Create and manage conversations within each module
- **File Uploads**: Drag & drop or browse to upload various file types
- **Markdown Support**: Rich message formatting with code highlighting and copy functionality
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Updates**: Messages and file uploads update in real-time

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **TailwindCSS** for styling
- **shadcn/ui** components for consistent UI
- **TanStack Query** for server state management
- **React Router** for navigation
- **Axios** for API communication
- **React Markdown** with syntax highlighting

## Prerequisites

- Node.js 18+ 
- pnpm (recommended) or npm

## Installation

1. Clone the repository and navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
pnpm install
# or
npm install
```

3. Set up environment variables:
```bash
cp env.example .env
```

Edit `.env` and set your backend API URL:
```env
VITE_API_BASE_URL=http://localhost:8001
```

## Development

Start the development server:
```bash
pnpm dev
# or
npm run dev
```

The app will be available at `http://localhost:3000`

## Building for Production

Build the application:
```bash
pnpm build
# or
npm run build
```

Preview the production build:
```bash
pnpm preview
# or
npm run preview
```

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Sidebar.tsx     # Left sidebar with modules and chat history
│   ├── ModuleList.tsx  # List of available modules
│   ├── ChatList.tsx    # Chat history for selected module
│   ├── NewChatButton.tsx # Button to create new chats
│   ├── ChatView.tsx    # Message display area
│   ├── MessageBubble.tsx # Individual message component
│   ├── Composer.tsx    # Message input and file upload
│   ├── FileBadge.tsx   # File upload status indicator
│   └── Toolbar.tsx     # Top toolbar with title and actions
├── pages/              # Page components
│   ├── Home.tsx        # Landing page (redirects to first module)
│   ├── ModulePage.tsx  # Module overview page
│   └── ChatPage.tsx    # Chat conversation page
├── ui/                 # shadcn/ui components
├── lib/                # Utilities and API
│   ├── api.ts          # API client and functions
│   ├── types.ts        # TypeScript type definitions
│   ├── query.ts        # React Query configuration
│   └── utils.ts        # Utility functions
└── styles.css          # Global styles and Tailwind imports
```

## API Endpoints

The frontend expects the following backend API endpoints:

- `GET /modules` - List available modules
- `GET /modules/:moduleKey/chats` - List chats for a module
- `POST /modules/:moduleKey/chats` - Create a new chat
- `GET /chats/:chatId/messages` - Get messages for a chat
- `POST /chats/:chatId/messages` - Send a message
- `POST /upload` - Upload a file
- `GET /jobs/:jobId` - Get job status (optional)

## File Upload Support

The application supports the following file types:
- Archives: `.zip`, `.tar`, `.gz`
- Code: `.diff`, `.patch`, `.md`, `.yaml`, `.yml`, `.json`, `.xml`
- Documents: `.pdf`, `.log`, `.txt`, `.info`
- Coverage: `.lcov`, `.coverage`
- Images: `.jpg`, `.png`

## Contributing

1. Follow the existing code style and patterns
2. Ensure TypeScript types are properly defined
3. Test your changes thoroughly
4. Update documentation as needed

## License

This project is part of the Software Development OS.
