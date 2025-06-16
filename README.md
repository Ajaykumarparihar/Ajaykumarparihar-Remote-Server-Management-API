# Ajaykumarparihar-Remote-Server-Management-API
# Remote Server Management API

A FastAPI-based REST API for managing remote Linux servers, executing commands, and monitoring activities.

## Features

- User authentication with JWT
- User profile management with photo upload
- Remote server CRUD operations
- Secure SSH command execution
- Command execution logging
- Email notifications
- Protection against dangerous commands

## Prerequisites

- Python 3.8+
- SQLite (default) or PostgreSQL
- SMTP server for email notifications

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv\Scripts\activate  
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

5. Update the `.env` file with your configuration:
- Set your database URL
- Generate a secure SECRET_KEY
- Configure SMTP settings for email notifications

## Running the Application

1. Start the development server:
```bash
uvicorn main:app --reload
```

2. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- POST `/token` - Login and get access token
- POST `/users/` - Register new user

### User Profile
- GET `/users/me/` - Get current user profile
- PUT `/users/me/` - Update user profile
- POST `/users/me/profile-photo/` - Upload profile photo

### Remote Servers
- POST `/servers/` - Add new server
- GET `/servers/` - List all servers
- GET `/servers/{server_id}` - Get server details
- PUT `/servers/{server_id}` - Update server
- DELETE `/servers/{server_id}` - Delete server

### Command Execution
- POST `/servers/{server_id}/execute` - Execute command on server
- GET `/servers/{server_id}/logs` - Get command execution logs

## Security Features

- Password hashing with bcrypt
- JWT-based authentication
- Protection against dangerous commands
- Secure storage of SSH private keys
- Input validation with Pydantic models

## Deployment

The application is ready for deployment on platforms like Render or Railway. Make sure to:

1. Set up all environment variables
2. Configure a production database
3. Set up proper SMTP credentials
4. Use a production-grade ASGI server like Gunicorn

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
