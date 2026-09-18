API Monitoring & Observability Platform

A full-stack API monitoring and observability platform built with FastAPI, Streamlit, SQLModel, SQLite, and Docker.

The platform allows users to register, authenticate securely, create API monitors, automatically check API health, track response times and uptime, view monitoring history, and receive alerts when monitored APIs fail.

🚀 Features

🔐 Authentication & Security
User registration and login
Password hashing using Argon2
JWT-based authentication
JWT token expiration
Protected API endpoints
User-specific monitor ownership
Users cannot access monitors belonging to other users
Input validation
Environment-based secret configuration

📡 API Monitoring
Create API monitors
Update existing monitors
Enable or disable monitors
Delete monitors
Support for GET, POST, PUT, and DELETE
Configurable monitoring intervals
Automatic background monitoring
HTTP status-code tracking
Response-time measurement
Success/failure detection
Network and request error handling

📊 Observability & Analytics
Monitor health status
Uptime percentage
Total checks
Successful checks
Failed checks
Average response time
Minimum response time
Maximum response time
Historical monitoring data
Response-time charts

🚨 Alerting
Automatic alert creation when a monitor fails
Prevents duplicate unresolved alerts
Automatically resolves alerts when a monitor recovers
Dashboard view of active alerts

🖥️ Dashboard
The Streamlit dashboard provides:
Total monitor count
Active monitor count
Healthy monitor count
Failing monitor count
Monitor overview table
Current status
HTTP status code
Response time
Monitoring interval
Active alerts
Historical response-time visualization

🐳 Docker
Dockerized application
Docker Compose configuration
Separate frontend and backend services
API healthcheck
Frontend waits for the API to become healthy
Environment variable support
Persistent SQLite database volume

🏗️ Architecture

                    ┌─────────────────────┐
                    │      User / Browser │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Streamlit UI     │
                    │     Port 8501        │
                    └──────────┬──────────┘
                               │ HTTP
                               ▼
                    ┌─────────────────────┐
                    │     FastAPI API     │
                    │     Port 8000       │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
      ┌─────────────┐   ┌─────────────┐   ┌──────────────┐
      │ SQLModel /  │   │ Auth / JWT  │   │ Monitoring   │
      │ SQLite      │   │             │   │ Scheduler    │
      └─────────────┘   └─────────────┘   └──────┬───────┘
                                                  │
                                                  ▼
                                         ┌─────────────────┐
                                         │ External APIs   │
                                         │ Being Monitored │
                                         └─────────────────┘
🔄 Monitoring Flow

Monitor Created
      │
      ▼
Background Scheduler
      │
      ▼
HTTP Request Sent
      │
      ▼
Measure Response Time
      │
      ├───────────────┐
      │               │
      ▼               ▼
   Success          Failure
      │               │
      ▼               ▼
Save CheckResult   Save CheckResult
      │               │
      ▼               ▼
Resolve Alert      Create Alert
if required        if required
      │               │
      └───────┬───────┘
              ▼
        Update Monitor
              │
              ▼
        Dashboard / Analytics

🛠️ Tech Stack
Technology
Purpose
Python
Core programming language
FastAPI
REST API backend
SQLModel
ORM and database models
SQLite
Relational database
HTTPX
HTTP requests for monitoring
Pydantic
Request validation
Pwdlib + Argon2
Password hashing
Python-JOSE
JWT authentication
Streamlit
Frontend dashboard
Pandas
Data processing
Plotly
Data visualization
Pytest
Automated testing
Docker
Containerization
Docker Compose
Multi-container orchestration
Git
Version control
GitHub
Source-code hosting

📁 Project Structure
api_monitoring_platform/
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── models.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── monitors.py
│   │
│   └── services/
│       ├── __init__.py
│       ├── analytics_service.py
│       ├── auth_service.py
│       ├── monitor_service.py
│       └── scheduler_service.py
│
├── frontend/
│   └── app.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_analytics.py
│   ├── test_auth.py
│   └── test_main.py
│
├── .env.example
├── .gitignore
├── .dockerignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md

⚙️ Local Setup
1. Clone the repository
git clone https://github.com/SandeepGandlakanna/api_monitoring_platform.git
cd api_monitoring_platform

