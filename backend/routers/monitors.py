from fastapi import APIRouter, HTTPException,Depends
from sqlmodel import Session, select,SQLModel,Field
from backend.database import engine
from backend.models import Monitor,CheckResult,User,Alert
from backend.services.monitor_service import check_monitor
from backend.dependencies import get_current_username
from backend.services.analytics_service import calculate_monitor_stats
from typing import Literal
from pydantic import HttpUrl

router = APIRouter(prefix="/monitors",tags=["Monitors"],)

class MonitorCreate(SQLModel):
    name: str = Field(min_length=1, max_length=100)
    url: HttpUrl
    method: Literal["GET","POST","PUT","DELETE"]="GET"
    check_interval_seconds: int = Field(default=60,ge=10)

class MonitorUpdate(SQLModel):
    name: str |None= Field( default=None ,min_length=1,max_length=100)
    url: HttpUrl | None = None
    method: Literal[  "GET",  "POST", "PUT", "DELETE"]| None = None
    check_interval_seconds: int | None = Field(default=None,ge=10)
    is_active: bool | None = None
    

def get_user_monitor(
    session: Session,
    monitor_id: int,
    username: str,
):
    user = session.exec(
        select(User).where(
            User.username == username
        )
    ).first()

    if not user:
        return None

    monitor = session.get(
        Monitor,
        monitor_id,
    )

    if not monitor:
        return None

    if monitor.user_id != user.id:
        return None

    return monitor


@router.post("/", response_model=Monitor)
def create_monitor(
    monitor_data: MonitorCreate,
    username: str = Depends(get_current_username),):
    with Session(engine) as session:
        user = session.exec(select(User).where( User.username == username) ).first()
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )

        monitor = Monitor(
            user_id=user.id,
            name=monitor_data.name,
            url=str(monitor_data.url),
            method=monitor_data.method,
            check_interval_seconds=monitor_data.check_interval_seconds,
        )

        session.add(monitor)
        session.commit()
        session.refresh(monitor)

        return monitor


@router.get("/", response_model=list[Monitor])
def get_monitors(
    username: str = Depends(
        get_current_username
    ),
):
    with Session(engine) as session:

        user = session.exec(
            select(User).where(
                User.username == username
            )
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )

        monitors = session.exec(
            select(Monitor).where(
                Monitor.user_id == user.id
            )
        ).all()

        return monitors
@router.get("/alerts")
def get_alerts(
    username: str = Depends(
        get_current_username
    ),
):
    with Session(engine) as session:

        user = session.exec(
            select(User).where(
                User.username == username
            )
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )

        monitors = session.exec(
            select(Monitor).where(
                Monitor.user_id == user.id
            )
        ).all()

        monitor_ids = [
            monitor.id
            for monitor in monitors
        ]

        if not monitor_ids:
            return []

        alerts = session.exec(
            select(Alert)
            .where(
                Alert.monitor_id.in_(monitor_ids)
            )
            .order_by(
                Alert.created_at.desc()
            )
        ).all()

        return alerts

@router.get("/{monitor_id}", response_model=Monitor)
def get_monitor(
    monitor_id: int,
    username: str = Depends(
        get_current_username
    ),
):
    with Session(engine) as session:

        monitor = get_user_monitor(
            session,
            monitor_id,
            username,
        )

        if not monitor:
            raise HTTPException(
                status_code=404,
                detail="Monitor not found",
            )

        return monitor

@router.put("/{monitor_id}", response_model=Monitor)
def update_monitor(
    monitor_id: int,
    monitor_data: MonitorUpdate,
    username: str = Depends(
        get_current_username
    ),
):
    with Session(engine) as session:

        monitor = get_user_monitor(
            session,
            monitor_id,
            username,
        )

        if not monitor:
            raise HTTPException(
                status_code=404,
                detail="Monitor not found",
            )

        update_data = monitor_data.model_dump(
            exclude_unset=True
        )
        
        for key, value in update_data.items():
        
            if key == "url" and value is not None:
                value = str(value)
        
            setattr(monitor, key, value)

        session.add(monitor)
        session.commit()
        session.refresh(monitor)

        return monitor

