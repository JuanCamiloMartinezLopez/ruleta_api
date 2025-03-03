from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router


app = FastAPI(title="ruleta API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)