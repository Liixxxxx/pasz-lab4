import logging

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.logging_config import setup_logging
from app.models import User
from app.schemas import ErrorOut, MessageOut, RegisterIn
from app.security import hash_password

setup_logging()
log = logging.getLogger("app")

app = FastAPI(title="pasz-lab4")


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
