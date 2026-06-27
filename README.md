# Enterprise Resource Planning (ERP) System

A complete, production-ready ERP system built with modern technologies for manufacturing companies.

## Architecture

This is a comprehensive ERP solution built by a team of Principal Software Engineers from leading ERP vendors.

### Technology Stack

**Frontend:**
- React 19
- TypeScript
- Vite
- Tailwind CSS
- ShadCN UI
- TanStack Query
- React Hook Form

**Backend:**
- FastAPI (Python)
- SQLAlchemy ORM
- Alembic Migrations
- Pydantic Validation

**Database:**
- PostgreSQL
- Redis Cache

**Infrastructure:**
- Docker & Docker Compose
- AWS S3 Compatible Storage

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+

### Setup

```bash
# Clone the repository
git clone https://github.com/Priyachaubey/ERP.git
cd ERP

# Start services with Docker Compose
docker-compose up -d

# Run database migrations
docker exec erp-backend alembic upgrade head

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Project Structure

```
ERP/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── modules/
│   │   ├── schemas/
│   │   ├── models/
│   │   ├── routes/
│   │   └── services/
│   ├── alembic/          # Database migrations
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/             # React frontend
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── types/
│   │   └── App.tsx
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Core Modules

### 1. Authentication
- Login/Logout
- JWT with Refresh Tokens
- Role-Based Access Control (RBAC)
- Session Management
- Audit Logging

### 2. User Management
- Users
- Roles & Permissions
- Department Masters

### 3. Production Management
- Work Issue & Receive
- Production Tracking
- Quality Inspection
- Rework Management

### 4. Inventory Management
- Raw Materials
- Finished Goods
- Stock Adjustments
- Stock Transfers

### 5. Purchase Management
- Suppliers
- Purchase Orders
- GRN (Goods Receipt Note)
- Purchase Bills

### 6. Financial Management
- Employee Payments
- Ledger Management
- Expense Tracking

### 7. Reporting & Analytics
- Dashboard KPIs
- Production Charts
- Employee Productivity
- Machine Utilization
- Export (Excel, PDF)

### 8. Notifications
- In-app Notifications
- Email Integration
- SMS Integration
- WhatsApp Integration

## Security Features

- Helmet for HTTP headers
- Rate limiting
- Password hashing (bcrypt)
- JWT authentication
- Refresh token rotation
- CORS configuration
- SQL injection protection
- XSS protection
- Complete audit logging

## Database Schema

Full PostgreSQL schema with:
- Foreign keys
- Indexes on performance-critical columns
- Check constraints
- Proper data types
- Comprehensive migrations

## API Documentation

Swagger/OpenAPI documentation automatically generated at `/docs`

## Contributing

Following SAP, Oracle, and Microsoft enterprise standards.

## License

MIT
