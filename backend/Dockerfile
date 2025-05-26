FROM python:3

WORKDIR /app

# 1) Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Application code
COPY app ./app

# 3) Static assets
COPY static ./static

# 4) Run the server
CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8000","--reload"]
