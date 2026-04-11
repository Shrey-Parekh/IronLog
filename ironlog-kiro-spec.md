# IronLog — Kiro Implementation Spec

> AI-Powered Training Intelligence System
> This document is the single source of truth for implementation.
> Follow phases in order. Do not skip ahead. Each task has explicit inputs, outputs, and acceptance criteria.

---

## GLOBAL RULES

- Language: Python 3.11+ (backend), TypeScript (frontend)
- Backend framework: FastAPI with async endpoints
- ORM: SQLAlchemy 2.0 (async) with Alembic migrations
- Frontend: React 18 + TypeScript + Vite
- Styling: Tailwind CSS + Shadcn/UI components
- State management: Zustand
- Charts: Recharts
- Package manager: pnpm (frontend), pip + requirements.txt (backend)
- Database: PostgreSQL 16
- Task queue: Celery + Redis
- Auth: JWT (access + refresh tokens)
- All API responses follow: `{ "data": ..., "error": null }` or `{ "data": null, "error": { "code": "...", "message": "..." } }`
- All timestamps are UTC ISO 8601
- All weights stored in kg internally, converted on display based on user preference
- All IDs are UUID for user-facing entities, SERIAL for internal reference tables
- Every endpoint must have Pydantic request/response schemas
- Every ML model must have a `min_data_points` threshold — return graceful "insufficient data" response below it
- Dark mode is the default and only theme for v1
- Mobile-first: all UI must work on 375px width (iPhone SE)

---

## PROJECT STRUCTURE

```
ironlog/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app factory + CORS + middleware
│   │   ├── config.py                  # Pydantic BaseSettings, env vars
│   │   ├── database.py                # async SQLAlchemy engine + session
│   │   ├── dependencies.py            # get_db, get_current_user
│   │   ├── models/                    # SQLAlchemy ORM models (one file per domain)
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── exercise.py            # exercises, muscle_groups, exercise_muscles, exercise_substitutions
│   │   │   ├── workout.py             # workout_sessions, workout_exercises, sets
│   │   │   ├── program.py             # training_programs, program_days
│   │   │   └── analytics.py           # strength_estimates, muscle_group_volume, plateau_detections, recovery_state, training_insights
│   │   ├── schemas/                   # Pydantic v2 schemas
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── exercise.py
│   │   │   ├── workout.py
│   │   │   ├── program.py
│   │   │   └── analytics.py
│   │   ├── api/                       # Router modules
│   │   │   ├── __init__.py
│   │   │   ├── router.py              # aggregates all routers
│   │   │   ├── auth.py
│   │   │   ├── exercises.py
│   │   │   ├── workouts.py
│   │   │   ├── analytics.py
│   │   │   ├── insights.py
│   │   │   ├── programs.py
│   │   │   └── recommendations.py
│   │   ├── services/                  # Business logic layer (routes call services, services call DB)
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── exercise_service.py
│   │   │   ├── workout_service.py
│   │   │   ├── analytics_service.py
│   │   │   └── recommendation_service.py
│   │   ├── ml/                        # ML models (pure Python, no API dependency)
│   │   │   ├── __init__.py
│   │   │   ├── strength_curve.py
│   │   │   ├── plateau_detector.py
│   │   │   ├── recovery_model.py
│   │   │   ├── volume_analyzer.py
│   │   │   ├── autoregulation.py
│   │   │   └── split_optimizer.py
│   │   ├── tasks/                     # Celery tasks
│   │   │   ├── __init__.py
│   │   │   ├── celery_app.py
│   │   │   ├── post_session.py
│   │   │   ├── nightly.py
│   │   │   └── weekly.py
│   │   └── seed/                      # Knowledge base seed data
│   │       ├── muscle_groups.json
│   │       ├── exercises.json
│   │       └── seed_db.py
│   ├── alembic/
│   │   ├── alembic.ini
│   │   └── versions/
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_workouts.py
│   │   └── test_ml/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── public/
│   │   ├── manifest.json
│   │   ├── sw.js
│   │   └── icons/                     # PWA icons (192x192, 512x512)
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── routes.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── WorkoutLogger.tsx
│   │   │   ├── ExercisePicker.tsx
│   │   │   ├── Analytics.tsx
│   │   │   ├── ExerciseDetail.tsx
│   │   │   ├── Insights.tsx
│   │   │   ├── Programs.tsx
│   │   │   └── Profile.tsx
│   │   ├── components/
│   │   │   ├── ui/                    # Shadcn components go here
│   │   │   ├── SetLoggerRow.tsx
│   │   │   ├── WeightInput.tsx        # Numpad + increment buttons
│   │   │   ├── RestTimer.tsx
│   │   │   ├── ExerciseCard.tsx
│   │   │   ├── StrengthChart.tsx
│   │   │   ├── VolumeChart.tsx
│   │   │   ├── RecoveryHeatmap.tsx
│   │   │   ├── BodyMap.tsx
│   │   │   ├── InsightCard.tsx
│   │   │   └── NavigationBar.tsx      # Bottom tab bar (mobile)
│   │   ├── hooks/
│   │   │   ├── useWorkoutSession.ts
│   │   │   ├── useOfflineSync.ts
│   │   │   ├── useAnalytics.ts
│   │   │   └── useAuth.ts
│   │   ├── services/
│   │   │   ├── api.ts                 # Axios instance with interceptors
│   │   │   └── offlineQueue.ts
│   │   ├── stores/
│   │   │   ├── authStore.ts
│   │   │   ├── workoutStore.ts
│   │   │   └── analyticsStore.ts
│   │   ├── types/
│   │   │   └── index.ts              # All TypeScript interfaces mirroring Pydantic schemas
│   │   └── lib/
│   │       ├── utils.ts
│   │       └── constants.ts           # RPE scale, unit conversions, volume landmarks
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── package.json
│
├── docker-compose.yml
├── docker-compose.dev.yml
├── Makefile                           # dev shortcuts: make up, make migrate, make seed, make test
└── README.md
```

---

## PHASE 1: Backend Foundation + Database

### Task 1.1: Project Scaffolding

**Do:**
1. Create the full directory structure above (empty `__init__.py` files where needed)
2. Create `backend/requirements.txt`:
   ```
   fastapi==0.115.0
   uvicorn[standard]==0.30.0
   sqlalchemy[asyncio]==2.0.35
   asyncpg==0.30.0
   alembic==1.13.0
   pydantic==2.9.0
   pydantic-settings==2.5.0
   python-jose[cryptography]==3.3.0
   passlib[bcrypt]==1.7.4
   celery==5.4.0
   redis==5.1.0
   scikit-learn==1.5.0
   scipy==1.14.0
   statsmodels==0.14.0
   ruptures==1.1.9
   numpy==2.1.0
   httpx==0.27.0
   python-multipart==0.0.12
   ```
