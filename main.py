from fastapi import FastAPI
# Assuming your audio upload file is named 'upload.py' and defines 'router'
from upload import router # <-- Correctly import the APIRouter instance

app = FastAPI()

# Include the router, optionally adding a prefix for API endpoints
app.include_router(router, prefix="/api/v1", tags=["Audio Upload Test"]) 

# Example root endpoint to verify the app is running
@app.get("/")
def read_root():
    return {"status": "Application is running", "endpoint_available": "/api/v1/upload-test"}
