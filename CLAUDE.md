# Climbing Video Analysis Agent

攀岩视频分析、指导、纠正智能体系统。

## Architecture

- **Backend**: Python FastAPI (`backend/`)
- **Frontend**: Next.js + Tailwind CSS (`frontend/`)
- **ML Pipeline**: MediaPipe pose → YOLOv8 holds → 3D reconstruction → movement classification → feedback

## Key Commands

```bash
# Backend
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run dev

# FFmpeg required for video decoding
```

## Conventions

- All user-facing strings in Chinese (中文)
- Backend uses async-first FastAPI with SQLAlchemy ORM
- ML components use abstract base classes for swappable implementations
- Frontend uses App Router with TanStack Query for server state