3. Create `backend/app/config.py` using Pydantic BaseSettings reading from `.env`
4. Create `backend/.env.example`
5. Create `docker-compose.dev.yml` with: postgres:16, redis:7, backend (uvicorn with reload)

**Acceptance criteria:**
- `docker-compose -f docker-compose.dev.yml up` starts all services
- `curl http://localhost:8000/health` returns `{"status": "ok"}`

---

### Task 1.2: Database Models + Migrations

**Do:**
Create all SQLAlchemy models matching this exact schema. Every column, constraint, index, and default must match.

**File: `backend/app/models/user.py`**
```
Table: users
- id: UUID, PK, default gen_random_uuid()
- email: VARCHAR(255), UNIQUE, NOT NULL
- password_hash: VARCHAR(255), NOT NULL
- display_name: VARCHAR(100), nullable
- body_weight_kg: DECIMAL(5,2), nullable
- height_cm: DECIMAL(5,2), nullable
- training_age_months: INT, default 0
- preferred_unit: VARCHAR(10), default 'kg'
- created_at: TIMESTAMPTZ, default NOW()
- updated_at: TIMESTAMPTZ, default NOW()
```

**File: `backend/app/models/exercise.py`**
```
Table: muscle_groups
- id: SERIAL PK
- name: VARCHAR(50), UNIQUE, NOT NULL — internal key like 'chest', 'front_delt'
- display_name: VARCHAR(100), NOT NULL — human readable like 'Chest', 'Front Deltoid'
- body_region: VARCHAR(20), NOT NULL — enum: 'upper', 'lower', 'core'
- push_pull: VARCHAR(10), nullable — 'push', 'pull', or NULL
- default_recovery_hours: INT, default 48
- default_mrv_sets_week: INT, default 20
- default_mev_sets_week: INT, default 10

Table: exercises
- id: SERIAL PK
- name: VARCHAR(100), UNIQUE, NOT NULL — internal key like 'barbell_bench_press'
- display_name: VARCHAR(150), NOT NULL
- movement_pattern: VARCHAR(30), NOT NULL — enum: 'horizontal_push', 'vertical_push', 'horizontal_pull', 'vertical_pull', 'hip_hinge', 'squat', 'isolation', 'carry'
- equipment: VARCHAR(30), NOT NULL — enum: 'barbell', 'dumbbell', 'cable', 'machine', 'bodyweight', 'smith_machine', 'band'
- is_compound: BOOLEAN, default TRUE
- is_unilateral: BOOLEAN, default FALSE
- supports_1rm: BOOLEAN, default TRUE
- difficulty: VARCHAR(15), default 'intermediate'
- instructions: TEXT, nullable
- tips: TEXT, nullable
- common_mistakes: TEXT, nullable

Table: exercise_muscles
- exercise_id: INT FK → exercises(id), PK part 1
- muscle_group_id: INT FK → muscle_groups(id), PK part 2
- role: VARCHAR(15), NOT NULL — enum: 'primary', 'secondary', 'stabilizer'
- activation_pct: DECIMAL(4,2), default 1.0

Table: exercise_substitutions
- exercise_id: INT FK → exercises(id), PK part 1
- substitute_id: INT FK → exercises(id), PK part 2
- similarity: DECIMAL(3,2), NOT NULL — range 0.0-1.0
- reason: VARCHAR(200), nullable
```

**File: `backend/app/models/workout.py`**
```
Table: workout_sessions
- id: UUID PK, default gen_random_uuid()
- user_id: UUID FK → users(id), NOT NULL
- started_at: TIMESTAMPTZ, NOT NULL
- finished_at: TIMESTAMPTZ, nullable
- session_name: VARCHAR(100), nullable
- notes: TEXT, nullable
- overall_rpe: DECIMAL(3,1), nullable
- bodyweight_kg: DECIMAL(5,2), nullable
- total_volume_kg: DECIMAL(10,2), nullable — computed post-session
- total_sets: INT, nullable
- duration_minutes: INT, nullable
- created_at: TIMESTAMPTZ, default NOW()
Index: (user_id, started_at DESC)

Table: workout_exercises
- id: SERIAL PK
- session_id: UUID FK → workout_sessions(id) ON DELETE CASCADE
- exercise_id: INT FK → exercises(id), nullable
- user_exercise_id: INT FK → user_exercises(id), nullable
- exercise_order: INT, NOT NULL
- notes: TEXT, nullable
- estimated_1rm: DECIMAL(6,2), nullable
- total_volume_kg: DECIMAL(8,2), nullable
- CHECK: exactly one of exercise_id or user_exercise_id must be non-null

Table: sets
- id: SERIAL PK
- workout_exercise_id: INT FK → workout_exercises(id) ON DELETE CASCADE
- set_order: INT, NOT NULL
- set_type: VARCHAR(15), default 'working' — enum: 'warmup', 'working', 'dropset', 'failure', 'amrap'
- weight_kg: DECIMAL(6,2), NOT NULL
- reps: INT, NOT NULL
- rpe: DECIMAL(3,1), nullable — range 6.0-10.0, step 0.5
- rir: INT, nullable
- is_pr: BOOLEAN, default FALSE
- volume_kg: DECIMAL(8,2), GENERATED ALWAYS AS (weight_kg * reps) STORED
- estimated_1rm: DECIMAL(6,2), nullable
- logged_at: TIMESTAMPTZ, default NOW()

Table: user_exercises
- id: SERIAL PK
- user_id: UUID FK → users(id)
- base_exercise_id: INT FK → exercises(id), nullable
- name: VARCHAR(150), NOT NULL
- movement_pattern: VARCHAR(30), nullable
- equipment: VARCHAR(30), nullable
- is_compound: BOOLEAN, default TRUE
- created_at: TIMESTAMPTZ, default NOW()
```

**File: `backend/app/models/program.py`**
```
Table: training_programs
- id: SERIAL PK
- user_id: UUID FK → users(id)
- name: VARCHAR(100), NOT NULL
- days_per_week: INT, NOT NULL
- is_active: BOOLEAN, default TRUE
- created_at: TIMESTAMPTZ, default NOW()

Table: program_days
- id: SERIAL PK
- program_id: INT FK → training_programs(id) ON DELETE CASCADE
- day_number: INT, NOT NULL
- day_name: VARCHAR(50), NOT NULL
- target_muscle_groups: INT[] — array of muscle_group IDs
```

