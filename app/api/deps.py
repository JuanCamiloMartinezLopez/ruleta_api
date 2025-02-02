from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, create_engine
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, '..', 'db', 'ruleta_api.db')}"
engine = create_engine(DATABASE_URL, echo=True)
# with engine.connect() as connection:
#         register = connection.execute("select * from usuario")
#         print(register.fetchall())

def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_db)]

