from sqlmodel import Session, select

from backend.database import engine
from backend.models import CheckResult


def calculate_monitor_stats(monitor_id: int):

    with Session(engine) as session:

        results = session.exec(
            select(CheckResult)
            .where(
                CheckResult.monitor_id == monitor_id
            )
        ).all()

    total_checks = len(results)

    if total_checks == 0:
        return {
            "total_checks": 0,
            "successful_checks": 0,
            "failed_checks": 0,
            "uptime_percentage": 0,
            "average_response_time_ms": 0,
            "minimum_response_time_ms": 0,
            "maximum_response_time_ms": 0,
        }

    successful_checks = sum(
        1
        for result in results
        if result.is_success
    )

    failed_checks = (
        total_checks - successful_checks
    )

    uptime_percentage = (
        successful_checks / total_checks
    ) * 100

    response_times = [
        result.response_time_ms
        for result in results
        if result.response_time_ms is not None
    ]

    average_response_time = (
        sum(response_times) / len(response_times)
        if response_times
        else 0
    )

    minimum_response_time = (
        min(response_times)
        if response_times
        else 0
    )

    maximum_response_time = (
        max(response_times)
        if response_times
        else 0
    )

    return {
        "total_checks": total_checks,
        "successful_checks": successful_checks,
        "failed_checks": failed_checks,
        "uptime_percentage": round(
            uptime_percentage, 2
        ),
        "average_response_time_ms": round(
            average_response_time, 2
        ),
        "minimum_response_time_ms": round(
            minimum_response_time, 2
        ),
        "maximum_response_time_ms": round(
            maximum_response_time, 2
        ),
    }