**File: `backend/app/models/analytics.py`**
```
Table: strength_estimates
- id: SERIAL PK
- user_id: UUID FK → users(id)
- exercise_id: INT FK → exercises(id)
- estimated_at: DATE, NOT NULL
- estimated_1rm: DECIMAL(6,2), NOT NULL
- confidence_low: DECIMAL(6,2), nullable
- confidence_high: DECIMAL(6,2), nullable
- model_version: VARCHAR(20), nullable
- data_points: INT, nullable
- UNIQUE(user_id, exercise_id, estimated_at)

Table: muscle_group_volume
- id: SERIAL PK
- user_id: UUID FK → users(id)
- muscle_group_id: INT FK → muscle_groups(id)
- week_start: DATE, NOT NULL
- total_sets: INT, NOT NULL
- total_volume_kg: DECIMAL(10,2), nullable
- avg_rpe: DECIMAL(3,1), nullable
- status: VARCHAR(20), nullable — enum: 'under_mev', 'in_range', 'over_mrv'
- UNIQUE(user_id, muscle_group_id, week_start)

Table: plateau_detections
- id: SERIAL PK
- user_id: UUID FK → users(id)
- exercise_id: INT FK → exercises(id)
- detected_at: DATE, NOT NULL
- plateau_start: DATE, NOT NULL
- weeks_stalled: INT, NOT NULL
- estimated_1rm_at_plateau: DECIMAL(6,2), nullable
- recommendation: TEXT, nullable
- is_resolved: BOOLEAN, default FALSE
- resolved_at: DATE, nullable

Table: recovery_state
- id: SERIAL PK
- user_id: UUID FK → users(id)
- muscle_group_id: INT FK → muscle_groups(id)
- computed_at: TIMESTAMPTZ, default NOW()
- fatigue_score: DECIMAL(4,2) — range 0.0-1.0
- estimated_recovery_pct: DECIMAL(4,2) — range 0-100
- next_ready_at: TIMESTAMPTZ, nullable
- last_trained_at: TIMESTAMPTZ, nullable
Index: (user_id, computed_at DESC)

Table: training_insights
- id: SERIAL PK
- user_id: UUID FK → users(id)
- generated_at: TIMESTAMPTZ, default NOW()
- insight_type: VARCHAR(30), NOT NULL — enum: 'plateau', 'pr', 'volume_warning', 'imbalance', 'recovery', 'recommendation'
- severity: VARCHAR(10), default 'info' — enum: 'info', 'warning', 'action'
- title: VARCHAR(200), NOT NULL
- body: TEXT, NOT NULL
- related_exercise_id: INT FK → exercises(id), nullable
- related_muscle_group_id: INT FK → muscle_groups(id), nullable
- is_read: BOOLEAN, default FALSE
- is_dismissed: BOOLEAN, default FALSE
Index: (user_id, generated_at DESC)
```

**Then:**
- Run `alembic init alembic` and configure
- Generate initial migration: `alembic revision --autogenerate -m "initial schema"`
- Verify migration applies cleanly: `alembic upgrade head`

**Acceptance criteria:**
- All tables created in PostgreSQL with correct columns, types, constraints, indexes
- `alembic upgrade head` and `alembic downgrade base` both work without errors

---

### Task 1.3: Exercise Knowledge Base Seed Data

**Do:**
Create `backend/app/seed/muscle_groups.json` and `backend/app/seed/exercises.json` with complete data.

**Muscle Groups (22 entries):**
```json
[
  {"name": "chest", "display_name": "Chest", "body_region": "upper", "push_pull": "push", "default_recovery_hours": 48, "default_mrv_sets_week": 22, "default_mev_sets_week": 10},
  {"name": "front_delt", "display_name": "Front Deltoid", "body_region": "upper", "push_pull": "push", "default_recovery_hours": 36, "default_mrv_sets_week": 12, "default_mev_sets_week": 6},
  {"name": "side_delt", "display_name": "Side Deltoid", "body_region": "upper", "push_pull": "push", "default_recovery_hours": 24, "default_mrv_sets_week": 26, "default_mev_sets_week": 8},
  {"name": "rear_delt", "display_name": "Rear Deltoid", "body_region": "upper", "push_pull": "pull", "default_recovery_hours": 24, "default_mrv_sets_week": 22, "default_mev_sets_week": 8},
  {"name": "long_head_tricep", "display_name": "Tricep (Long Head)", "body_region": "upper", "push_pull": "push", "default_recovery_hours": 36, "default_mrv_sets_week": 18, "default_mev_sets_week": 6},
  {"name": "lateral_head_tricep", "display_name": "Tricep (Lateral Head)", "body_region": "upper", "push_pull": "push", "default_recovery_hours": 36, "default_mrv_sets_week": 18, "default_mev_sets_week": 6},
  {"name": "biceps_long", "display_name": "Bicep (Long Head)", "body_region": "upper", "push_pull": "pull", "default_recovery_hours": 36, "default_mrv_sets_week": 22, "default_mev_sets_week": 8},
  {"name": "biceps_short", "display_name": "Bicep (Short Head)", "body_region": "upper", "push_pull": "pull", "default_recovery_hours": 36, "default_mrv_sets_week": 22, "default_mev_sets_week": 8},
  {"name": "brachialis", "display_name": "Brachialis", "body_region": "upper", "push_pull": "pull", "default_recovery_hours": 36, "default_mrv_sets_week": 18, "default_mev_sets_week": 6},
  {"name": "forearms", "display_name": "Forearms", "body_region": "upper", "push_pull": "pull", "default_recovery_hours": 24, "default_mrv_sets_week": 16, "default_mev_sets_week": 4},
  {"name": "lats", "display_name": "Latissimus Dorsi", "body_region": "upper", "push_pull": "pull", "default_recovery_hours": 48, "default_mrv_sets_week": 22, "default_mev_sets_week": 10},
  {"name": "upper_back", "display_name": "Upper Back (Traps/Rhomboids)", "body_region": "upper", "push_pull": "pull", "default_recovery_hours": 48, "default_mrv_sets_week": 22, "default_mev_sets_week": 10},
  {"name": "quads", "display_name": "Quadriceps", "body_region": "lower", "push_pull": null, "default_recovery_hours": 72, "default_mrv_sets_week": 20, "default_mev_sets_week": 8},
  {"name": "hamstrings", "display_name": "Hamstrings", "body_region": "lower", "push_pull": null, "default_recovery_hours": 72, "default_mrv_sets_week": 16, "default_mev_sets_week": 6},
  {"name": "glutes", "display_name": "Glutes", "body_region": "lower", "push_pull": null, "default_recovery_hours": 72, "default_mrv_sets_week": 16, "default_mev_sets_week": 4},
  {"name": "calves", "display_name": "Calves", "body_region": "lower", "push_pull": null, "default_recovery_hours": 36, "default_mrv_sets_week": 16, "default_mev_sets_week": 6},
  {"name": "hip_flexors", "display_name": "Hip Flexors", "body_region": "lower", "push_pull": null, "default_recovery_hours": 48, "default_mrv_sets_week": 10, "default_mev_sets_week": 2},
  {"name": "adductors", "display_name": "Adductors", "body_region": "lower", "push_pull": null, "default_recovery_hours": 48, "default_mrv_sets_week": 14, "default_mev_sets_week": 4},
  {"name": "abs", "display_name": "Abdominals", "body_region": "core", "push_pull": null, "default_recovery_hours": 24, "default_mrv_sets_week": 20, "default_mev_sets_week": 6},
  {"name": "obliques", "display_name": "Obliques", "body_region": "core", "push_pull": null, "default_recovery_hours": 24, "default_mrv_sets_week": 16, "default_mev_sets_week": 4},
  {"name": "lower_back", "display_name": "Lower Back (Erectors)", "body_region": "core", "push_pull": null, "default_recovery_hours": 72, "default_mrv_sets_week": 12, "default_mev_sets_week": 4}
]
```

