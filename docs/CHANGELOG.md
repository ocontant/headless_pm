# Headless PM Changelog

This document tracks major changes and updates to the Headless PM system.

## Recent Major Updates (July 2025)

### 🎯 UI/UX Enhancements and Permission Fixes
**Date**: July 20, 2025  
**Commits**: `08935fc`, `a3e8681`, `7eb597a`, `59c2498`, `6f707ad`, `dedcc6f`, `f4a815f`, `e0d9a63`

#### 🚀 Dashboard User Auto-Creation and Permission Management
- **Self-Healing Architecture**: Auto-creates dashboard-user for all projects on startup
- **Permission Fixes**: dashboard-user now has UI_ADMIN role with full create/edit permissions
- **Project Migration**: Automatic creation of dashboard-user for existing projects
- **Role Cleanup**: Eliminated legacy PM references, replaced with PROJECT_PM throughout codebase

#### 🎨 Enhanced User Interface
- **Auto-Selection**: Newly created epics/features automatically selected in dropdowns
- **Color Accessibility**: Replaced poor-contrast colors with WCAG-compliant alternatives
- **Error Boundaries**: Comprehensive error handling with graceful fallback UI
- **Responsive Layout**: Improved layouts with proper text truncation and overflow handling
- **Unified Edit Experience**: Consistent edit-mode patterns across all task management interfaces

#### 🐛 Critical Bug Fixes
- **Console Logging**: Fixed infinite "Acting as Agent: dashboard-user" loop
- **Select Component**: Fixed empty string validation errors in Select components
- **Project Filtering**: Enhanced task filtering with proper project context isolation
- **Service Startup**: Fixed virtual environment activation in background services
- **API Field Matching**: Corrected frontend/backend field name mismatches (assigned_role → target_role)

#### 🔧 Technical Improvements
- **Project-Independent Filtering**: Advanced task filtering without global context coupling
- **Task Creation**: Added branch field requirement and proper validation
- **Error Recovery**: Enhanced form validation with clear recovery options
- **Service Management**: Improved reliability of background service startup

### 🎯 Version 2.0.0 Release
**Date**: July 17, 2025  
**Commit**: Latest

#### 🚀 Major Version Bump
- **Version Update**: Bumped from 1.0.0 to 2.0.0 across all services
- **Breaking Changes**: Multi-project architecture requires database migration
- **API Compatibility**: New project endpoints and enhanced functionality
- **Service Management**: Complete overhaul of service management system

#### 📦 Updated Components
- **Main API**: FastAPI application version updated to 2.0.0
- **Dashboard**: Next.js dashboard version updated to 2.0.0
- **MCP Servers**: All MCP server implementations updated to 2.0.0
- **Health Endpoints**: Version reporting updated across all services

### 📚 Documentation Updates
**Date**: July 17, 2025  
**Commit**: `1bb0119`

#### ✅ New Documentation
- **PROJECT_MANAGEMENT.md**: Comprehensive guide for multi-project architecture
- **CHANGELOG.md**: Detailed tracking of system changes and updates
- **Updated API Reference**: Added project management endpoints documentation
- **Enhanced Setup Guides**: Updated for new service management system

#### 🔄 Documentation Updates
- **CLAUDE.md**: Updated startup instructions to use new service management scripts
- **LLM_AGENT_SETUP.md**: Added latest features and updated prerequisites
- **API_TASK_MANAGEMENT_REFERENCE.md**: Expanded to include project endpoints

#### 📖 Coverage
- Multi-project architecture documentation
- Service management system guides
- Database migration procedures
- Technology stack updates (Next.js 15.4.1, React 19.1.0)
- Enhanced MCP server features

### 🏗️ Service Management System Overhaul
**Date**: July 17, 2025  
**Commit**: `b3d5b71`, `bb73184`

#### ✅ New Features
- **Comprehensive Service Management**: New `scripts/` directory with full service lifecycle management
  - `manage_services.sh` - Unified service control interface  
  - `start_services.sh` - Background startup with pidfile management
  - `stop_services.sh` - Graceful shutdown with cleanup
  - `check_services.sh` - Health monitoring and status reporting
