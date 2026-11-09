import re
import string

from pydantic import BaseModel, field_validator

LOGIN_RE = re.compile(r"[A-Za-z0-9._-]{3,32}")


class RegisterIn(BaseModel):
    login: str
    password: str

    @field_validator("login")
    @classmethod
    def check_login(cls, v: str) -> str:
        if not LOGIN_RE.fullmatch(v):
            raise ValueError(
                "логин: от 3 до 32 символов, только латинские буквы, цифры, точка, _ и -"
            )
        return v

    @field_validator("password")
    @classmethod
    def check_password(cls, v: str) -> str:
        problems = []
        if len(v) < 8:
            problems.append("минимум 8 символов")
        if len(v) > 128:
            problems.append("не больше 128 символов")
        if not re.search(r"[A-Z]", v):
            problems.append("нужна заглавная латинская буква")
        if not re.search(r"[a-z]", v):
            problems.append("нужна строчная латинская буква")
        if not re.search(r"[0-9]", v):
            problems.append("нужна цифра")
        if not any(c in string.punctuation for c in v):
            problems.append("нужен спецсимвол")
        if problems:
            raise ValueError("пароль: " + ", ".join(problems))
        return v


class MessageOut(BaseModel):
    message: str


class ErrorOut(BaseModel):
    detail: str