**Exercises: minimum 120 exercises covering all major movement patterns.**

Each exercise entry must include:
```json
{
  "name": "barbell_bench_press",
  "display_name": "Barbell Bench Press",
  "movement_pattern": "horizontal_push",
  "equipment": "barbell",
  "is_compound": true,
  "is_unilateral": false,
  "supports_1rm": true,
  "difficulty": "intermediate",
  "instructions": "Lie on flat bench, grip bar slightly wider than shoulder width...",
  "tips": "Keep shoulder blades retracted and depressed...",
  "common_mistakes": "Bouncing bar off chest, flaring elbows excessively...",
  "muscles": [
    {"muscle": "chest", "role": "primary", "activation_pct": 1.0},
    {"muscle": "front_delt", "role": "secondary", "activation_pct": 0.6},
    {"muscle": "long_head_tricep", "role": "secondary", "activation_pct": 0.4}
  ],
  "substitutions": [
    {"exercise": "dumbbell_bench_press", "similarity": 0.9, "reason": "Same movement pattern, dumbbell variant allows greater ROM"},
    {"exercise": "machine_chest_press", "similarity": 0.7, "reason": "Machine-guided horizontal push, good for beginners"}
  ]
}
```

**Exercise categories to cover (aim for 8-15 exercises each):**
- Chest: flat/incline/decline × barbell/dumbbell/cable/machine + flyes + dips
- Back: rows (barbell/dumbbell/cable/machine), pulldowns, pull-ups, pullovers
- Shoulders: presses (barbell/dumbbell/machine), raises (lateral/front/rear), face pulls
- Arms: curls (barbell/dumbbell/cable, all grips), pushdowns, skull crushers, overhead extensions
- Legs: squats (barbell/smith/goblet/leg press), lunges, leg extensions, leg curls, RDLs, hip thrusts
- Core: planks, crunches, cable crunches, hanging leg raises, ab wheel
- Compound: deadlift, power clean, farmer walks

**Create `backend/app/seed/seed_db.py`:**
- Reads both JSON files
- Inserts muscle_groups first, then exercises, then exercise_muscles, then exercise_substitutions
- Idempotent: checks if data exists before inserting (use ON CONFLICT DO NOTHING)
- CLI command: `python -m app.seed.seed_db`

**Acceptance criteria:**
- Running seed script populates all tables
- Running seed script twice does not create duplicates
- Every exercise has at least 1 primary muscle group
- Every compound exercise has at least 1 secondary muscle group
- `SELECT COUNT(*) FROM exercises` returns >= 120
- `SELECT COUNT(*) FROM muscle_groups` returns 22 (note: we removed medial_head_tricep for simplicity, combine tricep heads if needed — actually keep 22 as listed above, but adjust if you find the granularity unnecessary for v1. Keep the 22 listed.)

---

### Task 1.4: Authentication

**Do:**
1. `backend/app/api/auth.py` — routes
2. `backend/app/services/auth_service.py` — logic
3. `backend/app/schemas/auth.py` — schemas

**Endpoints:**
```
POST /api/auth/register
  Request: { email: str, password: str, display_name?: str }
  Response: { user: UserResponse, access_token: str, refresh_token: str }
  Logic: hash password with bcrypt, create user, return JWT pair

POST /api/auth/login
  Request: { email: str, password: str }
  Response: { user: UserResponse, access_token: str, refresh_token: str }

POST /api/auth/refresh
  Request: { refresh_token: str }
  Response: { access_token: str, refresh_token: str }
```

**JWT config:**
- Access token: 30 min expiry, contains `{ sub: user_id, type: "access" }`
- Refresh token: 7 day expiry, contains `{ sub: user_id, type: "refresh" }`
- Secret from env var `JWT_SECRET`

**Dependency: `get_current_user`**
- Extracts Bearer token from Authorization header
- Decodes JWT, fetches user from DB
- Returns User model or raises 401

**Acceptance criteria:**
- Register creates user with hashed password
- Login returns valid JWT
- Protected endpoint returns 401 without token, 200 with valid token
- Refresh endpoint issues new token pair

---

### Task 1.5: Exercise Knowledge Base API

**Do:**
1. `backend/app/api/exercises.py` — routes
2. `backend/app/services/exercise_service.py` — logic
3. `backend/app/schemas/exercise.py` — schemas

**Endpoints:**
```
GET /api/exercises
  Query params: ?muscle_group=chest&equipment=barbell&movement_pattern=horizontal_push&compound_only=true&search=bench&limit=50&offset=0
  Response: { exercises: ExerciseListItem[], total: int }
  ExerciseListItem: { id, display_name, movement_pattern, equipment, is_compound, primary_muscles: str[] }

GET /api/exercises/{id}
  Response: { exercise: ExerciseDetail }
  ExerciseDetail: full exercise + muscles[] + substitutions[] + instructions + tips

GET /api/exercises/{id}/substitutions
  Response: { substitutions: Substitution[] }
  Substitution: { exercise: ExerciseListItem, similarity: float, reason: str }

GET /api/exercises/search?q=bench+press
  Response: { exercises: ExerciseListItem[] }
  Logic: ILIKE search on display_name, with fuzzy matching using trigram similarity if pg_trgm is available

GET /api/muscle-groups
  Response: { muscle_groups: MuscleGroup[] }
  Grouped by body_region

GET /api/muscle-groups/{id}/exercises
  Response: { exercises: ExerciseListItem[], role_filter?: str }
  Query param: ?role=primary (optional, defaults to all roles)
```

**Acceptance criteria:**
- All filters work individually and combined
- Search returns relevant results for partial matches ("bench" finds "Barbell Bench Press")
- Substitutions are returned with similarity scores
- Empty filters return all results (paginated)

---

### Task 1.6: Workout Logging API

**Do:**
1. `backend/app/api/workouts.py` — routes
2. `backend/app/services/workout_service.py` — logic
3. `backend/app/schemas/workout.py` — schemas