- **PID File Management**: Each service tracked with individual pidfiles in `run/` directory
- **Health Monitoring**: HTTP health checks and resource usage tracking
- **Service Logs**: Individual log files for each service with centralized access
- **Real-time Monitoring**: Watch mode for continuous service status updates

#### 🔄 Changes
- **Removed `start.sh`**: Replaced with comprehensive service management system
- **Enhanced Process Control**: Graceful SIGTERM followed by SIGKILL if needed
- **Parallel Service Startup**: Services start concurrently for faster boot times
- **Port-based Control**: Services only start if their port is defined in `.env`

#### 📚 Updated Documentation
- `docs/SERVICE_MANAGEMENT.md` - Complete service management guide
- `CLAUDE.md` - Updated startup instructions to use new service system
- `docs/LLM_AGENT_SETUP.md` - Updated prerequisites and setup instructions

### 🗄️ Multi-Project Architecture  
**Date**: July 17, 2025  
**Commit**: `bb73184`

#### ✅ New Features
- **Project Isolation**: Complete separation of epics, features, tasks, and documents by project
- **Project Management API**: Full CRUD operations for projects
- **Database Migrations**: Automated migration system with rollback support
- **Default Project**: Automatic "Headless-PM" project creation during initialization
- **Foreign Key Relationships**: Proper database constraints and referential integrity

#### 🔄 Database Changes
- New `project` table with status tracking
- Added `project_id` columns to existing tables
- Migration scripts for safe schema evolution
- Database sanity check commands

#### 📊 Web Dashboard Enhancements
- **Project Selector**: Switch between projects in navigation
- **Project Management UI**: Create, edit, and delete projects
- **Project Statistics**: Epic, feature, task, and agent counts
- **Project-specific Views**: All dashboard pages now project-aware

### ⚡ Technology Stack Updates
**Date**: July 17, 2025  
**Commit**: `bb73184`

#### 📦 Next.js Dashboard Upgrades
- **Next.js**: 15.3.4 → 15.4.1 (latest stable)
- **React**: 19.0.0 → 19.1.0  
- **@types/node**: 20.x → 24.x (latest Node.js support)
- **lucide-react**: Updated to 0.525.0
- **eslint-config-next**: Updated to match Next.js version

#### 🐍 Python Dependencies
- **Pydantic**: Version-locked to 2.11.7 for compatibility
- **SQLAlchemy**: Fixed enum deserialization issues
- **Datetime**: Updated to use `datetime.now(timezone.utc)` (deprecated `utcnow()`)

#### 🔧 Development Improvements
- **Platform Detection**: Universal setup script handles ARM64 vs x86_64
- **Virtual Environment Management**: Automatic `venv` vs `claude_venv` selection
- **Package Compatibility**: Platform-specific package versions

### 🔍 Database Fixes and Migrations
**Date**: July 17, 2025  
**Commits**: `5e7ce27`, `bb73184`

#### 🐛 Critical Fixes
- **Agent Status Column**: Added missing `status`, `current_task_id`, `last_activity` columns
- **Enum Deserialization**: Fixed SQLAlchemy enum handling with `values_callable`
- **Foreign Key Constraints**: Proper constraint handling during migrations
- **Datetime Deprecation**: Updated deprecated datetime methods

#### 🛠️ Migration System
- **Migration Runner**: `migrations/run_migrations.py` for orchestrated execution
- **Safe Schema Changes**: Backup and restore capabilities
- **Data Preservation**: Existing data maintained during schema evolution
- **Validation**: Post-migration sanity checks

### 🎯 Enhanced Agent Features
**Date**: July 17, 2025  
**Commit**: `bb73184`

#### 🤖 MCP Server Improvements
- **Token Tracking**: Usage statistics for MCP sessions
- **Multiple Protocols**: HTTP, SSE, WebSocket, STDIO support
- **Project Context**: MCP_PROJECT_ID environment variable
- **Natural Language Interface**: Enhanced command processing

