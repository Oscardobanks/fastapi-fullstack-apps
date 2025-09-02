# FastAPI Projects Collection

This repository contains 5 complete FastAPI applications demonstrating various features including CRUD operations, authentication, middleware, and database integration.

## Projects Overview

### 1. University Management System

**Port: 8000**

- **Features**: Student management with grades, JWT authentication, request logging
- **Database**: SQLite with SQLModel
- **Authentication**: Token-based with users.json storage
- **Middleware**: Request logging to file
- **CORS**: Enabled for http://localhost:3000

### 2. Online Store API

**Port: 8001**

- **Features**: Product management, shopping cart, order processing
- **Database**: SQLite with SQLModel
- **Authentication**: JWT-based user system
- **Middleware**: Response time measurement
- **Backup**: Orders saved to orders.json

### 3. Career Tracker

**Port: 8002**

- **Features**: Job application tracking with search functionality
- **Database**: SQLite with SQLModel
- **Authentication**: Simple token-based authentication
- **Middleware**: User-Agent header validation
- **Search**: Filter by status, company, position

### 4. Personal Notes App

**Port: 8003**

- **Features**: Note creation, editing, deletion with backup system
- **Database**: SQLite with SQLModel
- **Middleware**: Request counting and logging
- **Backup**: Automatic backup to notes.json
- **CORS**: Multiple origins support

### 5. Address Book API

**Port: 8004**

- **Features**: Contact management with user isolation
- **Database**: SQLite with SQLModel
- **Authentication**: JWT with user registration
- **Middleware**: IP address logging
- **Security**: User-specific data access

## Quick Start

### Prerequisites

- Python 3.8+
- pip

### Installation & Running

Each project can be run independently:

```bash
# Navigate to project directory
cd university-management-system/

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m app.main
# OR
uvicorn app.main:app --reload --port 8000
```

### Project Structure (Standard for all)

```
project-name/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app and routes
│   ├── models.py        # SQLModel data models
│   ├── database.py      # Database configuration
│   ├── auth.py          # Authentication logic
│   ├── middleware.py    # Custom middleware
│   └── routers/         # Route modules (if applicable)
├── requirements.txt     # Python dependencies
└── README.md           # Project-specific documentation
```

## API Documentation

Each project automatically generates API documentation:

- Swagger UI: `http://localhost:PORT/docs`
- ReDoc: `http://localhost:PORT/redoc`

## Default Credentials

### University Management System & Career Tracker

- Username: `admin`, Password: `admin123`
- Username: `user`, Password: `user123`

### Online Store API & Address Book API

- Register new users via `/auth/register` endpoint
- Login via `/auth/login` endpoint

## Features Demonstration

### Authentication Systems

- **Simple Token**: Projects 1 & 3 (username as token)
- **JWT Tokens**: Projects 2 & 5 (proper JWT implementation)

### Middleware Examples

- **Request Logging**: University Management System
- **Response Time**: Online Store API
- **Header Validation**: Career Tracker
- **Request Counting**: Personal Notes App
- **IP Logging**: Address Book API

### Database Features

- **CRUD Operations**: All projects
- **Foreign Keys**: Projects 3 & 5
- **Search Functionality**: Projects 3, 4, & 5
- **Data Validation**: All projects with Pydantic

### Backup Systems

- **JSON Backup**: Projects 2 & 4
- **Log Files**: Projects 1, 4, & 5

## Testing the APIs

### Using curl examples:

```bash
# University Management System - Login
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "admin123"}'

# Create Student
curl -X POST "http://localhost:8000/students/" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer admin" \
     -d '{"name": "John Doe", "age": 20, "email": "john@example.com", "grades": [85, 90, 78]}'

# Online Store - Register User
curl -X POST "http://localhost:8001/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "email": "test@example.com", "password": "password123"}'
```

## Development Notes

### Security Considerations

- Change JWT secret keys in production
- Use environment variables for sensitive data
- Implement proper password policies
- Add rate limiting for production use

### Database

- SQLite files are created automatically
- For production, consider PostgreSQL or MySQL
- Database schemas are auto-created on startup

### CORS Configuration

- Currently configured for development
- Adjust origins for production deployment

## Deployment

### Using Docker (example Dockerfile):

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables

```bash
DATABASE_URL=sqlite:///./app.db  # or PostgreSQL URL
SECRET_KEY=your-secret-key-here
```

## Contributing

Each project is self-contained and can be modified independently. Key areas for enhancement:

- Add more sophisticated authentication (OAuth2, etc.)
- Implement caching with Redis
- Add comprehensive testing suites
- Enhance error handling and validation
- Add API versioning

## License

This project is for educational purposes. Feel free to use and modify as needed.
