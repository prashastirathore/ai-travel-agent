from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.travel import router as travel_router


app = FastAPI(
    title="AI Travel Agent",
    version="4.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://ai-travel-agent-theta-sable.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(travel_router)


@app.get("/")
def home():

    return {
        "success": True,
        "message": "AI Travel Agent is running",
        "version": "4.0.0"
    }