**Endpoints:**
```
POST /api/workouts
  Request: { session_name?: str, started_at?: datetime }  — started_at defaults to NOW()
  Response: { session: WorkoutSession }

PUT /api/workouts/{id}
  Request: { session_name?: str, notes?: str, overall_rpe?: float, bodyweight_kg?: float, finished_at?: datetime }
  Response: { session: WorkoutSession }
  On finish (finished_at provided): compute total_volume_kg, total_sets, duration_minutes

DELETE /api/workouts/{id}
  Response: 204

GET /api/workouts
  Query: ?from=2024-01-01&to=2024-12-31&limit=20&offset=0
  Response: { sessions: WorkoutSessionSummary[], total: int }

GET /api/workouts/{id}
  Response: { session: WorkoutSessionDetail }
  Includes: exercises[] with sets[], computed stats

POST /api/workouts/{session_id}/exercises
  Request: { exercise_id: int, exercise_order?: int }
  Response: { workout_exercise: WorkoutExercise }

POST /api/workouts/{session_id}/exercises/{we_id}/sets
  Request: { weight_kg: float, reps: int, rpe?: float, rir?: int, set_type?: str }
  Response: { set: SetResponse }
  On create:
    1. Auto-compute estimated_1rm using Epley formula: weight * (1 + reps/30)
    2. Auto-set set_order based on existing sets
    3. Check if this is a PR (compare estimated_1rm against all previous sets for this exercise by this user)
    4. Return the set with { is_pr, estimated_1rm, previous_best_1rm }

PUT /api/workouts/{session_id}/exercises/{we_id}/sets/{set_id}
  Request: partial set update
  Response: { set: SetResponse }

DELETE /api/workouts/{session_id}/exercises/{we_id}/sets/{set_id}
  Response: 204

POST /api/quick-log
  Request: { exercise_name: str, weight_kg: float, reps: int, rpe?: float }
  Logic:
    1. Find or fuzzy-match exercise by name
    2. Find active session (started today, not finished) or create new one
    3. Find or create workout_exercise entry
    4. Log the set
  Response: { session_id, set: SetResponse }
```

**Business rules:**
- A user can only have one unfinished session at a time
- Sets must have weight_kg > 0 and reps > 0
- RPE must be between 6.0 and 10.0 in 0.5 increments if provided
- Finishing a session triggers post-session analytics (Phase 3, for now just compute totals)

**Acceptance criteria:**
- Full CRUD for sessions, exercises within sessions, sets within exercises
- 1RM auto-calculation on every set
- PR detection works correctly
- Quick-log creates session if needed and matches exercises by name
- Deleting a session cascades to exercises and sets

---

## PHASE 2: Frontend PWA + Core UI

### Task 2.1: Frontend Scaffolding

**Do:**
1. `pnpm create vite frontend --template react-ts`
2. Install: `pnpm add tailwindcss @tailwindcss/vite react-router-dom zustand axios recharts lucide-react`
3. Install Shadcn/UI: follow shadcn docs for Vite + Tailwind v4
4. Configure PWA: manifest.json, service worker (basic cache-first for static assets)
5. Set up routing with React Router:
   ```
   /                → Dashboard
   /workout         → WorkoutLogger (active session)
   /workout/history → Past sessions list
   /exercises       → Exercise browser
   /exercises/:id   → Exercise detail
   /analytics       → Analytics dashboard
   /insights        → Insights feed
   /programs        → Training programs
   /profile         → User profile + settings
   /login           → Auth page
   ```
6. Bottom navigation bar (mobile): Home, Workout, Exercises, Analytics, Profile
7. API service (`src/services/api.ts`): Axios instance with baseURL, JWT interceptor, refresh logic
8. Auth store + protected route wrapper

**Design system:**
- Background: zinc-950
- Card background: zinc-900
- Border: zinc-800
- Primary accent: emerald-500
- Warning: amber-500
- Danger: red-500
- Text primary: zinc-50
- Text secondary: zinc-400
- Font: Inter (import from Google Fonts)
- Border radius: 12px for cards, 8px for inputs/buttons
- Bottom nav height: 64px + safe area inset

**Acceptance criteria:**
- App loads on mobile (375px), all routes work
- Bottom nav visible on all pages
- Auth flow: login → redirect to dashboard, unauthorized → redirect to login
- PWA installable (Add to Home Screen works on iOS Safari)
- Dark theme applied globally

---

### Task 2.2: Workout Logger Screen (THE critical screen)

**This is the most important screen. If logging is annoying, the project fails.**

**Layout (top to bottom):**
```
┌─────────────────────────────┐
│ [←]  Push Day    ⏱ 00:34:12 │  ← Session header: name + timer
├─────────────────────────────┤
│ ┌───────────────────────────┐│
│ │ Barbell Bench Press     ⋮ ││  ← Exercise card (collapsible)
│ │ Last: 80×8, 82.5×7, 80×6 ││  ← Ghost of previous session
│ │                           ││
│ │  #  WEIGHT  REPS  RPE  ✓ ││
│ │  1  80.0    8     8   [✓]││  ← Logged set (muted)
│ │  2  82.5    -     -   [ ]││  ← Active set row (pre-filled weight suggestion)
│ │                           ││
│ │  [+ Add Set]              ││
│ └───────────────────────────┘│
│ ┌───────────────────────────┐│
│ │ Incline DB Press        ⋮ ││  ← Next exercise
│ │ ...                       ││
│ └───────────────────────────┘│
│                               │
│    [+ Add Exercise]           │  ← Opens exercise picker
│                               │
│    [Finish Workout]           │  ← Ends session, shows summary
├─────────────────────────────┤
│ 🏠  🏋️  📋  📊  👤           │  ← Bottom nav
└─────────────────────────────┘
```

**WeightInput component:**
- NOT a text field. Use a numeric display with +/- buttons.
- Buttons: [-5] [-2.5] [WEIGHT DISPLAY] [+2.5] [+5]
- Tap the weight display to type manually via numpad modal
- Pre-fills with either: suggested weight from model, or last set's weight

**Reps input:**
- Numeric stepper: [-] [REPS] [+]
- Tap to type manually

**RPE input:**
- Optional, collapsible by default
- Pill selector: [6] [6.5] [7] [7.5] [8] [8.5] [9] [9.5] [10]

**Set logging flow (target: 2-3 taps for a normal set):**
1. Weight pre-filled from suggestion or previous set → adjust if needed (0-1 taps)
2. Reps pre-filled to match previous session → adjust if needed (0-1 taps)
3. Tap checkmark ✓ to log (1 tap)
4. Set row locks (muted color), rest timer starts, new empty row appears

**Rest timer:**
- Auto-starts after logging a set
- Shows countdown in a toast/banner at top
- Default 90s for isolation, 180s for compound (configurable)
- Tap to dismiss

**Exercise picker (opened by "Add Exercise"):**
- Search bar at top (autofocus)
- Recent/Favorites section
- Filtered list with muscle group colored dots
- Tap exercise → added to current workout, picker closes

**PR celebration:**
- When a set is logged that's a new estimated 1RM PR:
- Brief animation (confetti/flash — keep it subtle)
- Toast: "New PR! Bench Press e1RM: 105kg (+2.5kg)"

