import logging

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.access import can_read
from app.auth import get_current_user
from app.db import get_db
from app.logging_config import setup_logging
from app.models import Resource, User
from app.schemas import (
    ErrorOut,
    LoginIn,
    MeOut,
    MessageOut,
    RegisterIn,
    ResourceItem,
    ResourceOut,
    TokenOut,
)
from app.security import DUMMY_HASH, create_access_token, hash_password, verify_password

setup_logging()
log = logging.getLogger("app")

app = FastAPI(title="pasz-lab4")

AUTH_RESPONSES = {401: {"model": ErrorOut, "description": "нет входа или токен недействителен"}}


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    fields = []
    messages = []
    for err in exc.errors():
        field = str(err["loc"][-1])
        fields.append(field)
        if err["type"] == "missing":
            messages.append(f"поле {field} обязательно")
        else:
            messages.append(err["msg"].removeprefix("Value error, "))
    log.error(
        "validation failed",
        extra={"ctx": {"event": "validation_error", "path": request.url.path, "fields": fields}},
    )
    return JSONResponse(status_code=422, content={"detail": "; ".join(messages)})


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post(
    "/api/register",
    status_code=201,
    response_model=MessageOut,
    responses={
        409: {"model": ErrorOut, "description": "логин уже занят"},
        422: {"model": ErrorOut, "description": "ошибка валидации"},
    },
)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    user = User(login=data.login, password_hash=hash_password(data.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        log.error(
            "login already taken",
            extra={"ctx": {"event": "register_duplicate", "login": data.login}},
        )
        raise HTTPException(status_code=409, detail="логин уже занят")
    log.info(
        "user registered",
        extra={"ctx": {"event": "register_success", "login": data.login, "user_id": user.id}},
    )
    return {"message": "user создан"}


@app.post(
    "/api/login",
    response_model=TokenOut,
    responses={401: {"model": ErrorOut, "description": "неверный логин или пароль"}},
)
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.login == data.login))
    ok = verify_password(data.password, user.password_hash if user else DUMMY_HASH)
    if user is None or not ok:
        log.error("login failed", extra={"ctx": {"event": "login_failed", "login": data.login}})
        raise HTTPException(status_code=401, detail="неверный логин или пароль")
    log.info("login ok", extra={"ctx": {"event": "login_success", "login": user.login}})
    return {"access_token": create_access_token(user.id), "token_type": "bearer"}


@app.get("/api/me", response_model=MeOut, responses=AUTH_RESPONSES)
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "login": user.login, "clearance": user.clearance}


@app.get("/api/resources", response_model=list[ResourceItem], responses=AUTH_RESPONSES)
def list_resources(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(Resource).order_by(Resource.id)).all()
    return [
        {
            "id": r.id,
            "title": r.title,
            "classification": r.classification,
            "allowed": can_read(user.clearance, r.classification),
        }
        for r in rows
    ]


@app.get(
    "/api/resources/{resource_id}",
    response_model=ResourceOut,
    responses={
        **AUTH_RESPONSES,
        403: {"model": ErrorOut, "description": "недостаточный уровень допуска"},
        404: {"model": ErrorOut, "description": "ресурс не найден"},
    },
)
def get_resource(
    resource_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resource = db.get(Resource, resource_id)
    if resource is None:
        raise HTTPException(status_code=404, detail="ресурс не найден")
    ctx = {
        "login": user.login,
        "clearance": user.clearance,
        "resource_id": resource.id,
        "classification": resource.classification,
    }
    if not can_read(user.clearance, resource.classification):
        log.error("access denied", extra={"ctx": {"event": "access_denied", **ctx}})
        raise HTTPException(status_code=403, detail="недостаточный уровень допуска")
    log.info("access granted", extra={"ctx": {"event": "access_granted", **ctx}})
    return {
        "id": resource.id,
        "title": resource.title,
        "classification": resource.classification,
        "content": resource.content,
    }
