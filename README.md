# FastAPI Authentication and CRUD Application

A simple web application built with FastAPI that demonstrates user authentication using JWT tokens and basic CRUD operations with PostgreSQL database.

## Features

- User registration and authentication
- JWT token-based authentication
- PostgreSQL database integration
- CRUD operations for items
- Clean and responsive UI
- Secure password hashing

## Prerequisites

- Python 3.8+
- PostgreSQL
- pip (Python package manager)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd fastapi-auth-middleware
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a PostgreSQL database named `fastapi_auth_db`

5. Update the `.env` file with your database credentials and secret key:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/fastapi_auth_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Running the Application

1. Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

2. Open your browser and navigate to:
```
http://localhost:8000
```

## API Documentation

Once the application is running, you can access the API documentation at:
```
http://localhost:8000/docs
```

## Project Structure

```
fastapi-auth-middleware/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── auth.py
│   ├── models.py
│   └── database.py
├── static/
│   ├── styles.css
│   └── script.js
├── templates/
│   ├── login.html
│   └── items.html
├── requirements.txt
├── .env
└── README.md
```

## Security Notes

- The secret key in the `.env` file should be kept secure and never committed to version control
- Passwords are hashed using bcrypt before storing in the database
- JWT tokens are used for authentication
- Database credentials should be properly secured 