**Acceptance criteria:**
- Can log a set in 3 taps or fewer when weight/reps are pre-filled
- Previous session ghost data visible for each exercise
- Rest timer auto-starts
- Exercise picker search works with partial matching
- PR detection and celebration works
- Session timer runs continuously
- Finish workout shows summary (total volume, exercises, sets, duration, any PRs)

---

### Task 2.3: Dashboard Screen

**Layout:**
```
┌─────────────────────────────┐
│ Good evening, Shrey          │
├─────────────────────────────┤
│ ┌─── Readiness ───────────┐ │  ← Color-coded (green/yellow/red)
│ │   [placeholder for ML]   │ │     Shows "Log more to unlock" if < 4 weeks data
│ └─────────────────────────┘ │
│                               │
│ ┌─── This Week ───────────┐ │
│ │ Sessions: 3/5            │ │
│ │ Volume: 42,350 kg        │ │
│ │ Sets: 68                 │ │
│ └─────────────────────────┘ │
│                               │
│ ┌─── Recovery ────────────┐ │  ← Body silhouette with colored muscle groups
│ │ [Body Map placeholder]   │ │     Green=ready, Yellow=recovering, Red=fatigued
│ │ or simple list for v1:   │ │
│ │  Chest    ████░░ 72%     │ │
│ │  Quads    ██░░░░ 35%     │ │
│ │  Lats     █████░ 90%     │ │
│ └─────────────────────────┘ │
│                               │
│ ┌─── Insights ────────────┐ │  ← Top 3 unread insights
│ │ ⚠ Bench plateaued 3wks  │ │
│ │ ℹ Rear delts: 0 sets    │ │
│ │ 🎉 Squat PR: 140kg      │ │
│ └─────────────────────────┘ │
│                               │
│  [ Start Workout ]            │  ← Big CTA button
├─────────────────────────────┤
│ 🏠  🏋️  📋  📊  👤           │
└─────────────────────────────┘
```

**Acceptance criteria:**
- Weekly summary card with real data
- Recovery section shows placeholder or simple list for v1
- Insights show real insights once ML is active, placeholder otherwise
- "Start Workout" navigates to /workout and creates a new session

---

### Task 2.4: Exercise Browser + Detail

**Browser:**
- Search bar with filter chips (muscle group, equipment, movement pattern)
- Grid/list of exercise cards
- Each card: name, equipment icon, primary muscle dots

**Detail page:**
- Exercise name, equipment, difficulty
- Muscles targeted (primary in bold, secondary in lighter color)
- Instructions, tips, common mistakes (collapsible sections)
- Personal stats: e1RM, total sessions, total volume, last performed date
- Substitutions: list of alternatives with similarity %
- History: chronological list of every time this exercise was performed

**Acceptance criteria:**
- Search + filters work together
- Detail page loads with all knowledge base data
- Personal stats show real data if available, "No data yet" otherwise

---

### Task 2.5: Analytics Dashboard (basic — ML charts come in Phase 3)

**Charts to implement now (non-ML):**
1. Volume per muscle group this week (horizontal bar chart)
2. Training frequency calendar (GitHub-style heatmap — days trained)
3. Estimated 1RM over time per exercise (line chart, select exercise from dropdown)
4. Total weekly volume trend (line chart, last 12 weeks)
5. PR log (timeline of personal records)

**Acceptance criteria:**
- All charts render with real data
- Exercise selector for 1RM chart works
- Empty states for charts with no data

---

## PHASE 3: ML Models + Background Jobs

### Task 3.1: Celery + Redis Setup

**Do:**
1. Add Redis to docker-compose
2. Create `backend/app/tasks/celery_app.py` with Celery config
3. Create worker Dockerfile / docker-compose service
4. Wire up: finishing a workout session triggers `post_session_analytics` task

**Acceptance criteria:**
- Celery worker starts and connects to Redis
- Finishing a workout (PUT with finished_at) enqueues post_session_analytics task
- Task runs and completes without error

---

### Task 3.2: Volume Analyzer

**File: `backend/app/ml/volume_analyzer.py`**

**Class: VolumeAnalyzer**

```
Method: compute_weekly_volume(user_id, week_start_date) -> dict[muscle_group_id, VolumeStats]
  Logic:
  1. Query all sets from workout_sessions in that week for the user
  2. For each set, look up exercise_muscles to get muscle group mappings
  3. For each muscle group, count "hard sets" (sets where RPE >= 7 or RIR <= 3 or set_type='working')
  4. Weight sets by activation_pct from exercise_muscles
  5. Compare against MEV/MRV from muscle_groups table
  6. Return: { muscle_group_id: { total_sets, total_volume_kg, avg_rpe, status } }

Method: detect_imbalances(user_id, window_weeks=4) -> list[Imbalance]
  Logic:
  1. Compute weekly volumes for the last N weeks
  2. Calculate push:pull set ratio (sum of push muscle sets vs pull muscle sets)
  3. Calculate quad:hamstring ratio
  4. Identify muscle groups with 0 sets for 2+ consecutive weeks
  5. Return imbalances with type, severity, message

Method: weekly_volume_trend(user_id, exercise_id?, weeks=12) -> list[WeeklyVolume]
  Returns volume per week for trend charts
```

**Store results in `muscle_group_volume` table after computation.**

**Acceptance criteria:**
- Volume computation accounts for primary/secondary muscle activation weights
- Status correctly identifies under_mev, in_range, over_mrv
- Push:pull ratio calculation is correct
- Imbalance detection flags muscle groups not trained in 14+ days

---

### Task 3.3: Strength Curve Model (Gaussian Process)

**File: `backend/app/ml/strength_curve.py`**

**Class: StrengthCurveModel**

```
MIN_DATA_POINTS = 20  # below this, use Epley average only

Method: fit(user_id, exercise_id) -> ModelState
  1. Query all working sets for this exercise by this user
  2. Compute Epley e1RM for each set as label
  3. Features: [days_since_first_set, reps, rpe_normalized(0-1)]
  4. If < 20 data points: store simple average + std of Epley estimates, return
  5. If >= 20: fit GP with Matern(nu=2.5) + WhiteKernel
  6. Store fitted model parameters in strength_estimates table

Method: predict(user_id, exercise_id, target_date) -> Prediction
  Returns: { estimated_1rm, confidence_low, confidence_high, data_points, model_type }
  model_type: "epley_average" or "gaussian_process"

Method: predict_reps_at_weight(user_id, exercise_id, weight) -> int
  Inverse of 1RM formula: how many reps can user do at this weight?

Method: get_strength_timeline(user_id, exercise_id, weeks=24) -> list[StrengthPoint]
  Returns weekly 1RM estimates with confidence bands for charting
```

**Acceptance criteria:**
- Returns "insufficient data" gracefully below 20 data points
- GP predictions have reasonable confidence intervals (widen with sparse data)
- Strength timeline produces smooth curves suitable for charting
- Model retraining completes in < 5s for a single exercise

