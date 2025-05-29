# backend/run.py

import os
import sys

# 1) Add backend/ (where run.py and main.py live) to the path
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    import uvicorn

    # 2) Point at main.py instead of app/main.py
    uvicorn.run(
        "main:app",       # ← note: "main", not "app.main"
        host="127.0.0.1",
        port=8000,
        reload=True,      # you can re-enable reload now
        reload_dirs=["."],# watch the current dir (backend/)
    )
