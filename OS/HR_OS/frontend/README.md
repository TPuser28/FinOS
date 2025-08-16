# HR Operating System - Frontend

A modern React.js frontend for the HR Operating System, providing an intuitive chat-based interface for managing HR operations.

## Features

### 🏢 **Multi-Module Architecture**
- **Recruitment Module**: Resume screening, interview scheduling, candidate management
- **HR Support Module**: Employee tickets, policy queries, helpdesk support
- **Feedback Module**: Employee surveys, sentiment analysis, engagement reports
- **Learning & Development Module**: Personalized learning paths, skill development
- **Onboarding Module**: New hire workflows, milestone tracking

### 💬 **Chat Interface**
- Real-time messaging with AI-powered HR assistants
- File upload support (PDF, DOC, TXT, CSV, Excel, Images)
- Conversation persistence with localStorage
- Auto-scrolling and responsive design
- Professional ChatGPT-like interface

### 🎨 **Modern Design**
- Clean, professional UI with dark sidebar and light chat panel
- Responsive layout that works on desktop, tablet, and mobile
- Smooth animations and transitions
- Accessible design with proper focus states

## Technology Stack

- **React 18** - Modern React with hooks
- **Lucide React** - Beautiful icons
- **CSS3** - Custom styling with modern CSS features
- **localStorage** - Client-side conversation persistence

## Getting Started

### Prerequisites
- Node.js 16+ 
- npm or yarn

### Installation

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Start the development server**
   ```bash
   npm start
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000 (make sure backend is running)

### Building for Production

```bash
npm run build
```

## Project Structure

```
src/
├── components/
│   ├── Sidebar.js          # Left navigation sidebar
│   ├── Sidebar.css         # Sidebar styles
│   ├── ChatPanel.js        # Main chat interface
│   ├── ChatPanel.css       # Chat panel styles
│   ├── ChatMessage.js      # Individual message component
│   ├── ChatMessage.css     # Message styles
│   ├── ChatInput.js        # Message input with file upload
│   └── ChatInput.css       # Input styles
├── App.js                  # Main application component
├── App.css                 # Global application styles
├── index.js                # React entry point
└── index.css               # Base styles
```

## API Integration

The frontend communicates with the FastAPI backend through REST endpoints:

- `POST /chat/{module_name}` - Send messages to specific HR modules
- Request format: `{ "text": "user message" }`
- Response format: `{ "reply": "agent response" }`

### Supported Modules
- `recruitment_module`
- `hr_support_module` 
- `feedback_module`
- `lnd_module`
- `onboarding_module`

## Features in Detail

### Conversation Management
- Each module maintains its own conversation history
- Messages are automatically saved to localStorage
- Conversations persist across page refreshes and module switches

### File Upload Support
- Support for common file types: PDF, DOC, TXT, CSV, Excel, Images
- 10MB file size limit
- Visual file preview before sending
- File information display in messages

### Responsive Design
- Mobile-first approach with progressive enhancement
- Collapsible sidebar on mobile devices
- Touch-friendly interface elements
- Optimized for various screen sizes

### Accessibility
- Proper ARIA labels and roles
- Keyboard navigation support
- Focus management
- Color contrast compliance

## Customization

### Adding New Modules
1. Add module configuration to `HR_MODULES` array in `App.js`
2. Include appropriate icon from Lucide React
3. Add API endpoint mapping in `ChatPanel.js`

### Styling
- Modify CSS custom properties for consistent theming
- Update component-specific styles in individual CSS files
- Use utility classes for common styling patterns

## Development Notes

### State Management
- Uses React hooks (`useState`, `useEffect`) for state management
- Conversation state is lifted up to the App component
- LocalStorage integration for persistence

### Performance Optimizations
- Auto-scrolling with smooth behavior
- Efficient re-rendering with proper key props
- Debounced textarea auto-resize

### Browser Support
- Modern browsers (Chrome, Firefox, Safari, Edge)
- ES6+ features used throughout
- CSS Grid and Flexbox for layouts

## Contributing

1. Follow the existing code structure and naming conventions
2. Add comments for complex logic
3. Test on multiple screen sizes
4. Ensure accessibility compliance

## License

This project is part of the HR Operating System suite.
