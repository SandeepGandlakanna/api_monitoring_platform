import time

import httpx
from sqlmodel import Session, select

from backend.database import engine
from backend.models import Alert, CheckResult, Monitor


def check_monitor(monitor: Monitor) -> CheckResult:

    start_time = time.perf_counter()

    try:

        with httpx.Client(timeout=10.0) as client:

            response = client.request(
                method=monitor.method,
                url=monitor.url,
            )

        end_time = time.perf_counter()

        response_time_ms = (
            end_time - start_time
        ) * 1000

        is_success = (
            200 <= response.status_code < 400
        )

        result = CheckResult(
            monitor_id=monitor.id,
            status_code=response.status_code,
            response_time_ms=response_time_ms,
            is_success=is_success,
            error_message=None,
        )

    except Exception as error:

        end_time = time.perf_counter()

        response_time_ms = (
            end_time - start_time
        ) * 1000

        result = CheckResult(
            monitor_id=monitor.id,
            status_code=None,
            response_time_ms=response_time_ms,
            is_success=False,
            error_message=str(error),
        )

    with Session(engine) as session:

        session.add(result)

        monitor_db = session.get(
            Monitor,
            monitor.id,
        )

        if monitor_db:

            monitor_db.last_checked_at = (
                result.checked_at
            )

            monitor_db.last_status_code = (
                result.status_code
            )

            monitor_db.last_response_time_ms = (
                result.response_time_ms
            )

            monitor_db.last_is_success = (
                result.is_success
            )

        # --------------------------------
        # SUCCESS → RESOLVE EXISTING ALERT
        # --------------------------------

        if result.is_success:

            existing_alert = session.exec(
                select(Alert)
                .where(
                    Alert.monitor_id == monitor.id
                )
                .where(
                    Alert.is_resolved == False
                )
            ).first()

            if existing_alert:

                existing_alert.is_resolved = True

                existing_alert.resolved_at = (
                    result.checked_at
                )

        if not result.is_success:

            existing_alert = session.exec(
                select(Alert)
                .where(
                    Alert.monitor_id == monitor.id
                )
                .where(
                    Alert.is_resolved == False
                )
            ).first()

            # Only create a new alert if
            # there is no unresolved alert.

            if not existing_alert:

                if result.status_code is not None:

                    message = (
                        f"Monitor '{monitor.name}' "
                        f"failed with status code "
                        f"{result.status_code}."
                    )

                else:

                    message = (
                        f"Monitor '{monitor.name}' "
                        f"failed to respond."
                    )

                alert = Alert(
                    monitor_id=monitor.id,
                    message=message,
                    alert_type="failure",
                    is_resolved=False,
                )

                session.add(alert)

        session.commit()

        session.refresh(result)

        return result