---

### Task 3.4: Plateau Detector

**File: `backend/app/ml/plateau_detector.py`**

**Class: PlateauDetector**

```
MIN_DATA_POINTS = 15  # minimum e1RM data points to run detection
MIN_PLATEAU_WEEKS = 3  # minimum weeks of stagnation to flag

Method: detect(user_id, exercise_id) -> list[PlateauEvent] | None
  1. Get e1RM time series from strength_estimates table
  2. If < 15 points, return None
  3. Run PELT changepoint detection (model="l2", min_size=4, pen=3.0)
  4. Extract segments between changepoints
  5. For each segment, compute linear slope
  6. If slope < threshold (0.5 kg/week) AND duration >= 3 weeks → plateau
  7. Generate rule-based recommendation:
     - High volume (>MRV) → "Consider a deload week"
     - Low volume (<MEV) → "Try adding 2-3 more sets per week"
     - Same rep range for 4+ weeks → "Try varying rep ranges (switch from 8-10 to 4-6)"
     - Only one exercise for this muscle → "Add exercise variation"
  8. Store in plateau_detections table

Method: check_resolved(user_id, exercise_id) -> bool
  If e1RM in the last 2 weeks exceeds plateau e1RM by > 2%, mark as resolved
```

**Acceptance criteria:**
- Returns None gracefully with insufficient data
- Correctly identifies flat segments in a time series
- Recommendations are contextual (based on actual training data, not generic)
- Resolved detection works

---

### Task 3.5: Recovery Model (Banister)

**File: `backend/app/ml/recovery_model.py`**

**Class: BanisterRecoveryModel**

```
Default parameters:
  tau_fitness = 45 days
  tau_fatigue = 15 days
  k_fitness = 1.0
  k_fatigue = 2.0

Method: compute_training_impulse(sets, avg_rpe, total_volume) -> float
  impulse = sets * ((avg_rpe - 5) / 5) * (log(1 + total_volume) / 10)
  Clamp to [0, 10]

Method: compute_recovery_state(user_id) -> dict[muscle_group_id, RecoveryState]
  1. Get all sessions from last 60 days
  2. For each session, compute per-muscle-group impulse (using exercise_muscles mappings)
  3. Simulate Banister model forward for each muscle group
  4. Compute current recovery_pct and predicted next_ready_at
  5. Store in recovery_state table

Method: personalize(user_id, muscle_group_id) -> PersonalizedParams
  Requires 8+ weeks of data with RPE logging
  Uses scipy.optimize.minimize to fit tau_fitness, tau_fatigue, k_fitness, k_fatigue
  Actual performance signal: compare predicted e1RM vs actual session e1RM

Method: predict_readiness_at(user_id, muscle_group_id, future_date) -> float
  Extrapolate current state forward assuming no training between now and future_date
```

**Acceptance criteria:**
- Recovery percentages are between 0-100%
- Muscles trained recently show lower recovery
- Muscles not trained in 5+ days show high recovery
- Personalization only runs with sufficient data (8+ weeks)

---

### Task 3.6: Autoregulation Engine

**File: `backend/app/ml/autoregulation.py`**

**Class: AutoregulationEngine**

```
Method: compute_readiness(user_id, session_id) -> ReadinessScore
  1. For each exercise in the session, compare actual e1RM vs predicted e1RM
  2. readiness_ratio = mean(actual / predicted) across exercises
  3. Score: > 1.05 = "great", 0.95-1.05 = "normal", 0.85-0.95 = "fatigued", < 0.85 = "consider_deload"
  4. Store as insight if notable

Method: suggest_weight(user_id, exercise_id, target_reps, target_rpe) -> WeightSuggestion
  1. Get current e1RM estimate from strength_curve model
  2. Apply Epley inverse: weight = e1RM / (1 + target_reps/30)
  3. Apply RPE adjustment: multiply by (10 - target_rpe + target_reps) / (10 + target_reps) — approximate
  4. Apply recent readiness modifier (if last 3 sessions show fatigue trend, reduce by 2-5%)
  5. Round to nearest 2.5 kg
  6. Return: { suggested_weight, if_feeling_good: +2.5kg, if_feeling_off: -2.5kg, basis: "e1RM of Xkg" }

  MIN_DATA: 10 sets of this exercise to make weight suggestions
```

**Acceptance criteria:**
- Weight suggestions are reasonable (not wildly off from recent performance)
- Readiness score reflects actual vs predicted performance gap
- Graceful "insufficient data" for new exercises

---

### Task 3.7: Split Optimizer

**File: `backend/app/ml/split_optimizer.py`**

**Class: SplitOptimizer**

```
Method: generate_split(user_id, constraints: SplitConstraints) -> WeeklyProgram
  Inputs:
    - available_days: list[int]  # 0=Mon, 6=Sun
    - session_duration_minutes: int  # max time per session
    - goal: "hypertrophy" | "strength" | "balanced"
    - experience_level: "beginner" | "intermediate" | "advanced"

  Logic:
  1. Determine target frequency per muscle group (based on goal + experience):
     - Beginner: 2x/week full body
     - Intermediate: each muscle 2x/week, PPL or Upper/Lower
     - Advanced: each muscle 2-3x/week
  2. Determine target weekly sets per muscle group (from volume landmarks, adjusted for goal)
  3. Assign muscle groups to days to minimize recovery conflict:
     - Don't train same muscle group on consecutive days
     - Balance session volume (sets) across days
     - Keep synergistic muscles together (chest + tricep + front delt on same day)
  4. For each day, select exercises:
     - Start with compound movements
     - Fill remaining volume with isolation
     - Prefer exercises user has history with (better tracking)
     - Ensure movement pattern variety (not all horizontal push)
  5. Assign set/rep prescriptions based on goal:
     - Hypertrophy: 3-4 sets × 8-12 reps
     - Strength: 4-5 sets × 3-6 reps (compounds), 3 sets × 8-12 (accessories)
     - Balanced: mix

  Return: WeeklyProgram with days, exercises per day, set/rep targets

Method: suggest_exercise_swap(exercise_id, reason) -> list[ExerciseSuggestion]
  Given an exercise and reason for swap (equipment unavailable, joint pain, boredom),
  return ranked alternatives from exercise_substitutions table
```

**Acceptance criteria:**
- Generated splits are valid (no muscle group trained on consecutive days)
- Session lengths are within constraint
- Volume targets are met (within 10%)
- Exercise selection is sensible (compounds first, variety enforced)

---

### Task 3.8: Post-Session Analytics Pipeline

**File: `backend/app/tasks/post_session.py`**

**Celery task: post_session_analytics(session_id)**

