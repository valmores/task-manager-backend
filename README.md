# TaskMaster API

TaskMaster is a robust RESTful API designed for a collaborative task management system. It provides comprehensive support for users, projects, and tasks with built-in Role-Based Access Control (RBAC).

## 🚀 Features

- **Advanced RBAC**: Granular permissions for Admins, Project Owners, and regular Users.
- **Task Management**: Full CRUD operations for tasks including status and priority tracking.
- **Project Tracking**: Organizes tasks into projects with ownership management.
- **Internal Discussion System**: A dedicated internal notes API for tasks, restricted to administrators and project owners for private decision tracking.
- **JWT Authentication**: Secure stateless authentication using `djangorestframework-simplejwt`.

## 🛠 Tech Stack

- **Framework**: Django 5.1.x
- **API Engine**: Django REST Framework (DRF)
- **Authentication**: Simple JWT
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Permissions**: Custom RBAC layers

## 📂 API Endpoints

### Authentication & Users
- `POST /api/users/register/` - Register a new user account.
- `POST /api/users/login/` - Authenticate and receive JWT tokens.
- `POST /api/users/token/refresh/` - Refresh an expired access token.
- `GET /api/users/user-profile/` - Get current authenticated user details.
- `GET /api/users/list/` - List users for task assignment.

### Admin Panel (Admin Only)
- `POST /api/users/admin/create-user/` - Create a user with a specific role.
- `GET /api/users/admin/` - List all users with metadata.
- `GET/PUT/DELETE /api/users/admin/{id}/` - Manage user roles and status.

### Projects & Tasks
- `GET/POST /api/tasks/projects/` - Manage projects (scoped by role).
- `GET/PUT/DELETE /api/tasks/projects/{id}/` - Manage specific project details.
- `GET/POST /api/tasks/` - Manage task list and creation.
- `GET/PUT/DELETE /api/tasks/{id}/` - Manage specific task details.
- `GET/POST /api/tasks/notes/` - (Admin/Owner only) Manage internal administrative notes for tasks.

## ⚙️ Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd task-manager-backend
   ```

2. **Setup Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create Superuser**:
   To gain full access to the Admin dashboard and all system features, create an administrative user:
   ```bash
   python manage.py createsuperuser
   ```
   > [!TIP]
   > Creating a superuser automatically assigns the `admin` role in this system, enabling user management and full project visibility.

6. **Run Server**:
   ```bash
   python manage.py runserver
   ```

## 🔐 Permissions Overview
- **Admin**: Full access to all data, user management, and all projects/tasks.
- **Project Owner**: Can create projects/tasks and see internal notes for their projects.
- **User**: Can view assigned tasks and update their status.
