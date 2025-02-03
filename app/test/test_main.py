import random
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete
from app.main import app
from app.api.deps import get_db
from app.api.deps import engine
from app.models import Apuesta, Ruleta



# Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="module")
def client():
    def override_get_db():
        try:
            db = Session(engine)
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="session",autouse=True)
def clean_tables():
    db = Session(engine)
    try:
        db.exec(delete(Apuesta))
        db.exec(delete(Ruleta))
        db.commit()
    finally:
        db.close()

def test_create_ruleta(client):
    response = client.get("/juego/crear_ruleta")
    assert response.status_code == 201

def test_open_ruleta(client):
    # Primero, crea una ruleta
    response = client.get("/juego/crear_ruleta")
    assert response.status_code == 201

    print(response.json())
    # Obtén el ID de la ruleta creada
    ruleta_id = response.json()["detail"]["id"]

    # Abre la ruleta
    response = client.get(f"/juego/abrir_ruleta/{ruleta_id}")
    assert response.status_code == 200

def test_create_apuesta(client):
    # Primero, crea una ruleta
    response = client.get("/juego/crear_ruleta")
    assert response.status_code == 201

    # Obtén el ID de la ruleta creada
    ruleta_id = response.json()["detail"]["id"]
    print(ruleta_id)

    # Abre la ruleta
    response = client.get(f"/juego/abrir_ruleta/{ruleta_id}")
    assert response.status_code == 200

    # Crea una apuesta
    apuesta_data = {
        "ruleta_id": ruleta_id,
        "tipo_apuesta": "numero",
        "numero_apostado": 17,
        "color_apostado": "rojo",
        "monto": 100.0
    }
    headers = {"usuario_id": "1"}
    response = client.post("/juego/crear_apuesta", json=apuesta_data, headers=headers)
    print(response.json())
    assert response.status_code == 201

def test_close_ruleta(client):
    # Primero, crea una ruleta
    response = client.get("/juego/crear_ruleta")
    assert response.status_code == 201

    # Obtén el ID de la ruleta creada
    ruleta_id = response.json()["detail"]["id"]

    # Abre la ruleta
    response = client.get(f"/juego/abrir_ruleta/{ruleta_id}")
    assert response.status_code == 200

    # Crear múltiples apuestas con valores aleatorios para los usuarios del 1 al 10
    for user_id in range(1, 11):
        apuesta_data = {
            "ruleta_id": ruleta_id,
            "tipo_apuesta": random.choice(["numero", "color"]),
            "numero_apostado": random.randint(0, 36) ,
            "color_apostado": random.choice(["rojo", "negro"]),
            "monto": random.uniform(1.0, 10000.0)
        }
        headers = {"usuario_id": str(user_id)}
        print(headers,apuesta_data)
        response = client.post("/juego/crear_apuesta", json=apuesta_data, headers=headers)
        print("response crear apuesta",response)
        assert response.status_code == 201


    # Cerrar la ruleta
    response = client.get(f"/juego/cerrar_ruleta/{ruleta_id}")
    print("response",response)
    assert response.status_code == 200
    assert response.json()["ruleta"]["estado"] == "cerrada"

    # Validar que las apuestas están correctas
    for apuesta in response.json()["apuestas"]:
        print("apuesta",apuesta)
        if apuesta["estado"]=="perdida":
            if apuesta["tipo_apuesta"]=="numero":
                assert response.json()["ruleta"]["numero_ganador"] != apuesta["numero_apostado"]
            else:
                assert response.json()["ruleta"]["color_ganador"] != apuesta["color_apostado"]
        else:
            if apuesta["tipo_apuesta"]=="numero":
                assert response.json()["ruleta"]["numero_ganador"] == apuesta["numero_apostado"]
                assert apuesta["monto"] == (apuesta["ganancia"]*5)
            else:
                assert response.json()["ruleta"]["color_ganador"] == apuesta["color_apostado"]
                assert apuesta["monto"] == (apuesta["ganancia"]*1.8)

