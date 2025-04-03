# api/app.py
from mainv52 import app  # Import your FastAPI app from mainv52.py
import os

# Vercel expects an object named 'app'
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
