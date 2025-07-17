# Headless PM Dashboard

A real-time web dashboard for the Headless PM project management system, built with Next.js 15.4.1 and TypeScript.

## Features

### Task Management
- **Enhanced Task Creation UI**: Complete Epic → Feature → Task creation flow from single dialog
- **Modal-on-Modal Interface**: + icons beside dropdowns open creation modals
- **Automatic Parent Selection**: Newly created Epics and Features are automatically selected
- **Hierarchy Creation**: Create entire project hierarchy without pre-existing entities
- **Real-time Updates**: Live task status updates and progress tracking

### Project Overview
- Real-time project metrics and analytics
- Task progress visualization with status boards
- Agent activity monitoring
- Service health status tracking

### User Experience
- **Responsive Design**: Works on desktop and mobile devices
- **TypeScript Integration**: Full type safety throughout the application
- **Modern UI Components**: Built with Tailwind CSS and shadcn/ui
- **Real-time Data**: Automatic polling for live updates

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm, yarn, pnpm, or bun
- Headless PM API server running on port 6969

### Installation & Setup

1. **Install dependencies**:
   ```bash
   cd dashboard
   npm install
   ```

2. **Configure environment**:
   ```bash
   # Create environment file
   cp .env.example .env.local
   
   # Edit .env.local with your API configuration
   NEXT_PUBLIC_API_URL=http://localhost:6969
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

4. **Access dashboard**:
   Open [http://localhost:3001](http://localhost:3001) in your browser

### Production Deployment

```bash
# Build for production
npm run build

# Start production server
npm start
```

## Architecture

### Technology Stack
- **Framework**: Next.js 15.4.1 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui components
- **State Management**: React Query (TanStack Query)
- **API Integration**: Axios client with automatic retries
- **Build Tool**: Turbopack (development) / Webpack (production)

### Key Components

#### Task Management
- `TaskCreateDialog`: Main task creation interface
- `EpicCreateModal`: Epic creation modal with form validation
- `FeatureCreateModal`: Feature creation modal with Epic context
- `TaskBoard`: Kanban-style task status visualization

#### API Integration
- `api/client.ts`: Centralized API client with proper error handling
- Automatic `dashboard-user` agent ID for API operations
- Real-time polling for live updates

### Agent Integration

The dashboard automatically uses the `dashboard-user` agent for all operations:
- **Agent ID**: `dashboard-user`
- **Role**: `project_pm` (Project Manager)
- **Level**: `senior`
- **Permissions**: Can create Epics, Features, and Tasks

This agent is automatically created during database initialization.

## Development

### Project Structure
```
dashboard/
├── src/
│   ├── app/                    # Next.js App Router pages
│   ├── components/            # React components
│   │   ├── tasks/            # Task-related components
│   │   └── ui/               # Reusable UI components
│   ├── lib/                  # Utilities and API client
│   │   └── api/             # API integration
│   └── types/               # TypeScript type definitions
├── public/                   # Static assets
└── package.json              # Dependencies and scripts
```

### Available Scripts

- `npm run dev` - Start development server with Turbopack
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript compiler

### Development Features

- **Hot Reload**: Instant updates during development
- **TypeScript**: Full type safety with proper error handling
- **ESLint**: Code quality and consistency enforcement
- **Automatic API Polling**: Live data updates every 30 seconds
- **Error Boundaries**: Graceful error handling throughout the app

## Integration

### API Requirements
- Headless PM API server running on port 6969
- Database initialized with default project and dashboard-user agent
- Proper CORS configuration for dashboard domain

### Service Management
The dashboard integrates with the Headless PM service management system:
```bash
# Start all services including dashboard
./scripts/manage_services.sh start

# Check dashboard status
./scripts/manage_services.sh status dashboard
```

## Troubleshooting

### Common Issues

1. **API Connection Errors**:
   - Verify API server is running on port 6969
   - Check CORS configuration
   - Ensure `dashboard-user` agent exists in database

2. **Build Errors**:
   - Clear Next.js cache: `rm -rf .next`
   - Reinstall dependencies: `rm -rf node_modules && npm install`

3. **Development Issues**:
   - Check Node.js version (requires 18+)
   - Verify environment variables in `.env.local`

### Logging
- Browser console shows API requests and errors
- Network tab in DevTools shows API communication
- Server logs available in `../run/dashboard.log`

## Contributing

When contributing to the dashboard:

1. Follow TypeScript strict mode requirements
2. Use existing UI components from `components/ui/`
3. Maintain consistent API error handling patterns
4. Test task creation flow thoroughly
5. Ensure responsive design principles

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [shadcn/ui Components](https://ui.shadcn.com/)
- [React Query](https://tanstack.com/query/latest)