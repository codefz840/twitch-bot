from enum import IntFlag

from sqlmodel import SQLModel, Field


class TwitchRole(IntFlag):
    NONE = 0
    USER = 1 << 0
    SUB1 = 1 << 1
    SUB2 = 1 << 2
    SUB3 = 1 << 3
    VIP = 1 << 4
    ARTIST = 1 << 5
    MOD = 1 << 6
    ADMIN = 1 << 7
    MANAGER = 1 << 8
    BROADCASTER = 1 << 9


class Token(SQLModel, table=True):
    user_id: str | None = Field(default=None, primary_key=True)
    token: str
    refresh: str


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str


class CustomCommand(SQLModel, table=True):
    channel: str = Field(primary_key=True)
    name: str = Field(primary_key=True)
    response: str