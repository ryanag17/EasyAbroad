# backend/Dockerfile

FROM python:3.11-slim

# 1) Set working directory
WORKDIR /app

# 2) Copy requirements and install
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 3) Copy the rest of the backend code
COPY . .

# 4) Expose the API port
EXPOSE 8000

# 5) Command to run the API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
