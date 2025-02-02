from typing import Any, List

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select

from app.api.deps import SessionDep
from app.models import Apuesta as ApuestaModel

router = APIRouter(prefix="/apuesta")

@router.get("/", response_model=List[ApuestaModel])
def get(session: SessionDep, limit: int = 100) -> Any:
    statement = select(ApuestaModel).limit(limit)
    apuestas = session.exec(statement).all()

    return apuestas

@router.get("/{id}", response_model=ApuestaModel)
def get_one(id:int,session: SessionDep) -> Any:
    
    apuesta = session.get(ApuestaModel, id)
    if not apuesta:
        raise HTTPException(status_code=404,detail="Apuesta no encontrada")
    return apuesta

@router.post("/",response_model=ApuestaModel)
def post(Apuesta:ApuestaModel,session:SessionDep) -> Any:
    try:
        session.add(Apuesta)
        session.commit()
        session.refresh(Apuesta)
        return Apuesta
    except SQLAlchemyError:
        session.rollback()
        raise HTTPException(status_code=500, detail="Error al realizar la apuesta")

@router.put("/{id}",response_model=ApuestaModel)
def put(id:int,Apuesta:ApuestaModel,session:SessionDep) -> Any:
    apuesta = session.get(ApuestaModel, id)
    if not apuesta:
        raise HTTPException(status_code=404,detail="Ruleta no encontrada")
    update_dict = Apuesta.model_dump(exclude_unset=True)
    apuesta.sqlmodel_update(update_dict)
    session.add(apuesta)
    session.commit()
    session.refresh(apuesta)
    return apuesta  

@router.delete("/{id}")
def delete(id:int,session:SessionDep) -> Any:
    apuesta = session.get(ApuestaModel, id)
    if not apuesta:
        raise HTTPException(status_code=404,detail="Apuesta no encontrada")
    session.delete(apuesta)
    session.commit()
    return {"message":"Apuesta eliminada"}