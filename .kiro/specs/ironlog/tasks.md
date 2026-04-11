# IronLog — Implementation Tasks

Reference spec: `ironlog-kiro-spec.md`

---

## PHASE 1: Backend Foundation + Database

- [x] 1.1 Project Scaffolding
  - [x] 1.1.1 Create full directory structure (ironlog/backend + ironlog/frontend trees with empty __init__.py files)
  - [x] 1.1.2 Create backend/requirements.txt with pinned dependencies
  - [x] 1.1.3 Create backend/app/config.py (Pydantic BaseSettings)
  - [x] 1.1.4 Create backend/app/main.py (FastAPI app factory, CORS, /health endpoint)
  - [x] 1.1.5 Create backend/app/database.py (async SQLAlchemy engine + session)
  - [x] 1.1.6 Create backend/app/dependencies.py (get_db stub)
  - [x] 1.1.7 Create backend/.env.example
  - [x] 1.1.8 Create docker-compose.dev.yml (postgres:16, redis:7, backend with uvicorn reload)
  - [x] 1.1.9 Create Makefile with dev shortcuts

- [x] 1.2 Database Models + Migrations
  - [x] 1.2.1 Create backend/app/models/user.py (users table)
  - [x] 1.2.2 Create backend/app/models/exercise.py (muscle_groups, exercises, exercise_muscles, exercise_substitutions)
  - [x] 1.2.3 Create backend/app/models/workout.py (workout_sessions, workout_exercises, sets, user_exercises)
  - [x] 1.2.4 Create backend/app/models/program.py (training_programs, program_days)
  - [x] 1.2.5 Create backend/app/models/analytics.py (strength_estimates, muscle_group_volume, plateau_detections, recovery_state, training_insights)
  - [x] 1.2.6 Configure Alembic (alembic.ini, env.py pointing to async engine)
  - [x] 1.2.7 Generate initial migration and verify alembic upgrade head / downgrade base

- [x] 1.3 Exercise Knowledge Base Seed Data
  - [x] 1.3.1 Create backend/app/seed/muscle_groups.json (22 entries, exact data from spec)
  - [x] 1.3.2 Create backend/app/seed/exercises.json (120+ exercises with muscles + substitutions)
  - [x] 1.3.3 Create backend/app/seed/seed_db.py (idempotent seeder, ON CONFLICT DO NOTHING)

- [x] 1.4 Authentication
  - [x] 1.4.1 Create backend/app/schemas/auth.py (RegisterRequest, LoginRequest, TokenResponse, UserResponse)
  - [x] 1.4.2 Create backend/app/services/auth_service.py (register, login, refresh, password hashing)
  - [x] 1.4.3 Create backend/app/api/auth.py (POST /register, /login, /refresh)
  - [x] 1.4.4 Implement get_current_user dependency in dependencies.py

- [x] 1.5 Exercise Knowledge Base API
  - [x] 1.5.1 Create backend/app/schemas/exercise.py
  - [x] 1.5.2 Create backend/app/services/exercise_service.py (filters, search, substitutions)
  - [x] 1.5.3 Create backend/app/api/exercises.py (GET /exercises, /exercises/{id}, /exercises/{id}/substitutions, /exercises/search, /muscle-groups, /muscle-groups/{id}/exercises)
  - [x] 1.5.4 Create backend/app/api/router.py (aggregate all routers)

- [x] 1.6 Workout Logging API
  - [x] 1.6.1 Create backend/app/schemas/workout.py
  - [x] 1.6.2 Create backend/app/services/workout_service.py (CRUD, 1RM calc, PR detection, quick-log)
  - [x] 1.6.3 Create backend/app/api/workouts.py (full CRUD + sets endpoints + quick-log)

---

## PHASE 2: Frontend PWA + Core UI

