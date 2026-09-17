from datetime import datetime
from sqlmodel import SQLModel,Field

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True,unique=True)
    email: str = Field(index=True,unique=True)
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Monitor(SQLModel, table=True):
    id: int | None = Field(default=None,primary_key=True)
    user_id: int | None = Field( default=None, index=True)
    name: str
    url: str
    method: str = "GET"
    check_interval_seconds:int = 60
    is_active: bool = True
    last_checked_at: datetime | None = None
    last_status_code: int | None = None
    last_response_time_ms: float | None = None
    last_is_success: bool | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CheckResult(SQLModel, table=True):
    id: int | None = Field(default=None,primary_key=True)
    monitor_id: int = Field(index=True)
    status_code: int | None = None
    response_time_ms: float | None = None
    is_success: bool
    error_message: str | None = None
    checked_at: datetime = Field(default_factory=datetime.utcnow)

class Alert(SQLModel, table=True):
    id: int | None = Field(
        default=None,
        primary_key=True,
    )
    monitor_id: int = Field(
        index=True,
    )
    message: str
    alert_type: str = "failure"
    is_resolved: bool = False
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
    )
    resolved_at: datetime | None = None