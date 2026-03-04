# Task Management System API

A robust, asynchronous Task and Team Management backend built with **FastAPI**, **SQLAlchemy 2.0**, and **PostgreSQL**. This system is designed with industry-standard patterns including Role-Based Access Control (RBAC), JWT-based authentication, and automated activity logging.



## Features

- **Asynchronous Architecture:** High-performance implementation using `FastAPI` and `SQLAlchemy` (AsyncIO).
- **Role-Based Access Control (RBAC):** Tiered permissions for `Admin`, `Manager`, and `User` roles.
- **Team Management:** Logic for creating teams, managing memberships, and tracking team-specific metrics.
- **Secure Invitation System:** JWT-signed invitation tokens with expiration logic and background email processing.
- **Task Lifecycle:** Comprehensive CRUD operations including bulk creation/deletion and soft-delete capabilities.
- **Advanced Error Handling:** Professionalized global exception handlers for database integrity, validation, and internal errors.
- **Database Migrations:** Full schema versioning using `Alembic`.
- **Activity Logging:** Middleware-style tracking of user actions for audit trails.

## Tech Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Database:** [PostgreSQL](https://www.postgresql.org/)
- **ORM:** [SQLAlchemy 2.0](https://www.sqlalchemy.org/)
- **Migrations:** [Alembic](https://alembic.sqlalchemy.org/)
- **Validation:** [Pydantic v2](https://docs.pydantic.dev/)
- **Auth:** [PyJWT](https://pyjwt.readthedocs.io/) & [Argon2](https://passlib.readthedocs.io/en/stable/lib/passlib.hash.argon2.html)

## Project Structure

```text
├── routes/             # API route handlers (v1)
├── core/               # Global config, security (JWT/Hashing), and DB setup
├── models/             # SQLAlchemy database models (Declarative Base)
├── schemas/            # Pydantic models for request/response validation
├── utils/              # Helper utilities (Emailing, logic helpers)
├── alembic/            # Database migration environment and history
└── main.py             # Application entry point and middleware config
```

## Setup & Installation

1. Clone the Repository
   
```
git clone [https://github.com/Nishant-Jain-hietch/FastAPI-Project.git](https://github.com/yourusername/task-management-api.git)
cd task-management-api
```

2. Environment Configuration

Create a .env file in the root directory:

```
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
SECRET_KEY=your_generate_secret_key_here
ALGORITHM=encryption_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES=time_in_minutes
```

3. Install Dependencies

```
pip install -r requirements.txt
```

4. Database Migrations

```
# Initialize database to the latest schema
alembic upgrade head
```

5. Run the Application

```
uvicorn main:app --reload
(or)
fastapi dev main.py
```

## API Endpoints Summary

### Authentication & Users

- POST /api/user/signup - Register a new user (Manager/Admin only).
- POST /api/user/login - Authenticate and receive access token.
- GET /api/user/me - Retrieve current authenticated user profile.
- PATCH /api/user/update-user - Update user details or roles (Admin restricted).

### Teams

- POST /api/team/create-team - Initialize a new team.
- POST /api/team/create-invite - Generate a secure invite link for a user.
- GET /api/team/{team_id} - Fetch detailed team stats, manager info, and member tasks.

### Tasks

- POST /api/task/create-task - Create a single task.
- POST /api/task/bulk-create - Create up to 50 tasks in one request.
- PATCH /api/task/update-task - Modify task status, priority, or content.
- DELETE /api/task/bulk-delete - Soft-delete multiple tasks simultaneously.


## Security Implementation :

- The system employs a multi-layered security approach:

- Password Safety: Argon2 hashing for all stored credentials.

- Stateless Auth: JWT tokens for request authorization.

- Role Guard: Custom require_roles dependency to enforce access boundaries.

- Soft Deletion: Critical data (Tasks/Teams) is flagged as deleted rather than removed, preventing accidental data loss.