@router.delete("/{monitor_id}")
def delete_monitor(
    monitor_id: int,
    username: str = Depends(
        get_current_username
    ),
):
    with Session(engine) as session:

        monitor = get_user_monitor(
            session,
            monitor_id,
            username,
        )

        if not monitor:
            raise HTTPException(
                status_code=404,
                detail="Monitor not found",
            )

        session.delete(monitor)
        session.commit()

        return {
            "message": "Monitor deleted successfully"
        }

@router.post("/{monitor_id}/check")
def run_monitor_check(
    monitor_id: int,
    username: str = Depends(
        get_current_username
    ),
):
    with Session(engine) as session:

        monitor = get_user_monitor(
            session,
            monitor_id,
            username,
        )

        if not monitor:
            raise HTTPException(
                status_code=404,
                detail="Monitor not found",
            )

    result = check_monitor(monitor)

    return result
@router.get("/{monitor_id}/results")
def get_monitor_results(
    monitor_id: int,
    username: str = Depends(
        get_current_username
    ),
):
    with Session(engine) as session:

        monitor = get_user_monitor(
            session,
            monitor_id,
            username,
        )

        if not monitor:
            raise HTTPException(
                status_code=404,
                detail="Monitor not found",
            )

        results = session.exec(
            select(CheckResult)
            .where(
                CheckResult.monitor_id == monitor_id
            )
            .order_by(
                CheckResult.checked_at.desc()
            )
        ).all()

        return results

@router.get("/{monitor_id}/stats")
def get_monitor_stats(
    monitor_id: int,
    username: str = Depends(
        get_current_username
    ),
):
    with Session(engine) as session:

        monitor = get_user_monitor(
            session,
            monitor_id,
            username,
        )

        if not monitor:
            raise HTTPException(
                status_code=404,
                detail="Monitor not found",
            )

    stats = calculate_monitor_stats(
        monitor_id
    )

    return {
        "monitor_id": monitor_id,
        **stats,
    }

@router.get("/dashboard/summary")
def get_dashboard_summary(
    current_username: str = Depends(
        get_current_username
    ),
):
    with Session(engine) as session:

        user = session.exec(
            select(User).where(
                User.username == current_username
            )
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )

        monitors = session.exec(
            select(Monitor).where(
                Monitor.user_id == user.id
            )
        ).all()

    total_monitors = len(monitors)

    active_monitors = sum(
        1
        for monitor in monitors
        if monitor.is_active
    )

    healthy_monitors = sum(
        1
        for monitor in monitors
        if monitor.last_is_success is True
    )

    failing_monitors = sum(
        1
        for monitor in monitors
        if monitor.last_is_success is False
    )

    return {
        "total_monitors": total_monitors,
        "active_monitors": active_monitors,
        "healthy_monitors": healthy_monitors,
        "failing_monitors": failing_monitors,
    }


@router.get("/{monitor_id}/status")
def get_monitor_status(
    monitor_id: int,
    username: str = Depends(
        get_current_username
    ),
):
    with Session(engine) as session:

        monitor = get_user_monitor(
            session,
            monitor_id,
            username,
        )

        if not monitor:
            raise HTTPException(
                status_code=404,
                detail="Monitor not found",
            )

        if monitor.last_is_success is True:
            status = "healthy"

        elif monitor.last_is_success is False:
            status = "failing"

        else:
            status = "not_checked"

        return {
            "monitor_id": monitor.id,
            "name": monitor.name,
            "url": monitor.url,
            "status": status,
            "status_code": monitor.last_status_code,
            "response_time_ms": monitor.last_response_time_ms,
            "last_checked_at": monitor.last_checked_at,
            "is_active": monitor.is_active,
        }

@router.get("/{monitor_id}/history")
def get_monitor_history(
    monitor_id: int,
    username: str = Depends(
        get_current_username
    ),
):
    with Session(engine) as session:

        monitor = get_user_monitor(
            session,
            monitor_id,
            username,
        )

        if not monitor:
            raise HTTPException(
                status_code=404,
                detail="Monitor not found",
            )

        results = session.exec(
            select(CheckResult)
            .where(
                CheckResult.monitor_id == monitor_id
            )
            .order_by(
                CheckResult.checked_at.asc()
            )
        ).all()

        return [
            {
                "checked_at": result.checked_at,
                "response_time_ms": result.response_time_ms,
                "status_code": result.status_code,
                "is_success": result.is_success,
            }
            for result in results
        ]