```
Triggered when: workout session is finished (PUT with finished_at)

Steps (in order):
1. Compute and store session totals (total_volume_kg, total_sets, duration)
2. Compute and store estimated_1rm for each workout_exercise (best e1RM from its sets)
3. Update muscle_group_volume for the current week
4. Update recovery_state for affected muscle groups
5. Check for new PRs across all exercises in this session → generate 'pr' insights
6. Run plateau detection for exercises with sufficient data → generate 'plateau' insights
7. Run volume analyzer → generate 'volume_warning' or 'imbalance' insights if applicable
8. Compute readiness score for this session
9. Log completion
```

**Acceptance criteria:**
- All 9 steps execute without error
- Insights are created in the database
- Recovery state is updated for the correct muscle groups
- PRs are correctly detected by comparing against ALL historical sets, not just current session

---

### Task 3.9: Nightly + Weekly Jobs

**Nightly (`backend/app/tasks/nightly.py`):**
```
Schedule: 2:00 AM UTC daily

1. For each active user:
   a. Retrain strength curve models for exercises with new data since last train
   b. Recompute recovery state (fatigue decays even without training)
   c. Check for muscle groups not trained in 10+ days → generate 'recommendation' insight
```

**Weekly (`backend/app/tasks/weekly.py`):**
```
Schedule: Sunday 8:00 PM UTC

1. For each active user:
   a. Generate weekly summary insight:
      - Sessions, total volume, duration
      - Volume per muscle group vs targets
      - Strength changes (Δ1RM for top exercises)
      - Top recommendation for next week
   b. Recompute volume trends
   c. Run full imbalance detection
```

**Acceptance criteria:**
- Jobs run on schedule via Celery beat
- Jobs are idempotent (running twice doesn't create duplicate insights)
- Recovery state decays correctly even on rest days

---

### Task 3.10: ML-Enhanced Frontend

**Update these screens with real ML data:**

1. **Dashboard:** Recovery section shows real recovery_state data (colored bars per muscle group)
2. **Dashboard:** Readiness score from autoregulation engine (or "Keep logging to unlock")
3. **Dashboard:** Insights feed from training_insights table
4. **Analytics:** Strength chart now shows GP confidence bands (shaded area around line)
5. **Analytics:** Volume chart shows MEV/MRV threshold lines
6. **Analytics:** Add "Plateaus" section showing active plateaus with recommendations
7. **Workout Logger:** Weight suggestion from autoregulation engine (shown as pre-fill)
8. **Workout Logger:** Rest timer defaults based on exercise type (compound vs isolation)
9. **Exercise Detail:** Show strength curve with confidence bands
10. **Exercise Detail:** Show plateau status if active

**Acceptance criteria:**
- All ML data renders correctly when available
- All ML sections show appropriate empty/placeholder state when data is insufficient
- Confidence bands are visually clear (shaded area, not just lines)
- MEV/MRV lines on volume chart are labeled

---

## PHASE 4: Smart Programming + Recommendations

### Task 4.1: Program Generation UI
- "Generate Split" button on Programs page
- Form: available days, session duration, goal, experience level
- Calls split optimizer API
- Displays generated program with day-by-day breakdown
- "Accept" saves as active program
- "Regenerate" gets a new suggestion

### Task 4.2: Recommendation Endpoints
```
GET /api/recommend/weight/{exercise_id}?target_reps=8&target_rpe=8
GET /api/recommend/exercises?muscle_group=chest&exclude_ids=1,2,3
GET /api/recommend/deload  — returns boolean + reasoning
GET /api/recommend/next-session — based on active program + recovery state
```

### Task 4.3: Deload Detection
- Monitor weekly volume trend
- If volume has increased for 4+ consecutive weeks AND readiness scores are declining → suggest deload
- Deload prescription: 50% volume, maintain intensity, 1 week

---

## PHASE 5: Polish

### Task 5.1: Offline Support
- Service worker caches static assets + exercise knowledge base
- IndexedDB queue for set logging when offline
- Sync queue when connection returns
- Visual indicator when offline

### Task 5.2: PWA Polish
- Install prompt (beforeinstallprompt event)
- Splash screen
- Status bar theme color
- iOS standalone mode meta tags

### Task 5.3: Data Export
- GET /api/export/csv — full training history as CSV
- GET /api/export/json — full data dump

### Task 5.4: Error Handling + Empty States
- Every screen has loading skeleton
- Every screen has empty state with helpful CTA
- API errors show toast notifications
- Form validation with clear error messages

### Task 5.5: Docker Compose Production Config
- Multi-stage Dockerfile for backend
- Nginx for frontend serving
- Environment variable configuration
- Health checks on all services

---

## APPENDIX A: 1RM Formulas

```python
def epley_1rm(weight: float, reps: int) -> float:
    """Most common formula. Accurate for 2-10 rep range."""
    if reps == 1:
        return weight
    return weight * (1 + reps / 30)

def brzycki_1rm(weight: float, reps: int) -> float:
    """More conservative. Accurate for 1-10 rep range."""
    if reps == 1:
        return weight
    if reps >= 37:
        return weight  # formula breaks down
    return weight * 36 / (37 - reps)

def combined_1rm(weight: float, reps: int) -> float:
    """Average of Epley and Brzycki for best estimate."""
    return (epley_1rm(weight, reps) + brzycki_1rm(weight, reps)) / 2
```

## APPENDIX B: Volume Landmarks Reference (Israetel)

```python
VOLUME_LANDMARKS = {
    "chest":       {"mev": 10, "mrv": 22, "optimal": [12, 18]},
    "lats":        {"mev": 10, "mrv": 22, "optimal": [12, 18]},
    "side_delt":   {"mev":  8, "mrv": 26, "optimal": [12, 20]},
    "rear_delt":   {"mev":  8, "mrv": 22, "optimal": [12, 18]},
    "quads":       {"mev":  8, "mrv": 20, "optimal": [12, 18]},
    "hamstrings":  {"mev":  6, "mrv": 16, "optimal": [10, 14]},
    "glutes":      {"mev":  4, "mrv": 16, "optimal": [8,  14]},
    "biceps":      {"mev":  8, "mrv": 22, "optimal": [10, 18]},
    "triceps":     {"mev":  6, "mrv": 18, "optimal": [8,  14]},
    "forearms":    {"mev":  4, "mrv": 16, "optimal": [6,  12]},
    "upper_back":  {"mev": 10, "mrv": 22, "optimal": [12, 18]},
    "calves":      {"mev":  6, "mrv": 16, "optimal": [8,  14]},
    "abs":         {"mev":  6, "mrv": 20, "optimal": [8,  16]},
    "lower_back":  {"mev":  4, "mrv": 12, "optimal": [6,  10]},
}
```

## APPENDIX C: RPE to RIR Mapping

```
RPE 10   = 0 RIR (failure)
RPE 9.5  = 0-1 RIR
RPE 9    = 1 RIR
RPE 8.5  = 1-2 RIR
RPE 8    = 2 RIR
RPE 7.5  = 2-3 RIR
RPE 7    = 3 RIR
RPE 6    = 4 RIR
```
