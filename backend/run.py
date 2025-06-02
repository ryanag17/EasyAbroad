import os, sys

# Add backend/ to sys.path so that `uvicorn app.main:app` works
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",  # points to backend/app/main.py
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["."],  # watch the current directory for changes
    )
