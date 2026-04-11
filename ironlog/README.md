# IronLog

**AI-powered training intelligence system for strength athletes**

IronLog is a progressive web app that combines workout logging with machine learning to provide intelligent training insights, automatic periodization, and personalized recommendations.

## Features

### Core Functionality
- **Smart Workout Logger** - Log sets with weight, reps, and RPE in a streamlined mobile-first interface
- **Exercise Knowledge Base** - 120+ exercises with detailed instructions, muscle targeting, and substitution recommendations
- **Automatic 1RM Tracking** - Real-time estimated 1RM calculations with PR detection
- **Training Analytics** - Volume tracking, strength curves, and frequency heatmaps

### AI-Powered Intelligence (Coming Soon)
- **Gaussian Process Strength Modeling** - Predict future performance with confidence intervals
- **Plateau Detection** - PELT changepoint analysis to identify training stagnation
- **Recovery Modeling** - Banister fitness-fatigue model for readiness prediction
- **Volume Analysis** - Automatic MEV/MRV tracking per muscle group
- **Smart Programming** - AI-generated training splits optimized for your recovery and goals

## Tech Stack

### Backend
- **FastAPI** - Modern async Python web framework
- **SQLAlchemy 2.0** - Async ORM with PostgreSQL
- **Alembic** - Database migrations
- **Celery + Redis** - Background job processing
- **JWT Authentication** - Secure token-based auth
- **Pydantic** - Data validation and serialization

### Frontend
- **React 18** + **TypeScript** - Type-safe component architecture
- **Vite** - Lightning-fast build tooling
- **Tailwind CSS** - Utility-first styling
- **Zustand** - Lightweight state management
- **Axios** - HTTP client with JWT refresh logic
- **Framer Motion** - Smooth animations
- **PWA** - Offline-first progressive web app

### Machine Learning (Planned)
- **scikit-learn** - Gaussian Process regression, changepoint detection
- **NumPy/Pandas** - Data processing and analysis
- **Ruptures** - PELT algorithm for plateau detection

## Project Structure

```
ironlog/
├── backend/
│   ├── alembic/              # Database migrations
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   ├── ml/               # ML models (planned)
│   │   ├── tasks/            # Celery tasks (planned)
│   │   └── seed/             # Database seed data
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── stores/           # Zustand stores
│   │   ├── hooks/            # Custom React hooks
│   │   ├── services/         # API client
│   │   ├── types/            # TypeScript types
│   │   └── lib/              # Utilities
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.dev.yml
└── Makefile
```

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 16
- Redis 7 (for background jobs)
- Docker & Docker Compose (optional)

### Local Development

#### 1. Clone the repository
```bash
git clone https://github.com/yourusername/ironlog.git
cd ironlog
```

#### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
alembic upgrade head

# Seed database with exercises
python -m app.seed.seed_db

# Start development server
uvicorn app.main:app --reload --port 8000
```

#### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install --legacy-peer-deps

# Start development server
npm run dev
```

The app will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Docker Development

```bash
# Start all services
docker-compose -f docker-compose.dev.yml up

# Run migrations
docker-compose exec backend alembic upgrade head

# Seed database
docker-compose exec backend python -m app.seed.seed_db
```

## API Documentation

Interactive API documentation is available at `/docs` when running the backend server.

### Key Endpoints

**Authentication**
- `POST /api/auth/register` - Create new user
- `POST /api/auth/login` - Login and get JWT tokens
- `POST /api/auth/refresh` - Refresh access token

**Exercises**
- `GET /api/exercises` - List exercises with filters
- `GET /api/exercises/{id}` - Get exercise details
- `GET /api/exercises/search?q={query}` - Search exercises
- `GET /api/muscle-groups` - List muscle groups

**Workouts**
- `POST /api/workouts/sessions` - Create workout session
- `GET /api/workouts/sessions` - List user's workouts
- `POST /api/workouts/sessions/{id}/exercises` - Add exercise to session
- `POST /api/workouts/exercises/{id}/sets` - Log a set
- `POST /api/workouts/quick-log` - Quick log single exercise

## Design Philosophy

IronLog follows a **"dark athletic minimalism"** design aesthetic:
- Near-black backgrounds (#0A0A0B) with subtle borders
- Warm amber accent color (#E8A23E) for CTAs and highlights
- DM Sans for UI, Instrument Serif for editorial accents
- Dense with data but never cluttered
- Mobile-first, touch-optimized interface
- Smooth animations with Framer Motion

## Database Schema

### Core Tables
- `users` - User accounts and preferences
- `exercises` - Exercise library with 120+ movements
- `muscle_groups` - 22 muscle groups with MEV/MRV defaults
- `workout_sessions` - Training sessions
- `sets` - Individual set logs with weight, reps, RPE
- `strength_estimates` - Historical 1RM estimates (planned)
- `plateau_detections` - Detected training plateaus (planned)
- `recovery_state` - Daily recovery metrics (planned)

## Roadmap

### Phase 1: Backend Foundation ✅
- [x] Project scaffolding
- [x] Database models and migrations
- [x] Exercise knowledge base
- [x] Authentication system
- [x] Workout logging API

### Phase 2: Frontend PWA (In Progress)
- [x] Frontend scaffolding with design system
- [x] Dashboard with stats
- [x] Navigation and routing
- [ ] Workout logger screen
- [ ] Exercise browser
- [ ] Analytics dashboard

### Phase 3: ML Models (Planned)
- [ ] Celery + Redis setup
- [ ] Volume analyzer
- [ ] Strength curve modeling (Gaussian Process)
- [ ] Plateau detector (PELT)
- [ ] Recovery model (Banister)
- [ ] Autoregulation engine

### Phase 4: Smart Programming (Planned)
- [ ] Program generation UI
- [ ] Recommendation endpoints
- [ ] Deload detection

### Phase 5: Polish (Planned)
- [ ] Offline support with IndexedDB
- [ ] PWA install prompts
- [ ] Data export (CSV/JSON)
- [ ] Error handling and empty states
- [ ] Production Docker config

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Exercise data curated from evidence-based strength training research
- ML models inspired by Renaissance Periodization's training principles
- Design inspired by Linear and Whoop's interfaces

---

**Built with ❤️ for strength athletes who take their training seriously**
