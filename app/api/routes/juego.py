from random import randrange
from fastapi import APIRouter, HTTPException, Header
from typing import Union
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select

from app.api.deps import SessionDep
from app.models import Ruleta as RuletaModel,Apuesta as ApuestaModel, Usuario as UsuarioModel, EstadoRuleta, CrearApuesta, TipoApuesta, EstadoApuesta, ColorApuesta

router=APIRouter(prefix="/juego")


@router.get("/crear_ruleta")
def create_ruleta(session:SessionDep):
    try:
        ruleta = RuletaModel()
        session.add(ruleta)
        session.commit()
        session.refresh(ruleta)
        raise HTTPException(status_code=201, detail={"message": "Ruleta creada", "id": ruleta.id})
    except SQLAlchemyError as e:
        session.rollback()
        print(e)
        raise HTTPException(status_code=500, detail="Error crear la ruleta")

@router.get("/abrir_ruleta/{id}")
def open_ruleta(id:int,session:SessionDep):
    ruleta = session.get(RuletaModel, id)
    if not ruleta:
        raise HTTPException(status_code=404,detail="Ruleta no encontrada")
    if ruleta.estado!=EstadoRuleta.INICIAL:
        raise HTTPException(status_code=409, detail="La ruleta ya fue abierta o cerrada")
    ruleta.estado=EstadoRuleta.ABIERTA
    session.add(ruleta)
    session.commit()
    session.refresh(ruleta)
    raise HTTPException(status_code=200,detail={"message":"Ruleta abierta", "id": ruleta.id})

@router.post("/crear_apuesta")
def create_apuesta(apuesta_body:CrearApuesta,session:SessionDep,usuario_id: Union[int, None] = Header(default=None, convert_underscores=False)):
    try:
        if apuesta_body.monto>10000:
            raise HTTPException(status_code=400, detail="Monto maximo 10000")
        if apuesta_body.tipo_apuesta==TipoApuesta.NUMERO:
            if (apuesta_body.numero_apostado >=36 or apuesta_body.numero_apostado <0):
                raise HTTPException(status_code=400, detail="Numero no valido.")
        ruleta=session.get(RuletaModel,apuesta_body.ruleta_id)
        if ruleta is None or ruleta.estado!=EstadoRuleta.ABIERTA:
            raise HTTPException(status_code=409, detail="La ruleta no esta abierta o no existe")
        if session.get(UsuarioModel,usuario_id) is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        apuesta = ApuestaModel(usuario_id=usuario_id,ruleta_id=apuesta_body.ruleta_id,tipo_apuesta=apuesta_body.tipo_apuesta,numero_apostado=apuesta_body.numero_apostado,color_apostado=apuesta_body.color_apostado,monto=apuesta_body.monto)
        session.add(apuesta)
        session.commit()
        session.refresh(apuesta)
        raise HTTPException(status_code=201,detail="Apuesta realizada")
    except SQLAlchemyError as e:
        session.rollback()
        print(e)
        raise HTTPException(status_code=500, detail="Error al realizar la apuesta")

@router.get("/cerrar_ruleta/{id}")
def close_ruleta(id:int,session:SessionDep):
    try:
        ruleta = session.get(RuletaModel, id)
        print("ruleta",ruleta)
        if not ruleta:
            raise HTTPException(status_code=404,detail="Ruleta no encontrada")
        if ruleta.estado!=EstadoRuleta.ABIERTA:
            raise HTTPException(status_code=409, detail="La ruleta no esta abierta")
        
        resultado_ruleta=randrange(0,37)
        print(resultado_ruleta)
        ruleta.numero_ganador= resultado_ruleta
        ruleta.color_ganador=ColorApuesta.ROJO if resultado_ruleta%2==0 else ColorApuesta.NEGRO

        statement=select(ApuestaModel).where(ApuestaModel.ruleta_id==id)
        print("session",session)
        apuestas=session.exec(statement)
        print("session",session)
        print("apuestas",apuestas)
        for apuesta in apuestas:
            if apuesta.tipo_apuesta==TipoApuesta.NUMERO:
                if apuesta.numero_apostado==ruleta.numero_ganador:
                    apuesta.estado=EstadoApuesta.GANADA
                    apuesta.ganancia=apuesta.monto*5
                else:
                    apuesta.estado=EstadoApuesta.PERDIDA
            elif apuesta.tipo_apuesta==TipoApuesta.COLOR:
                if apuesta.color_apostado==ruleta.color_ganador:
                    apuesta.estado=EstadoApuesta.GANADA
                    apuesta.ganancia=apuesta.monto*1.8
                else:
                    apuesta.estado=EstadoApuesta.PERDIDA
            session.add(apuesta)
        ruleta.estado=EstadoRuleta.CERRADA
        session.add(ruleta)
        apuestas=session.exec(statement)
        print(apuestas)
        session.commit()
        session.refresh(ruleta)
        return {"apuestas":apuestas.all(),"ruleta":ruleta}
    except SQLAlchemyError as e:
        session.rollback()
        print(e)
        raise HTTPException(status_code=500, detail="Error al realizar la apuesta")
