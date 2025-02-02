from typing import Any,List

from fastapi import APIRouter, HTTPException
from sqlmodel import select
from sqlalchemy.exc import SQLAlchemyError

from app.api.deps import SessionDep
from app.models import Usuario as UsuarioModel

router = APIRouter(prefix="/usuario")

@router.get("/", response_model=List[UsuarioModel])
def get(session: SessionDep, limit: int = 100) -> Any:
    statement = select(UsuarioModel).limit(limit)
    usuarios = session.exec(statement).all()
    return usuarios

@router.get("/{id}", response_model=UsuarioModel)
def get_one(id:int,session: SessionDep) -> Any:
    
    usuario = session.get(UsuarioModel, id)
    if not usuario:
        raise HTTPException(status_code=404,detail="Usuario no encontrado")
    return usuario

@router.post("/")
def post(session:SessionDep) -> Any:
    try:
        usuario= UsuarioModel()
        session.add(usuario)
        session.commit()
        raise HTTPException(status_code=201,detail="Usuario creado")
    except SQLAlchemyError:
        session.rollback()
        raise HTTPException(status_code=500, detail="Error al realizar la apuesta")

@router.put("/{id}",response_model=UsuarioModel)
def put(id:int,Usuario:UsuarioModel,session:SessionDep) -> Any:
    usuario = session.get(UsuarioModel, id)
    if not usuario:
        raise HTTPException(status_code=404,detail="Ruleta no encontrada")
    update_dict = Usuario.model_dump(exclude_unset=True)
    usuario.sqlmodel_update(update_dict)
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario  

@router.delete("/{id}")
def delete(id:int,session:SessionDep) -> Any:
    usuario = session.get(UsuarioModel, id)
    if not usuario:
        raise HTTPException(status_code=404,detail="Usuario no encontrado")
    session.delete(usuario)
    session.commit()
    return {"message":"Usuario eliminado"}
