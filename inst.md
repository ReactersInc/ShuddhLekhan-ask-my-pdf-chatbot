# Ask My PDF Chatbot - Setup Guide

## Prerequisites
- Python 3.8+
- Node.js 16+
- Supabase account access

## Quick Setup

### 1. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Environment Configuration
Create `.env` file in backend directory:
```bash
SUPABASE_URL=https://fkfmtxczjvrcfbswqdse.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
JWT_SECRET=your-secure-random-string-here
```

### 3. Database Setup
- Go to https://fkfmtxczjvrcfbswqdse.supabase.co
- SQL Editor → Run `backend/database/setup_tables.sql`

### 4. Start Backend
```bash
python app.py
```
Backend: http://127.0.0.1:5000

### 5. Frontend Setup
```bash
cd frontend
# Create .env file:
echo "VITE_SUPABASE_URL=https://fkfmtxczjvrcfbswqdse.supabase.co" > .env
echo "VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." >> .env

npm install
npm run dev
```
Frontend: http://localhost:5173

## 🔐 Authentication System (Already Built)

### What's Implemented:
- ✅ User Registration & Login 
- ✅ JWT Token Authentication
- ✅ Password Hashing (bcrypt)
- ✅ Protected Routes
- ✅ User Sessions

### Key Files:
- `backend/services/auth_service.py` - Core auth logic
- `backend/utils/auth_utils.py` - `@require_auth` decorator
- `backend/controllers/auth_controller.py` - Request handlers
- `backend/routes/auth_routes.py` - API routes

### Auth Endpoints:
- `POST /auth/signup` - Register user
- `POST /auth/login` - Login user
- `DELETE /auth/delete-account` - Delete account

## 🚀 Next Steps for Team

### 1. Protect New Routes
```python
from utils.auth_utils import require_auth
from flask import g

@app.route('/api/your-endpoint')
@require_auth  # Add this decorator
def your_function():
    user_id = g.user_id  # Get logged-in user ID
    # Your code here
```

### 2. Frontend Token Usage
```javascript
// Include token in requests
const token = localStorage.getItem('token');
fetch('/api/endpoint', {
  headers: {'Authorization': 'Bearer ' + token}
});
```

### 3. User-Specific Data
Always filter data by `user_id` from `g.user_id` in protected routes.

## 📁 Project Structure
```
backend/
├── services/auth_service.py    # Core authentication
├── utils/auth_utils.py         # @require_auth decorator  
├── controllers/                # Request handlers
├── routes/                     # API endpoints
└── database/                   # DB setup & client

frontend/
└── src/                        # React components
```

## 🔧 Common Commands
```bash
# Backend
cd backend && venv\Scripts\activate && python app.py

# Frontend  
cd frontend && npm run dev

# Test auth
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password"}'
```

---

**Authentication is ready! Start building features using `@require_auth` decorator.**
