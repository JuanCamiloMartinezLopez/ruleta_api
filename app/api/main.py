from fastapi import APIRouter

from api.routes import root

api_router= APIRouter()

api_router.include_router(root.router)