#### 👥 Agent Management
- **Connection Types**: Distinguish between MCP and client connections
- **Multi-Project Support**: Agents can work across multiple projects
- **Status Tracking**: Enhanced agent status and activity monitoring
- **Role-based Permissions**: Project management restricted by role

### 🧪 Testing and Quality
**Date**: July 17, 2025  
**Commit**: `bb73184`

#### ✅ Test Improvements
- **Coverage**: Maintained 78 tests with 71% coverage
- **Database Testing**: File-based SQLite for reliable test execution
- **Enum Validation**: Comprehensive enum testing suite
- **Client Integration**: Full API integration tests

#### 🔧 Quality Assurance
- **Sanity Check Command**: `python -m src.cli.main sanity-check`
- **Health Monitoring**: Comprehensive service health checks
- **Error Handling**: Improved error reporting and debugging
- **Documentation**: Updated all relevant documentation

## Migration Guide

### From Pre-Service Management System
1. **Stop existing services**: `Ctrl+C` on any running `start.sh` processes
2. **Use new service system**: `./scripts/manage_services.sh start`
3. **Monitor services**: `./scripts/manage_services.sh status --watch`

### From Pre-Project System
1. **Automatic Migration**: Run `python migrations/run_migrations.py`
2. **Default Project**: Existing data automatically associated with "Headless-PM" project
3. **Update Client Code**: Add project context to API calls if needed
4. **MCP Configuration**: Add `MCP_PROJECT_ID` environment variable

### Dashboard Updates
1. **Clear Browser Cache**: Dashboard UI significantly updated
2. **New Features**: Explore project selector and management features
3. **Updated URLs**: Some dashboard URLs may have changed

## Breaking Changes

### Service Management
- ❌ **Removed**: `start.sh` script (replaced with service management system)
- ⚠️ **Changed**: Startup procedure now uses `./scripts/manage_services.sh start`
- ⚠️ **Changed**: Log locations moved to `run/*.log`

### Database Schema
- ⚠️ **Added**: `project_id` columns require migration
- ⚠️ **Changed**: Foreign key relationships updated
- ✅ **Backward Compatible**: Automatic migration preserves existing data

### API Changes
- ✅ **New Endpoints**: Project management endpoints added
- ✅ **Backward Compatible**: Existing endpoints unchanged
- ⚠️ **Enhanced**: Some responses now include project information

## Known Issues

### Service Management
- **Windows Support**: Service scripts designed for Unix/Linux systems
- **Port Conflicts**: Ensure ports are available before starting services
- **Permission Issues**: Scripts may need executable permissions (`chmod +x`)

### Database
- **Migration Order**: Run migrations in correct sequence using migration runner
- **Foreign Keys**: Some database systems may require manual foreign key constraint handling
- **Backup**: Always backup database before running migrations

### Dashboard
- **Cache Issues**: Clear browser cache if dashboard doesn't load properly
- **Node Version**: Requires Node.js 18+ for Next.js 15.4.1
- **Build Time**: First build may take longer due to Next.js upgrades

## Future Enhancements

### Planned Features
- **Docker Support**: Containerized deployment options
- **Authentication**: Enhanced security with user authentication
- **Real-time Updates**: WebSocket-based real-time dashboard updates
- **Backup System**: Automated database backup and restore
- **Monitoring**: Enhanced metrics and monitoring capabilities

### Technical Debt
- **Test Coverage**: Expand test coverage beyond 71%
- **Documentation**: Additional API documentation and examples
- **Performance**: Database query optimization
- **Security**: Enhanced security audit and improvements

## Support and Troubleshooting

### Common Solutions
1. **Service Issues**: Use `./scripts/manage_services.sh status --detailed`
2. **Database Problems**: Run `python -m src.cli.main sanity-check`
3. **Migration Errors**: Check `migrations/run_migrations.py` logs
4. **Dashboard Issues**: Clear cache and check `run/dashboard.log`

### Getting Help
- **Documentation**: Check `docs/` directory for specific guides
- **Logs**: Review service logs in `run/` directory
- **Debug Mode**: Set `DEBUG=1` environment variable for verbose output
- **Health Checks**: Use health monitoring tools in `scripts/`