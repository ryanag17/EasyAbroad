# File: backend/run.py

import os
import sys

# 1) Ensure the 'app' package is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

if __name__ == "__main__":
    import uvicorn

    # 2) Tell Uvicorn where your FastAPI instance lives:
    #    "<module path>:<variable name>"
    #     - module path "app.main" points at backend/app/main.py
    #     - variable "app" is the FastAPI() instance inside that file
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,            # <-- requires import string above
        reload_dirs=["app"],    # watch your app/ folder for changes
    )
