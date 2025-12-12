# Architecture & Design Decisions

## Overview

This document explains the key architectural decisions made during the upgrade of Smart CV from a Streamlit prototype to a production-ready web application.

## Framework Choice: FastAPI

**Decision**: Use FastAPI instead of Streamlit for the backend.

**Rationale**:
- **Modern & Fast**: Built on Starlette and Pydantic, very fast performance (comparable to Node.js and Go)
- **Type Safety**: Automatic request/response validation with Pydantic models
- **Auto Documentation**: Built-in Swagger UI and ReDoc at `/docs` and `/redoc`
- **Async Support**: Native async/await support for better performance
- **Production-ready**: Can be deployed with Uvicorn/Gunicorn
- **API-first**: Natural REST API design with automatic OpenAPI schema generation
- **Python-native**: Seamless integration with existing Python codebase, uses modern Python features

**Why FastAPI over Flask**:
- Better performance (async support, faster request handling)
- Automatic API documentation (no need to write docs separately)
- Type validation out of the box (Pydantic models)
- Modern Python features (async/await, type hints)
- Better developer experience

**Alternatives Considered**:
- Flask: Simpler but slower, no built-in validation/docs
- Django: Too heavy for this use case, more opinionated
- Node.js: Would require rewriting all Python code

## Frontend: Vanilla JavaScript

**Decision**: Use vanilla JavaScript instead of React/Vue/Angular.

**Rationale**:
- **No build step**: Simpler deployment, no webpack/vite configuration needed
- **Fast**: No framework overhead, smaller bundle size
- **Maintainable**: Easy for any developer to understand and modify
- **Compatible**: Works everywhere, no browser compatibility issues
- **Sufficient**: The application doesn't need complex state management or component reusability

**Trade-offs**:
- Less reusable components (acceptable for this application size)
- More manual DOM manipulation (acceptable given the simple UI)
- Could migrate to React/Vue later if needed without changing backend

## Database: SQLite

**Decision**: Continue using SQLite instead of PostgreSQL/MySQL.

**Rationale**:
- **Simple**: No separate database server to manage
- **Sufficient**: Handles expected data volume (thousands of CVs, not millions)
- **Portable**: Easy to backup (single file), easy to migrate
- **Zero-config**: Works out of the box
- **Upgradeable**: Can migrate to PostgreSQL later if needed (same SQL structure)

**Migration Path**: If needed later, can use SQLAlchemy with minimal code changes.

## Multiple Jobs Architecture

### Database Schema

**Decision**: Add `jobs` table with foreign key relationship to `analyses`.

**Design**:
```
jobs (1) -----> (many) analyses
```

- Each job has its own `id`, `title`, `description`
- Each CV analysis is linked to a job via `job_id` foreign key
- Cascading delete: Deleting a job deletes all its analyses

**Rationale**:
- **Data isolation**: Each job's CVs are logically separated
- **Flexible queries**: Can view all CVs or filter by job
- **Scalable**: Easy to add job-specific settings later (e.g., custom scoring weights)
- **Normalized**: Follows database normalization best practices

### API Design

**Decision**: RESTful API with separate endpoints for jobs and CVs.

**Endpoints**:
- `/api/jobs` - CRUD operations for jobs
- `/api/cvs/process` - Process a CV for a specific job
- `/api/cvs/ranking` - Get rankings (optionally filtered by job)

**Rationale**:
- **Separation of concerns**: Jobs and CVs are separate resources
- **RESTful**: Follows REST principles, easy to understand
- **Extensible**: Easy to add more endpoints (e.g., `/api/cvs/<id>` to get specific CV)

## Service Layer Pattern

**Decision**: Extract business logic into service classes.

**Structure**:
- `CVProcessor`: Handles OCR, parsing, and scoring
- `RankingService`: Manages ranking queries

**Rationale**:
- **Separation of concerns**: Routes handle HTTP, services handle business logic
- **Testable**: Services can be tested independently
- **Reusable**: Services can be used by different routes or scripts
- **Maintainable**: Business logic changes don't affect route code

## Core Scoring Logic Preservation

**Decision**: Keep the existing scoring logic unchanged, only wrap it.

**Implementation**:
- `marker.py` and `prompt.py` remain unchanged
- `CVProcessor` calls `marker.compute_score()` exactly as before
- Scoring algorithm (average of 5 categories) unchanged

