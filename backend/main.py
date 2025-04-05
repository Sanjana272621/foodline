from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine
from routers import users, gatherings, claims

# Create DB tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Food Donation API")

# CORS middleware setup for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)
app.include_router(gatherings.router)
app.include_router(claims.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Food Donation API. Visit /docs for API documentation."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)