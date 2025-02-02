from typing import Any, List

from fastapi import APIRouter, HTTPException
from sqlmodel import select
from sqlalchemy.exc import SQLAlchemyError

from app.api.deps import SessionDep
from app.models import Ruleta as RuletaModel

router = APIRouter(prefix="/ruleta")

@router.get("/", response_model=List[RuletaModel])
def get(session: SessionDep, limit: int = 100) -> Any:
    statement = select(RuletaModel).limit(limit)
    ruletas = session.exec(statement).all()
    return ruletas

@router.get("/{id}", response_model=RuletaModel)
def get_one(id:int,session: SessionDep) -> Any:
    
    ruleta = session.get(RuletaModel, id)
    if not ruleta:
        raise HTTPException(status_code=404,detail="Ruleta no encontrada")
    return ruleta

@router.post("/",response_model=RuletaModel)
def post(Ruleta:RuletaModel,session:SessionDep) -> Any:
    try:
        session.add(Ruleta)
        session.commit()
        session.refresh(Ruleta)
        return Ruleta
    except SQLAlchemyError as e:
        session.rollback()
        print(e)
        raise HTTPException(status_code=500, detail="Error crear la ruleta")

@router.put("/{id}",response_model=RuletaModel)
def put(id:int,Ruleta:RuletaModel,session:SessionDep) -> Any:
    ruleta = session.get(RuletaModel, id)
    if not ruleta:
        raise HTTPException(status_code=404,detail="Ruleta no encontrada")
    update_dict = Ruleta.model_dump(exclude_unset=True)
    ruleta.sqlmodel_update(update_dict)
    session.add(ruleta)
    session.commit()
    session.refresh(ruleta)
    return ruleta  

@router.delete("/{id}")
def delete(id:int,session:SessionDep) -> Any:
    ruleta = session.get(RuletaModel, id)
    if not ruleta:
        raise HTTPException(status_code=404,detail="Ruleta no encontrada")
    session.delete(ruleta)
    session.commit()
    return {"message":"Ruleta eliminada"}