**Rationale**:
- **Requirement**: Explicitly stated not to change core ranking logic
- **Risk mitigation**: Existing logic is proven, changing it could break things
- **Extensibility**: Can add new categories or modify weights later without touching core

## Error Handling Strategy

**Decision**: Consistent error handling across all layers.

**Implementation**:
- **Backend**: All routes return JSON with `{"success": bool, "error": str}` or `{"success": bool, "data": ...}`
- **Frontend**: Shows user-friendly error messages, logs technical details
- **Logging**: All errors logged to `logs/app.log` with stack traces

**Rationale**:
- **User experience**: Users see helpful messages, not technical errors
- **Debugging**: Developers can find issues in logs
- **Consistency**: Same error format everywhere

## Frontend UX Features

**Decision**: Add loading indicators, validation, and success/error messages.

**Implementation**:
- Loading spinners during API calls
- Form validation (client-side and server-side)
- Toast notifications for success/error
- Disabled buttons during processing
- Clear error messages for each field

**Rationale**:
- **User feedback**: Users know what's happening
- **Error prevention**: Validation catches errors early
- **Professional**: Makes the app feel polished and production-ready

## File Structure

**Decision**: Separate backend and frontend directories.

**Structure**:
```
backend/          # Python backend code
  models/         # Database models
  services/       # Business logic
  routes/         # API endpoints
frontend/         # Frontend code
  templates/      # HTML templates
  static/         # CSS, JS, images
```

**Rationale**:
- **Clear separation**: Easy to understand what goes where
- **Scalable**: Can add more backend/frontend code easily
- **Deployment**: Can deploy backend and frontend separately if needed
- **Team structure**: Backend and frontend developers can work independently

## Import Strategy

**Decision**: Use `sys.path` manipulation to handle imports.

**Implementation**:
- Each module adds project root to `sys.path` if needed
- Allows imports like `from backend.models.database import ...`

**Rationale**:
- **Simple**: Works without complex package setup
- **Flexible**: Can run from any directory
- **Alternative**: Could use proper Python packages, but adds complexity

**Trade-off**: Not ideal Python practice, but works for this application size.

## Configuration Management

**Decision**: Keep configuration in `config.py` with environment variable support.

**Implementation**:
- `config.py` reads from environment variables with defaults
- API keys can be set via environment variables

**Rationale**:
- **Security**: API keys not hardcoded (though defaults exist for development)
- **Flexibility**: Easy to change config without code changes
- **Simple**: No complex config management needed

**Future improvement**: Use `.env` file with python-dotenv for better security.

## Deployment Considerations

**Current setup**: Development server with Uvicorn (`uvicorn.run()`)

**Production recommendations**:
1. Use Gunicorn with Uvicorn workers: `gunicorn backend.app:create_app --workers 4 --worker-class uvicorn.workers.UvicornWorker`
2. Use Nginx as reverse proxy
3. Set `reload=False` in production
4. Use environment variables for all secrets
5. Set up proper logging (file rotation, etc.)
6. Add database backups
7. Use PostgreSQL for production (if scale requires it)
8. Enable HTTPS with SSL certificates
9. Set up rate limiting for API endpoints

## Extensibility Points

The architecture is designed to be easily extended:

1. **New scoring categories**: Add to `marker.py` and `prompt.py`
2. **Different UI framework**: Replace frontend without changing backend
3. **Different database**: Use SQLAlchemy, change connection in `config.py`
4. **Authentication**: Add Flask-Login, protect routes
5. **Batch processing**: Add new route/service for batch CV upload
6. **Export features**: Add routes to export rankings as CSV/Excel
7. **Notifications**: Add service to send emails on new CV uploads

## Testing Strategy (Future)

**Recommended approach**:
- Unit tests for services (mock LLM/OCR)
- Integration tests for routes (test API endpoints)
- Frontend tests for critical user flows

**Current state**: No tests (acceptable for MVP, should be added for production)

## Performance Considerations

**Current optimizations**:
- Database indexes on `job_id` and `score`
- Efficient queries (JOINs, proper WHERE clauses)

**Future optimizations**:
- Caching for job lists (Redis/Memcached)
- Async processing for CV analysis (Celery)
- CDN for static assets
- Database connection pooling

## Security Considerations

**Current state**:
- Input validation on backend
- Parameterized queries (SQL injection prevention)
- File type validation (PDF only)

**Future improvements**:
- Rate limiting for API endpoints
- File size limits
- Virus scanning for uploaded files
- HTTPS enforcement
- CSRF protection for forms
- Authentication and authorization