2. Create a virtual environment
python -m venv venv

3. Activate the virtual environment
Windows PowerShell:
venv\Scripts\Activate.ps1

4. Install dependencies
pip install -r requirements.txt

5. Configure environment variables
Create a .env file in the project root:
SECRET_KEY=your-random-secret-key
DATABASE_URL=sqlite:///monitoring.db

Generate a secure secret key with:
python -c "import secrets; print(secrets.token_urlsafe(32))"
Never commit the .env file to GitHub.

▶️ Running the Application Locally
Start the FastAPI backend
uvicorn backend.main:app --reload

The API will be available at:
http://127.0.0.1:8000

FastAPI interactive documentation:
http://127.0.0.1:8000/docs

Start the Streamlit frontend
Open a second terminal and activate the virtual environment.

Then run:
streamlit run frontend/app.py

The dashboard will be available at:
http://localhost:8501

🐳 Running with Docker Compose
Build and start the complete application:
docker compose up --build

The application contains two services:
FastAPI API
    ↓
http://localhost:8000

Streamlit Frontend
    ↓
http://localhost:8501

The API container includes a healthcheck.
The frontend waits until the API service reports a healthy status before starting.

Stop the application
Press:

Ctrl + C
🧪 Testing

The project includes automated tests for:
Root endpoint
Health endpoint
Invalid routes
Protected monitor endpoints
Password hashing
Wrong password handling
JWT token generation
Invalid JWT handling
Expired JWT handling
Analytics with empty monitor history

Run the complete test suite:
pytest
Current test result:
11 passed
The test suite may display dependency deprecation warnings. These warnings do not indicate test failures.

🔑 Authentication Flow
User
 │
 ▼
Register
 │
 ▼
Password hashed with Argon2
 │
 ▼
Stored in SQLite
 │
 ▼
Login
 │
 ▼
JWT access token generated
 │
 ▼
Client sends:
Authorization: Bearer <token>
 │
 ▼
FastAPI validates JWT
 │
 ▼
User identity extracted
 │
 ▼
Protected resource accessed

🔒 Authorization & Ownership
Each monitor is associated with the user who created it.
When a protected monitor endpoint is accessed:
JWT Token
    │
    ▼
Identify User
    │
    ▼
Find Monitor
    │
    ▼
Check Monitor Ownership
    │
    ├── Owner → Allow access
    │
    └── Different user → Reject request
This prevents one authenticated user from accessing another user's monitors.

📈 Monitoring Metrics
For every monitoring check, the system records:
HTTP status code
Response time
Success/failure state
Error message when applicable
Check timestamp
Historical check results are used to calculate:
Uptime percentage
Total checks
Successful checks
Failed checks
Average response time
Minimum response time
Maximum response time
Uptime calculation
Uptime % =
Successful Checks / Total Checks × 100

Its workflow is:
Start application
       │
       ▼
Start scheduler
       │
       ▼
Load active monitors
       │
       ▼
Check monitoring interval
       │
       ▼
Send HTTP request
       │
       ▼
Store result
       │
       ▼
Create or resolve alert
       │
       ▼
Wait
       │
       └──────────► Repeat

🔐 Security Considerations
The project implements several security practices:
Passwords are never stored in plain text
Argon2 password hashing
JWT authentication
JWT expiration
Protected API routes
User-level monitor ownership
Input validation
URL validation
Monitoring interval validation
Secrets stored through environment variables
.env excluded from Git
Database file excluded from Git
Docker environment configuration

📊 Observability Concepts Demonstrated
This project demonstrates several practical observability concepts:
Availability
Tracks whether monitored APIs are responding successfully.
Latency
Measures how long each API request takes.
Errors
Records failed HTTP requests and error information.
Historical Data
Stores monitoring results so that API behavior can be analyzed over time.
Alerting
Creates alerts when monitored services fail and resolves them after recovery.

🎯 Project Goals
This project was built to demonstrate practical experience with:
REST API development
Backend architecture
Authentication
Authorization
Database design
SQLModel
Background processing
API monitoring
Observability
Alerting
Data analytics
Dashboard development
Automated testing
Docker containerization
Multi-service application architecture

