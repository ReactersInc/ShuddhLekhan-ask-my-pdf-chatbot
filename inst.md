# Team Deployment Guide

## Prerequisites
- Python 3.8+
- Node.js 16+
- Supabase account access

## Backend Setup

1. **Clone and setup virtual environment:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

2. **Environment Configuration:**
```bash
# Copy the example file
copy .env.example .env

# Fill in your values in .env:
SUPABASE_URL=https://fkfmtxczjvrcfbswqdse.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # Get from Supabase Settings > API
JWT_SECRET=your-secure-random-string-here
```

3. **Database Setup:**
   - Go to https://fkfmtxczjvrcfbswqdse.supabase.co
   - Open SQL Editor
   - Run the SQL from `backend/database/setup_tables.sql`

4. **Start Backend:**
```bash
cd backend
venv\Scripts\activate
python app.py
```
Backend runs on: http://127.0.0.1:5000

## Frontend Setup

1. **Environment Configuration:**
```bash
cd frontend
# Create .env file:
VITE_SUPABASE_URL=https://fkfmtxczjvrcfbswqdse.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

2. **Install and Run:**
```bash
npm install
npm run dev
```
Frontend runs on: http://localhost:5173

## Authentication Features Implemented

✅ **User Registration** (`/auth/signup`)
✅ **User Login** (`/auth/login`) 
✅ **User Profile** (with name, email display)
✅ **Logout** (clears tokens and redirects)
✅ **Delete Account** (`/auth/delete-account`)
✅ **JWT Token Protection**
✅ **Protected Routes** (redirect to auth if not logged in)
✅ **Password Hashing** (bcrypt)
✅ **Session Management** (localStorage)

## API Endpoints

### Authentication
- `POST /auth/signup` - Create new user
- `POST /auth/login` - User login  
- `DELETE /auth/delete-account` - Delete user account (requires auth)

### Other Features (PDF/Plagiarism)
- `POST /upload/pdf` - Upload PDF for processing
- `POST /plagiarism/upload` - Upload for plagiarism check
- `GET /pdfs/` - List uploaded PDFs

## Security Notes
- Never commit `.env` files
- `SUPABASE_SERVICE_KEY` is for backend only
- `SUPABASE_ANON_KEY` is safe for frontend
- Change `JWT_SECRET` to a strong random string in production

