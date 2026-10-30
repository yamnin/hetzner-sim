import random
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import Base, engine, get_session
from app.models import IMAGES, LOCATIONS, SERVER_TYPES, Server


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="Hetzner Cloud Simulator", version="0.1.0", lifespan=lifespan)


class ServerCreate(BaseModel):
    name: str = Field(pattern=r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$")
    server_type: str = "cx22"
    location: str = "fsn1"
    image: str = "ubuntu-24.04"


class ServerOut(BaseModel):
    id: int
    name: str
    server_type: str
    location: str
    image: str
    status: str
    ipv4: str
    created: datetime

    model_config = {"from_attributes": True}


class ActionIn(BaseModel):
    action: Literal["poweron", "poweroff", "reboot"]


def _get_or_404(session: Session, server_id: int) -> Server:
    server = session.get(Server, server_id)
    if server is None:
        raise HTTPException(404, "server not found")
    return server


@app.get("/health")
def health(session: Session = Depends(get_session)):
    session.execute(text("SELECT 1"))
    return {"status": "ok", "database": "ok"}


@app.get("/v1/server_types")
def server_types():
    return {"server_types": [{"name": k, **v} for k, v in SERVER_TYPES.items()]}


@app.get("/v1/locations")
def locations():
    return {"locations": LOCATIONS}


@app.get("/v1/servers", response_model=list[ServerOut])
def list_servers(session: Session = Depends(get_session)):
    return session.scalars(select(Server).order_by(Server.id)).all()


@app.post("/v1/servers", response_model=ServerOut, status_code=201)
def create_server(body: ServerCreate, session: Session = Depends(get_session)):
    if body.server_type not in SERVER_TYPES:
        raise HTTPException(422, f"unknown server_type '{body.server_type}'")
    if body.location not in LOCATIONS:
        raise HTTPException(422, f"unknown location '{body.location}'")
    if body.image not in IMAGES:
        raise HTTPException(422, f"unknown image '{body.image}'")

    server = Server(
        **body.model_dump(),
        ipv4=f"49.12.{random.randint(0, 255)}.{random.randint(1, 254)}",
    )
    session.add(server)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, f"server name '{body.name}' already in use")
    session.refresh(server)
    return server


@app.get("/v1/servers/{server_id}", response_model=ServerOut)
def get_server(server_id: int, session: Session = Depends(get_session)):
    return _get_or_404(session, server_id)


@app.post("/v1/servers/{server_id}/actions", response_model=ServerOut)
def server_action(server_id: int, body: ActionIn, session: Session = Depends(get_session)):
    server = _get_or_404(session, server_id)
    server.status = "off" if body.action == "poweroff" else "running"
    session.commit()
    session.refresh(server)
    return server


@app.delete("/v1/servers/{server_id}", status_code=204)
def delete_server(server_id: int, session: Session = Depends(get_session)):
    session.delete(_get_or_404(session, server_id))
    session.commit()
