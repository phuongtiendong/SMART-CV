# Smart CV - CV Analysis & Ranking System

A production-ready web application for analyzing and ranking CVs against job descriptions using AI/LLM technology.

## Features

- **Multiple Job Positions**: Create and manage multiple job positions, each with its own job description
- **Independent CV Ranking**: Each job has its own CV ranking/scoring system
- **Modern Web UI**: Clean, responsive interface built with HTML, CSS, and JavaScript
- **CV Processing**: Upload PDF CVs, extract text via OCR, parse with LLM, and score against job requirements
- **Real-time Analysis**: View detailed scoring breakdowns with explanations
- **Ranking Dashboard**: See ranked candidates sorted by score

## Project Structure

```
smart_cv/
├── backend/                 # FastAPI backend application
│   ├── models/             # Database models and schema
│   │   ├── __init__.py
│   │   └── database.py    # Database initialization and CRUD operations
│   ├── services/           # Business logic services
│   │   ├── __init__.py
│   │   ├── cv_processor.py    # CV processing service (OCR, parsing, scoring)
│   │   └── ranking_service.py # Ranking service
│   ├── routes/             # API routes/controllers
│   │   ├── __init__.py
│   │   ├── jobs.py         # Job management endpoints
│   │   └── cvs.py          # CV processing endpoints
│   └── app.py              # FastAPI application factory
├── frontend/               # Frontend application
│   ├── templates/          # HTML templates
│   │   └── index.html      # Main application page
│   └── static/            # Static assets
│       ├── css/
│       │   └── style.css   # Application styles
│       └── js/
│           └── app.js      # Frontend JavaScript
├── config.py               # Configuration and constants
├── ocr.py                  # OCR functions for PDF text extraction
├── llm_processor.py        # LLM-based CV parsing
├── marker.py               # Scoring logic (core ranking algorithm)
├── prompt.py               # LLM prompts
├── utils.py                # Utility functions
├── requirements.txt        # Python dependencies
└── run.py                  # Application entry point
```

## Architecture

### Backend Architecture

- **Models Layer** (`backend/models/`): Database schema and data access layer
  - Handles all database operations
  - Manages job and CV analysis data
  
- **Services Layer** (`backend/services/`): Business logic
  - `CVProcessor`: Orchestrates OCR, parsing, and scoring
  - `RankingService`: Manages candidate rankings
  
- **Routes Layer** (`backend/routes/`): API endpoints
  - RESTful API for jobs and CVs
  - Handles HTTP requests/responses
  - Input validation and error handling

### Frontend Architecture

- **Single Page Application**: Vanilla JavaScript (no framework dependencies)
- **RESTful API Communication**: Fetches data from FastAPI backend
- **Component-based UI**: Modular, reusable UI components
- **Responsive Design**: Works on desktop and mobile devices

### Database Schema

- **jobs table**: Stores job positions
  - `id`: Primary key
  - `title`: Job title
  - `description`: Job description (JD)
  - `created_at`, `updated_at`: Timestamps

- **analyses table**: Stores CV analysis results
  - `id`: Primary key
  - `job_id`: Foreign key to jobs table
  - `name`, `email`, `phone`: Candidate information
  - `score`: Total score (0-100)
  - `jd_text`: Job description used for scoring
  - `cv_data`: JSON data with full analysis
  - `created_at`: Timestamp

## Installation

1. **Clone the repository** (if applicable) or navigate to the project directory

