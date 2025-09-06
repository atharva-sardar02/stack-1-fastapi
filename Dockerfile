# 1) Start from a small Python image
FROM python:3.12-slim

# 2) Make Python friendlier in containers
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1

# 3) Set working directory *inside* the image
WORKDIR /app

# 4) Install dependencies first (better build caching)
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# 5) Copy your application code
COPY app /app/app

# 6) Expose the port uvicorn will listen on
EXPOSE 8000

# 7) Command to run your server when the container starts
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]