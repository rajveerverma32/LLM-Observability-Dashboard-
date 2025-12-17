
# LLM Observability Dashboard

A production-ready frontend application for monitoring and analyzing LLM operations with enterprise features.

## 🚀 Features

- **Authentication & Authorization**: Secure login with role-based access (Admin/Viewer)
- **Dashboard Analytics**: Real-time monitoring with interactive charts
  - Token usage over time
  - Latency distribution
  - Error rate trends
  - Cost estimation
- **Feedback Management**: View and analyze user feedback
- **System Settings**: Admin-only settings including Claude Haiku 4.5 toggle
- **Responsive Design**: Enterprise-grade UI with Material-UI
- **Mock API**: Ready-to-use mock data services

## 🛠️ Tech Stack

- **React 18** with TypeScript
- **Vite** - Fast build tool
- **Material-UI** - Enterprise UI components
- **React Router** - Client-side routing
- **Recharts** - Data visualization
- **Axios** - HTTP client

## 📦 Installation

```bash
npm install
```

## 🏃 Running the Application

```bash
npm run dev
```

Visit `http://localhost:5173`

## 👤 Demo Credentials

### Admin Access
- Email: `admin@company.com`
- Password: any

### Viewer Access
- Email: `user@company.com`
- Password: any

## 🏗️ Project Structure

```
src/
├── pages/
│   ├── Login.tsx          # Login page
│   ├── Dashboard.tsx      # Main dashboard with charts
│   ├── Feedback.tsx       # User feedback view
│   └── Settings.tsx       # Admin settings (Claude Haiku toggle)
├── components/
│   ├── Layout.tsx         # Main layout with navigation
│   └── ProtectedRoute.tsx # Route protection component
├── services/
│   └── api.ts            # Mock API services with Axios
├── context/
│   └── AuthContext.tsx   # Authentication context
├── routes/
│   └── index.tsx         # Route configuration
├── types/
│   └── index.ts          # TypeScript interfaces
└── App.tsx               # Root component
```

## 🔑 Key Features

### Role-Based Access Control
- **Admin**: Full access to all features including settings
- **Viewer**: Read-only access to dashboard and feedback

### Dashboard Metrics
- Total tokens consumed
- Total cost estimation
- Average latency
- Error rate percentage

### Settings Panel (Admin Only)
- Enable/Disable Claude Haiku 4.5 for all clients
- Configure max tokens per request
- Toggle response caching

## 🔄 API Integration

The app currently uses mock data from `services/api.ts`. To integrate with a real backend:

1. Update `API_BASE_URL` in `api.ts`
2. Replace mock functions with real API calls
3. Update authentication logic in `AuthContext.tsx`

## 📝 Environment Variables

Create a `.env` file:

```env
VITE_API_URL=http://your-api-url.com/api
```

## 🎨 Customization

### Theme
Edit theme in `main.tsx`:
```typescript
const theme = createTheme({
  palette: {
    primary: { main: '#667eea' },
    secondary: { main: '#764ba2' },
  },
});
```

### Charts
Charts use Recharts library. Customize in `Dashboard.tsx`.

## 🚀 Build for Production

```bash
npm run build
```

Preview production build:
```bash
npm run preview
```

## 📄 License

MIT
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
=======
# LLM-Observability-Dashboard-
Real‑time monitoring of LLM calls (token usage, latency, errors, user feedback) and Interactive charts, alerts, and exportable analytics.
>>>>>>> cdc7361a718c547d8e652acb948ba165393ec24d