- [x] 2.1 Frontend Scaffolding
  - [x] 2.1.1 Scaffold Vite + React + TypeScript project in ironlog/frontend
  - [x] 2.1.2 Install and configure Tailwind CSS v4 + Shadcn/UI
  - [x] 2.1.3 Set up React Router with all routes defined in spec
  - [x] 2.1.4 Create src/services/api.ts (Axios instance, JWT interceptor, refresh logic)
  - [x] 2.1.5 Create src/stores/authStore.ts (Zustand) + ProtectedRoute wrapper
  - [x] 2.1.6 Create src/components/NavigationBar.tsx (bottom tab bar, mobile)
  - [x] 2.1.7 Create src/types/index.ts (TypeScript interfaces mirroring Pydantic schemas)
  - [x] 2.1.8 Create src/lib/constants.ts (RPE scale, unit conversions, volume landmarks)
  - [x] 2.1.9 Configure PWA (manifest.json, sw.js cache-first, iOS meta tags)
  - [x] 2.1.10 Create pages/Login.tsx (auth form)

- [-] 2.2 Workout Logger Screen
  - [x] 2.2.1 Create src/stores/workoutStore.ts (Zustand — active session state)
  - [x] 2.2.2 Create src/hooks/useWorkoutSession.ts
  - [x] 2.2.3 Create src/components/WeightInput.tsx (numeric display + ±2.5/±5 buttons + numpad modal)
  - [x] 2.2.4 Create src/components/SetLoggerRow.tsx (weight + reps + RPE + checkmark)
  - [x] 2.2.5 Create src/components/RestTimer.tsx (countdown toast, auto-start on set log)
  - [x] 2.2.6 Create src/pages/ExercisePicker.tsx (search + filter + recent)
  - [x] 2.2.7 Create src/pages/WorkoutLogger.tsx (full logger screen with session header, exercise cards, finish flow)

- [ ] 2.3 Dashboard Screen
  - [x] 2.3.1 Create src/pages/Dashboard.tsx (greeting, readiness placeholder, weekly summary, recovery list, insights preview, Start Workout CTA)

- [ ] 2.4 Exercise Browser + Detail
  - [x] 2.4.1 Create src/components/ExerciseCard.tsx
  - [x] 2.4.2 Create src/pages/Exercises.tsx (search + filter chips + exercise list)
  - [x] 2.4.3 Create src/pages/ExerciseDetail.tsx (full detail: muscles, instructions, personal stats, substitutions, history)

- [ ] 2.5 Analytics Dashboard (basic)
  - [x] 2.5.1 Create src/stores/analyticsStore.ts
  - [x] 2.5.2 Create src/hooks/useAnalytics.ts
  - [x] 2.5.3 Create src/components/VolumeChart.tsx (horizontal bar — volume per muscle group)
  - [x] 2.5.4 Create src/components/StrengthChart.tsx (line chart — e1RM over time)
  - [x] 2.5.5 Create src/pages/Analytics.tsx (volume chart, frequency heatmap, 1RM chart, weekly volume trend, PR log)

---

## PHASE 3: ML Models + Background Jobs

- [x] 3.1 Celery + Redis Setup
  - [x] 3.1.1 Create backend/app/tasks/celery_app.py (Celery config, broker=Redis)
  - [x] 3.1.2 Add Celery worker service to docker-compose
  - [x] 3.1.3 Wire finishing a session to enqueue post_session_analytics task

- [x] 3.2 Volume Analyzer
  - [x] 3.2.1 Create backend/app/ml/volume_analyzer.py (VolumeAnalyzer class: compute_weekly_volume, detect_imbalances, weekly_volume_trend)

- [x] 3.3 Strength Curve Model
  - [x] 3.3.1 Create backend/app/ml/strength_curve.py (StrengthCurveModel: fit, predict, predict_reps_at_weight, get_strength_timeline — GP with Matern kernel)

- [x] 3.4 Plateau Detector
  - [x] 3.4.1 Create backend/app/ml/plateau_detector.py (PlateauDetector: detect via PELT changepoint, check_resolved, contextual recommendations)

- [x] 3.5 Recovery Model
  - [x] 3.5.1 Create backend/app/ml/recovery_model.py (BanisterRecoveryModel: compute_training_impulse, compute_recovery_state, personalize, predict_readiness_at)

