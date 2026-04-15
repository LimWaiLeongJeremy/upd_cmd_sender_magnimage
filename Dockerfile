# ─────────────────────────────────────────────────────────────
# Stage 1 — Build React
# Uses Node to compile src/ into static HTML/CSS/JS files.
# This stage is discarded after the build — it never ends up
# in your final image, keeping the image lean.
# ─────────────────────────────────────────────────────────────

FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# install dependencies first (separate layer so it's cached
# if pacakage.json hasn't changed - save time in rebuild)
COPY frontend/ ./ 
RUN npm run build
# Output is now in /app/frontend/dist

# ─────────────────────────────────────────────────────────────
# Stage 2 — Python runtime
# Only this stage ends up in your final image.
# ─────────────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY requirments.txt ./ 
RUN pip install --no-cache-dir -r requirments.txt

# Copy the entire Python project 
COPY api/ ./api/
COPY config/ ./config/
COPY services/ ./services/
COPY utils/ ./utils/
COPY constants.py ./

# Copy the entire build React files from stage 1 
# They end up at /app/frontend/dist - FastAPI serves them from here
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

EXPOSE 8000

# Start server 
# --host 0.0.0.0 is critical - without it server only listen 
# on localhost inside the container and is not reachable from outside 
CMD ["unicorn", "api.app:app", "--host"< "0.0.0.0", "--port", "8000"]