2. **Create a virtual environment** (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:
   - `GOOGLE_VISION_API_KEY`: Google Vision API key for OCR
   - `GOOGLE_GENAI_API_KEY`: Google Generative AI API key for LLM
   
   Or edit `config.py` directly (not recommended for production).

## Running the Application

Start the FastAPI development server:

```bash
python run.py
```

The application will be available at:
- **Main app**: `http://localhost:8000`
- **API documentation**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative docs**: `http://localhost:8000/redoc` (ReDoc)

## Usage

### 1. Create a Job Position

1. Navigate to the "Job Management" tab
2. Click "Create New Job"
3. Enter job title and description
4. Save the job

### 2. Upload and Analyze CVs

1. Go to the "Upload CV" tab
2. Select a job position from the dropdown
3. Choose a PDF CV file
4. Click "Analyze CV"
5. View the detailed scoring breakdown

### 3. View Rankings

1. Open the "Ranking" tab
2. Optionally filter by a specific job position
3. View candidates ranked by score (highest to lowest)

## Core Scoring Logic

The scoring system evaluates CVs across 5 categories:

1. **Education**: Relevance of educational background
2. **Experience**: Relevance and recency of work experience
3. **Skills**: Match of skills with job requirements
4. **Awards**: Relevance of awards and certifications
5. **Languages**: Language proficiency match

Each category is scored 0-100 by the LLM, and the total score is the average of all categories.

**Note**: The core scoring logic in `marker.py` and `prompt.py` remains unchanged - only wrapped and extended to support multiple jobs.

## API Endpoints

### Interactive API Documentation

FastAPI automatically generates interactive API documentation:
- **Swagger UI**: `http://localhost:5000/docs`
- **ReDoc**: `http://localhost:5000/redoc`

### Jobs

- `GET /api/jobs` - List all jobs
- `GET /api/jobs/{job_id}` - Get a specific job
- `POST /api/jobs` - Create a new job
  - Body: `{"title": string, "description": string}`
- `PUT /api/jobs/{job_id}` - Update a job
  - Body: `{"title": string, "description": string}`
- `DELETE /api/jobs/{job_id}` - Delete a job

### CVs

- `POST /api/cvs/process` - Process and score a CV
  - Form data: `file` (PDF), `job_id` (integer)
- `GET /api/cvs/ranking` - Get ranking
  - Query params: `job_id` (optional integer)

## Design Decisions

### Framework Choice: Flask

- **Lightweight**: Minimal overhead, fast development
- **Python-native**: Seamless integration with existing Python code
- **Flexible**: Easy to extend and customize
- **Production-ready**: Can be deployed with Gunicorn/uWSGI

### Frontend: Vanilla JavaScript

- **No build step**: Simple deployment, easy to understand
- **Fast**: No framework overhead
- **Maintainable**: Clear, straightforward code
- **Compatible**: Works everywhere

### Database: SQLite

- **Simple**: No separate database server needed
- **Sufficient**: Handles the expected data volume
- **Portable**: Easy to backup and migrate
- **Upgradeable**: Can migrate to PostgreSQL/MySQL if needed

### Multiple Jobs Architecture

- **Foreign Key Relationship**: Each CV analysis is linked to a job via `job_id`
- **Independent Rankings**: Rankings are filtered by `job_id` when requested
- **Job Management**: Full CRUD operations for jobs
- **Data Isolation**: Each job's CVs are stored separately but can be viewed together

## Extending the Application

### Adding New Scoring Categories

1. Add prompt function in `prompt.py`
2. Update `marker.py` to handle the new category
3. Update `cv_processor.py` to include the new category in scoring
4. Update frontend to display the new category

### Changing UI Framework

The frontend is decoupled from the backend. You can replace the vanilla JS frontend with React, Vue, or any other framework by:
1. Keeping the same API endpoints
2. Replacing `frontend/static/js/app.js` with your framework code
3. Updating templates if needed

### Migrating to Production Database

To use PostgreSQL or MySQL:
1. Update `backend/models/database.py` to use SQLAlchemy or another ORM
2. Change connection strings in `config.py`
3. Run migrations to create tables

## Error Handling

- **Backend**: All routes return JSON with `success` and `error` fields
- **Frontend**: Displays user-friendly error messages
- **Validation**: Client-side and server-side validation
- **Logging**: All errors logged to `logs/app.log`

## Security Considerations

- **API Keys**: Should be stored in environment variables, not in code
- **File Upload**: Currently accepts PDFs only; add file size limits in production
- **Input Validation**: All inputs validated on backend
- **SQL Injection**: Using parameterized queries prevents SQL injection

## Future Enhancements

- User authentication and authorization
- Export rankings to CSV/Excel
- Batch CV upload
- Advanced filtering and search
- Email notifications
- Integration with ATS systems

## License

[Specify your license here]

## Contributing

[Add contribution guidelines if applicable]
