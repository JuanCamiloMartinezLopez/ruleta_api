from fastapi import APIRouter

from app.api.routes import usuario,ruleta,apuesta,juego

api_router= APIRouter()

#api_router.include_router(root.router)
api_router.include_router(usuario.router)
api_router.include_router(ruleta.router)
api_router.include_router(apuesta.router)
api_router.include_router(juego.router)

