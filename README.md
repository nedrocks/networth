# Full-Stack Application

A simple full-stack application with a Python FastAPI backend and React TypeScript frontend.

## Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- npm 6 or higher

## Quick Start

The easiest way to get started is to use the bootstrap script:

```bash
cd frontend
npm run bootstrap
```

This will set up both the backend and frontend environments.

## Manual Setup

If you prefer to set up manually:

### Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

The backend will be available at http://localhost:8000

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

The frontend will be available at http://localhost:3000

## Development

- Backend API documentation: http://localhost:8000/docs
- Frontend development server includes hot reloading
- Tailwind CSS for styling

## Project Structure

```
my-fullstack-app/
├── backend/
│   ├── requirements.txt
│   ├── main.py
│   └── models.py
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   └── src/
│       ├── App.tsx
│       └── types.ts
├── bootstrap.sh
└── README.md
```