- [x] 3.6 Autoregulation Engine
  - [x] 3.6.1 Create backend/app/ml/autoregulation.py (AutoregulationEngine: compute_readiness, suggest_weight)

- [x] 3.7 Split Optimizer
  - [x] 3.7.1 Create backend/app/ml/split_optimizer.py (SplitOptimizer: generate_split, suggest_exercise_swap)

- [x] 3.8 Post-Session Analytics Pipeline
  - [x] 3.8.1 Create backend/app/tasks/post_session.py (9-step Celery task: totals → 1RM → volume → recovery → PRs → plateaus → imbalances → readiness → log)

- [x] 3.9 Nightly + Weekly Jobs
  - [x] 3.9.1 Create backend/app/tasks/nightly.py (retrain models, recompute recovery, inactivity insights)
  - [x] 3.9.2 Create backend/app/tasks/weekly.py (weekly summary insight, volume trends, imbalance detection)
  - [x] 3.9.3 Configure Celery beat schedule for nightly (2AM UTC) and weekly (Sun 8PM UTC)

- [x] 3.10 ML-Enhanced Backend API
  - [x] 3.10.1 Create backend/app/api/analytics.py (analytics endpoints)
  - [x] 3.10.2 Create backend/app/schemas/analytics.py (analytics response schemas)
  - [x] 3.10.3 Wire analytics router to main API

- [ ] 3.11 ML-Enhanced Frontend (Frontend integration with ML backend)
  - [ ] 3.11.1 Update Dashboard: real recovery_state bars, readiness score, insights feed
  - [ ] 3.11.2 Update Analytics: GP confidence bands on strength chart, MEV/MRV lines on volume chart, Plateaus section
  - [ ] 3.11.3 Update WorkoutLogger: weight suggestion pre-fill, compound vs isolation rest timer defaults
  - [ ] 3.11.4 Update ExerciseDetail: strength curve with confidence bands, plateau status

---

## PHASE 4: Smart Programming + Recommendations

- [-] 4.1 Program Generation UI
  - [x] 4.1.1 Create backend/app/schemas/program.py + backend/app/api/programs.py (generate split endpoint)
  - [ ] 4.1.2 Create src/pages/Programs.tsx (Generate Split form, day-by-day display, Accept/Regenerate)

- [x] 4.2 Recommendation Endpoints
  - [x] 4.2.1 Create backend/app/services/recommendation_service.py
  - [x] 4.2.2 Create backend/app/api/recommendations.py (GET /recommend/weight/{id}, /recommend/exercises, /recommend/deload, /recommend/next-session)

- [x] 4.3 Deload Detection
  - [x] 4.3.1 Implement deload detection logic in recommendation_service.py (4+ weeks volume increase + declining readiness → suggest deload)

---

## PHASE 5: Polish

- [ ] 5.1 Offline Support
  - [ ] 5.1.1 Create src/services/offlineQueue.ts (IndexedDB queue for sets)
  - [ ] 5.1.2 Create src/hooks/useOfflineSync.ts (sync on reconnect)
  - [ ] 5.1.3 Update sw.js (cache exercise knowledge base, static assets)
  - [ ] 5.1.4 Add offline indicator UI

- [ ] 5.2 PWA Polish
  - [ ] 5.2.1 Add beforeinstallprompt install banner
  - [ ] 5.2.2 Splash screen + status bar theme + iOS standalone meta tags

- [ ] 5.3 Data Export
  - [ ] 5.3.1 Create backend/app/api/export endpoints (GET /export/csv, /export/json)

- [ ] 5.4 Error Handling + Empty States
  - [ ] 5.4.1 Add loading skeletons to all pages
  - [ ] 5.4.2 Add empty states with CTAs to all pages
  - [ ] 5.4.3 Add global toast notification system for API errors
  - [ ] 5.4.4 Add form validation with inline error messages

- [ ] 5.5 Docker Compose Production Config
  - [ ] 5.5.1 Create multi-stage Dockerfile for backend
  - [ ] 5.5.2 Create Nginx config + frontend Dockerfile
  - [ ] 5.5.3 Create docker-compose.yml (production) with health checks
